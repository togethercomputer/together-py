"""Main jig CLI commands (deploy, build, push, etc.)."""

from __future__ import annotations

import os
import sys
import json
import time
import shlex
import types
import shutil
import typing
import asyncio
import subprocess
from enum import Enum
from typing import TYPE_CHECKING, Any, Union, Callable
from pathlib import Path
from datetime import datetime
from itertools import groupby
from dataclasses import field, asdict, dataclass, is_dataclass
from urllib.parse import urlparse

import click

from together import Together
from together._exceptions import APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.types.beta.deployment import Deployment, ReplicaEvents
from together.lib.cli.api.beta.jig._uploader import Uploader
from together.types.beta.jig.queue_submit_response import QueueSubmitResponse

if TYPE_CHECKING or sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

# Managed dockerfile marker - if this is the first line, jig will regenerate the file
DOCKERFILE_MANAGED_MARKER = "# MANAGED BY JIG - Remove this line to prevent jig from overwriting this file"


# == Config and state ==
# --- Environment Configuration ---

DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")

# Warmup configuration (for torch compile cache)
WARMUP_ENV_NAME = os.getenv("WARMUP_ENV_NAME", "TORCHINDUCTOR_CACHE_DIR")
WARMUP_DEST = os.getenv("WARMUP_DEST", "torch_cache")


# --- Configuration Dataclasses ---


@dataclass
class ImageConfig:
    """Container image configuration from pyproject.toml"""

    python_version: str = "3.11"
    system_packages: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    run: list[str] = field(default_factory=list)
    cmd: str = "python app.py"
    copy: list[str] = field(default_factory=list)
    auto_include_git: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImageConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class VolumeMount:
    """Volume mount configuration"""

    name: str
    mount_path: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VolumeMount:
        try:
            return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
        except Exception as e:
            raise click.UsageError(f"Invalid volume mount {data}: {e}") from None


@dataclass
class DeployConfig:
    """Deployment configuration"""

    description: str = ""
    gpu_type: str = "h100-80gb"
    gpu_count: int = 1
    cpu: int | float = 1
    memory: int | float = 8
    storage: int = 100
    min_replicas: int = 1
    max_replicas: int = 1
    port: int = 8000
    environment_variables: dict[str, str] = field(default_factory=dict)
    command: list[str] | None = None
    autoscaling: dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    termination_grace_period_seconds: int = 300
    volume_mounts: list[VolumeMount] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeployConfig:
        cfg = {k: v for k, v in data.items() if k in cls.__annotations__}
        if isinstance((mounts := cfg.get("volume_mounts")), list):
            cfg["volume_mounts"] = [VolumeMount.from_dict(vm) for vm in mounts]  # pyright: ignore
        return cls(**cfg)


def validate(value: Any, value_type: type, path: str = "") -> str | None:
    origin = typing.get_origin(value_type)
    args = typing.get_args(value_type)

    if origin is list:
        if not isinstance(value, list):
            return f"{path}: expected list, got {type(value).__name__}"
        for i, v in enumerate(value):  # pyright: ignore
            if err := validate(v, args[0], f"{path}[{i}]"):
                return err
        return None

    if origin is dict:
        if not isinstance(value, dict):
            return f"{path}: expected dict, got {type(value).__name__}"
        for k, v in value.items():  # pyright: ignore
            if err := validate(k, args[0], f"{path}.key({k!r})"):
                return err
            if err := validate(v, args[1], f"{path}[{k!r}]"):
                return err
        return None

    if origin is Union or origin is getattr(types, "UnionType", None):
        if value is None or any(validate(value, a, path) is None for a in args if a is not type(None)):
            return None
        return f"{path}: expected {value_type}, got {type(value).__name__}"

    if is_dataclass(value_type):
        if not isinstance(value, value_type):
            return f"{path}: expected {value_type.__name__}, got {type(value).__name__}"
        for k, t in typing.get_type_hints(value_type, globalns=globals()).items():
            if err := validate(getattr(value, k), t, f"{path}.{k}" if path else k):
                return err
        return None

    if not isinstance(value, value_type):
        return f"{path}: expected {value_type.__name__}, got {value!r}"  # pyright: ignore
    return None


@dataclass
class Config:
    """Main configuration from jig.toml or pyproject.toml"""

    model_name: str = ""
    dockerfile: str = "Dockerfile"
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))
    _unique_name_tip: str = "Update project.name in pyproject.toml"

    def __post_init__(self) -> None:
        if err := validate(self, type(self)):
            raise click.UsageError(f"Invalid {self._path}: {err}")

    @classmethod
    def find(cls, config_path: str | None = None, init: bool = False) -> Config:
        """Find specified config_path, pyproject.toml, or jig.toml"""
        if config_path:
            found_path = Path(config_path)
            if not found_path.exists():
                click.echo(f"ERROR: Configuration file not found: {config_path}", err=True)
                sys.exit(1)
            return cls.load(tomllib.load(found_path.open("rb")), found_path)

        if (jigfile := Path("jig.toml")).exists():
            return cls.load(tomllib.load(jigfile.open("rb")), jigfile)

        if (pyproject_path := Path("pyproject.toml")).exists():
            data = tomllib.load(pyproject_path.open("rb"))
            if "tool" in data and "jig" in data["tool"]:
                return cls.load(data, pyproject_path)

        if init:
            return cls()
        click.echo(
            "ERROR: No pyproject.toml or jig.toml found, use --config to specify a config path.",
            err=True,
        )
        sys.exit(1)

    @classmethod
    def load(cls, data: dict[str, Any], path: Path) -> Config:
        """Load configuration from parsed TOML data"""
        # figure out config location and "Deployment name must be unique. Tip: update ..." message
        is_pyproject = path.name.endswith("pyproject.toml")
        if is_pyproject:
            jig_config = data.get("tool", {}).get("jig", {})
            if name := jig_config.get("name"):
                tip = "update `name` in your pyproject.toml"
            elif name := data.get("project", {}).get("name", ""):
                tip = "update `project.name` in your pyproject.toml"
            else:
                name = path.resolve().parent.name
                tip = "rename your folder or add `project.name` to your pyproject.toml"
                click.echo(f"\N{PACKAGE} Name not set in {path} - defaulting to {name}")
        else:
            jig_config = data
            if name := jig_config.get("name"):
                tip = f"update `name` in {path}"
            else:
                name = path.resolve().parent.name
                tip = f"rename your folder or add `name` to {path}"
                click.echo(f"\N{PACKAGE} Name not set in {path} - defaulting to {name}")

        if autoscaling := jig_config.get("autoscaling", {}):
            autoscaling["model"] = name
            jig_config["deploy"]["autoscaling"] = autoscaling

        # Support volume_mounts at jig level (merge into deploy config)
        jig_config.setdefault("deploy", {})["volume_mounts"] = jig_config.get("volume_mounts", [])

        return cls(
            image=ImageConfig.from_dict(jig_config.get("image", {})),
            deploy=DeployConfig.from_dict(jig_config.get("deploy", {})),
            dockerfile=jig_config.get("dockerfile", "Dockerfile"),
            model_name=name,
            _path=path,
            _unique_name_tip=tip,
        )


# --- State Management ---


@dataclass
class State:
    """Persistent state stored in .jig.json"""

    _config_dir: Path
    _project_name: str
    registry_base_path: str = ""
    secrets: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config_dir: Path, project_name: str, **data: Any) -> State:
        filtered = {k: v for k, v in data.items() if k in cls.__annotations__ and not k.startswith("_")}
        return cls(_config_dir=config_dir, _project_name=project_name, **filtered)

    @classmethod
    def load(cls, config_dir: Path, project_name: str) -> State:
        """Load state for a specific project from .jig.json.

        The state file structure is:
        {
          "project-name-1": {
            "registry_base_path": "...",
            "secrets": {...},
            "volumes": {...}
          },
          "project-name-2": {...}
        }

        """
        path = config_dir / ".jig.json"
        try:
            all_data = json.loads(path.read_text())

            # Check if this is the new nested structure (project_name as key)
            if project_name in all_data and isinstance(all_data[project_name], dict):
                # New structure: extract project-specific state
                project_data = all_data[project_name]
                return cls.from_dict(config_dir, project_name, **project_data)
            # Secrets or volumes exist, but not yet migrated (don't care about registry base path)
            if "secrets" in all_data or "volumes" in all_data:
                return cls.from_dict(config_dir, project_name, **all_data)
            # File exists but this project isn't in it yet
            return cls(_config_dir=config_dir, _project_name=project_name)
        except FileNotFoundError:
            return cls(_config_dir=config_dir, _project_name=project_name)

    def save(self) -> None:
        """Save state for this project to .jig.json.

        Preserves other projects' state in the same file.
        """
        path = self._config_dir / ".jig.json"

        # Load existing file to preserve other projects
        try:
            all_data = json.loads(path.read_text())
        except FileNotFoundError:
            all_data = {}

        # Update this project's state
        project_data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        all_data[self._project_name] = project_data

        # Save back to file
        with open(path, "w") as f:
            json.dump(all_data, f, indent=2)


# == Status prettyprint utils ==


def _format_timestamp(timestamp: str | None) -> str:
    """Format ISO timestamp for display"""
    t = timestamp or "-"
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return t


def _image_tag(image: str | None) -> str:
    if image is None:
        return "unknown"
    tag = image.rsplit(":", 1)[-1]
    return f"sha256:{tag[:8]}" if "sha256:" in image else tag


def format_deployment_status(d: Deployment) -> str:
    """Format d status for CLI display"""
    status = (
        "App:\n"
        f"  {'Name':<8}: {d.name} ┃ ID: {d.id}\n"
        f"  {'Image':<8}: {d.image}\n"
        f"  {'Status':<8}: {d.status}\n"
        f"  Created : {_format_timestamp(d.created_at)}"
        f" ┃ Updated : {_format_timestamp(d.updated_at)}\n"
    )

    if d.autoscaling:
        autoscaling_status = (
            f"\n  Autoscaling: {d.autoscaling.get('metric', 'N/A')} {d.autoscaling.get('target', 'N/A')}(target)\n"
        )
        status += autoscaling_status

    replica_status = (
        "\n"
        f"  Replicas:\n"
        f"    {'Min/Max':<16}: {d.min_replicas}/{d.max_replicas}\n"
        f"    {'Ready/Desired':<16}: {d.ready_replicas}/{d.desired_replicas}\n"
    )

    status += replica_status

    config_status = (
        f"\nConfiguration:\n"
        f"  Port: {d.port}\n"
        f"  Command: {d.command}\n"
        f"  Args: {d.args}\n"
        f"  Health Check Path: {d.health_check_path}\n"
        f"  Resources: {d.cpu} core CPU ┃ {d.memory}GB Memory ┃ {d.storage}GB Storage \n"
    )

    if d.gpu_count and d.gpu_type:
        config_status += f"  GPU: {d.gpu_count}x {d.gpu_type}\n"

    if d.volumes:
        config_status += f"\n  Volumes:\n    {'NAME':<28} MOUNT_PATH\n"
        for vol in d.volumes:
            config_status += f"    {vol.name:<28} {vol.mount_path}\n"

    if d.environment_variables:
        secrets = [env for env in d.environment_variables if env.value_from_secret]
        env_vars = [env for env in d.environment_variables if not env.value_from_secret]

        if secrets:
            config_status += f"\n  Secrets: {[secret.name for secret in secrets]}\n"

        if env_vars:
            config_status += f"\n  Environment Variables:\n    {'NAME':<40} VALUE\n"
            for env in env_vars:
                config_status += f"    {env.name:<40} {env.value}\n"

    status += config_status

    if d.replica_events:
        for replica in d.replica_events.values():
            replica.image = replica.image or "-"
        sorted_replicas = sorted(d.replica_events.items(), key=lambda item: item[1].image or "-", reverse=True)
        events_status = "\nReplica Events:\n"
        for image, group in groupby(sorted_replicas, key=lambda item: item[1].image):
            events_status += f"{_image_tag(image)}:\n"
            for replica_id, replica in group:
                events_status += f"  {replica_id}: "
                if replica.volume_preload_status and not replica.volume_preload_completed_at:
                    events_status += "Volume Preloading"
                else:
                    events_status += f"{replica.replica_status}"
                    if replica.replica_status == "Running":
                        events_status += f", ready since {_format_timestamp(replica.replica_ready_since)}"
                events_status += "\n"

        status += events_status
    return status


# = Secrets and Volumes subcommands =
# == Secrets ==


def _set_secret(
    client: Together,
    config: Config,
    state: State,
    name: str,
    value: str,
    description: str,
) -> None:
    """Set secret for the deployment"""
    deployment_secret_name = f"{config.model_name}-{name}"

    try:
        client.beta.jig.secrets.retrieve(deployment_secret_name)
        client.beta.jig.secrets.update(
            deployment_secret_name, name=deployment_secret_name, description=description, value=value
        )
        click.echo(f"\N{CHECK MARK} Updated secret: '{name}'")
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo("\N{ROCKET} Creating new secret")
        client.beta.jig.secrets.create(name=deployment_secret_name, value=value, description=description)
        click.echo(f"\N{CHECK MARK} Created secret: {name}")

    state.secrets[name] = deployment_secret_name
    state.save()


@click.group()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Manage deployment secrets"""
    pass


@secrets.command("set")
@click.pass_context
@click.option("--name", required=True, help="Secret name")
@click.option("--value", required=True, help="Secret value")
@click.option("--description", default="", help="Secret description")
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_set(
    ctx: click.Context,
    name: str,
    value: str,
    description: str,
    config_path: str | None,
) -> None:
    """Set a secret (create or update)"""
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)
    _set_secret(ctx.obj, config, state, name, value, description)


@secrets.command("unset")
@click.pass_context
@click.option("--name", required=True, help="Secret name to remove")
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_unset(
    ctx: click.Context,  # noqa: ARG001
    name: str,
    config_path: str | None,
) -> None:
    """Remove a secret from both remote and local state"""
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)

    if state.secrets.pop(name, ""):
        state.save()
        click.echo(f"\N{CHECK MARK} Deleted secret '{name}' from local state")
    else:
        click.echo(f"\N{CROSS MARK} Secret '{name}' is not set")


@secrets.command("list")
@click.pass_context
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Secrets")
def secrets_list(
    ctx: click.Context,
    config_path: str | None,
) -> None:
    """List all secrets with sync status"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)

    prefix = f"{config.model_name}-"

    local_secrets = set(state.secrets.keys())
    remote_secrets: set[str] = set()
    # Get all remote secrets then filter for this deployment
    for secret in client.beta.jig.secrets.list().data or []:
        if (name := secret.name) and name.startswith(prefix):
            # Strip prefix to get local name
            remote_secrets.add(name.removeprefix(prefix))

    if not local_secrets and not remote_secrets:
        click.echo(f"\N{INFORMATION SOURCE} No secrets configured for deployment '{config.model_name}'")
        return

    click.echo(f"\N{INFORMATION SOURCE} Secrets for deployment '{config.model_name}':")
    click.echo()

    for name in sorted(local_secrets | remote_secrets):
        in_local = name in local_secrets
        in_remote = name in remote_secrets

        if in_local and in_remote:
            status = click.style("synced", fg="green")
        elif in_local:
            status = click.style("local only", fg="yellow")
        else:
            status = click.style("remote only", fg="yellow")

        click.echo(f"  - {name} [{status}]")


# == Volumes ==
# --- File upload ---


def _validate_source(p: Path) -> None:
    if not p.exists():
        raise ValueError(f"Source path does not exist: {p}")
    if not p.is_dir():
        raise ValueError(f"Source path must be a directory: {p}")


async def _create_volume(client: Together, name: str, source: str) -> None:
    """Create a volume and upload files"""
    source_path = Path(source)
    _validate_source(source_path)
    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{ROCKET} Creating volume '{name}' with source prefix '{source_prefix}'")
    try:
        volume_response = client.beta.jig.volumes.create(
            name=name,
            type="readOnly",
            content={"type": "files", "source_prefix": source_prefix},
        )
        click.echo(f"\N{CHECK MARK} Volume created: {volume_response.id}")
    except Exception as e:
        raise RuntimeError(f"Failed to create volume: {e}") from e

    try:
        await Uploader(client).upload_files(source_path, volume_name=name)
    except Exception as e:
        click.echo(f"\N{CROSS MARK} Upload failed: {e}")
        click.echo(f"\N{WASTEBASKET} Cleaning up volume '{name}'")
        try:
            client.beta.jig.volumes.delete(name)
        except Exception as cleanup_error:
            click.echo(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise


async def _update_volume(client: Together, name: str, source: str) -> None:
    """Update a volume and re-upload files"""
    source_path = Path(source)
    _validate_source(source_path)
    try:
        client.beta.jig.volumes.retrieve(name)
    except APIStatusError as e:
        if e.status_code == 404:
            raise ValueError(f"Volume '{name}' does not exist") from e
        raise

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{INFORMATION SOURCE} Uploading files for volume '{name}'")
    await Uploader(client).upload_files(source_path, volume_name=name)

    click.echo(f"\N{INFORMATION SOURCE} Updating volume '{name}' with source prefix '{source_prefix}'")
    client.beta.jig.volumes.update(name, content={"type": "files", "source_prefix": source_prefix})
    click.echo("\N{CHECK MARK} Volume updated successfully")


# --- Volumes CLI Commands ---


@click.group()
@click.pass_context
def volumes(ctx: click.Context) -> None:
    """Manage volumes"""
    pass


@volumes.command("create")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="Source directory path")
@handle_api_errors("Volumes")
def volumes_create(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Create a volume and upload files"""
    client: Together = ctx.obj
    asyncio.run(_create_volume(client, name, source))


@volumes.command("update")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="New source directory path")
@handle_api_errors("Volumes")
def volumes_update(
    ctx: click.Context,
    name: str,
    source: str,
) -> None:
    """Update a volume and re-upload files"""
    client: Together = ctx.obj
    asyncio.run(_update_volume(client, name, source))


@volumes.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_delete(
    ctx: click.Context,
    name: str,
) -> None:
    """Delete a volume"""
    client: Together = ctx.obj

    try:
        client.beta.jig.volumes.delete(name)
        click.echo(f"\N{CHECK MARK} Deleted volume '{name}'")
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo(f"\N{CROSS MARK} Volume '{name}' not found")


@volumes.command("describe")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")
def volumes_describe(
    ctx: click.Context,
    name: str,
) -> None:
    """Describe a volume"""
    client: Together = ctx.obj

    try:
        response = client.beta.jig.volumes.with_raw_response.retrieve(name)
        click.echo(json.dumps(response.json(), indent=2))
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo(f"\N{CROSS MARK} Volume '{name}' not found")


@volumes.command("list")
@click.pass_context
@handle_api_errors("Volumes")
def volumes_list(ctx: click.Context) -> None:
    """List all volumes"""
    client: Together = ctx.obj
    response = client.beta.jig.volumes.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))


# == Main CLI ==
# --- Helper Functions ---


def _get_api_base_url(client: Together) -> str:
    """Extract base URL (scheme://host) from client, stripping any path like /v1"""
    parsed = urlparse(str(client.base_url))
    return f"{parsed.scheme}://{parsed.netloc}"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run process with defaults"""
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def _generate_dockerfile(config: Config) -> str:
    """Generate Dockerfile from config"""
    apt = ""
    if config.image.system_packages:
        sys_pkgs = " ".join(config.image.system_packages)
        apt = f"""RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \\
  apt-get update && \\
  DEBIAN_FRONTEND=noninteractive \\
  apt-get install -y --no-install-recommends {sys_pkgs} && \\
  apt-get clean && rm -rf /var/lib/apt/lists/*
"""

    if env := "\n".join(f"ENV {k}={v}" for k, v in config.image.environment.items()):
        env += "\n"

    if run := "\n".join(f"RUN {cmd}" for cmd in config.image.run):
        run += "\n"

    copy = "\n".join(f"COPY {file} {file}" for file in _get_files_to_copy(config))

    # Check if .git exists in current directory
    if Path(".git").exists():
        git_version_cmd = 'RUN --mount=type=bind,source=.git,target=/git git --git-dir /git describe --tags --exact-match > VERSION || echo "0.0.0-dev" > VERSION'
    else:
        git_version_cmd = 'RUN echo "0.0.0-dev" > VERSION'

    return f"""{DOCKERFILE_MANAGED_MARKER}

# Build stage
FROM python:{config.image.python_version} AS builder

{apt}
# Grab UV to install python packages
COPY --from=ghcr.io/astral-sh/uv /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --compile-bytecode . && \\
    (python -c "import sprocket" 2>/dev/null || (echo "sprocket not found in pyproject.toml, installing from pypi.together.ai..." && uv pip install --system --extra-index-url https://pypi.together.ai/ sprocket))

# Final stage - slim image
FROM python:{config.image.python_version}-slim

{apt}
COPY --from=builder /usr/local/lib/python{config.image.python_version} /usr/local/lib/python{config.image.python_version}
COPY --from=builder /usr/local/bin /usr/local/bin

# Tini for proper signal handling
COPY --from=krallin/ubuntu-tini:latest /usr/local/bin/tini /tini
ENTRYPOINT ["/tini", "--"]

{env}
{run}
WORKDIR /app
{copy}
ENV DEPLOYMENT_NAME={config.model_name}
# this tag will set the X-Worker-Version header, used for rollout monitoring
{git_version_cmd}

CMD {json.dumps(shlex.split(config.image.cmd))}"""


def _get_files_to_copy(config: Config) -> list[str]:
    """Combine explicitly copied files with git files if requested and valid"""
    files = set(config.image.copy)
    if config.image.auto_include_git:
        try:
            if _run(["git", "status", "--porcelain"]).stdout.strip():
                raise RuntimeError("Git repository has uncommitted changes: auto_include_git not allowed.")
            git_files = _run(["git", "ls-files"]).stdout.strip().split("\n")
            files.update(f for f in git_files if f and f != ".")
        except subprocess.CalledProcessError:
            pass

    if "." in files:
        raise ValueError("Copying '.' is not allowed. Please enumerate specific files.")

    return sorted(files)


def _dockerfile(config: Config) -> bool:
    """Generate Dockerfile if appropriate.

    Returns True if Dockerfile was generated, False if skipped (user-managed file exists).

    Logic:
    - If no Dockerfile exists → generate and return True
    - If Dockerfile exists without our marker → skip and return False (user-managed)
    - Else and config is older → skip and return True (no-op)
    - Else → regenerate and return True
    """
    dockerfile_path = Path(config.dockerfile)

    if dockerfile_path.exists():
        first_line = dockerfile_path.read_text().split("\n")[0]
        if first_line != DOCKERFILE_MANAGED_MARKER:
            return False

        # Skip regeneration if config hasn't changed
        if config._path and config._path.exists() and dockerfile_path.stat().st_mtime >= config._path.stat().st_mtime:
            return True

    dockerfile_path.write_text(_generate_dockerfile(config))

    return True


def _get_image(state: State, config: Config, tag: str = "latest") -> str:
    """Get full image name"""
    return f"{state.registry_base_path}/{config.model_name}:{tag}"


def _get_image_with_digest(state: State, config: Config, tag: str = "latest") -> str:
    """Get full image name tagged with digest"""
    image_name = _get_image(state, config, tag)
    if tag != "latest":
        return image_name
    try:
        cmd = ["docker", "inspect", "--format={{json .RepoDigests}}", image_name]
        if (repo_digests := _run(cmd).stdout.strip()) and repo_digests != "null":
            registry = image_name.rsplit("/", 2)[0]
            for digest in json.loads(repo_digests):
                if digest.startswith(registry):
                    return str(digest)
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() if e.stderr else "Docker command failed"
        raise RuntimeError(f"Failed to get digest for {image_name}: {msg}") from e
    raise RuntimeError(f"No registry digest found for {image_name}. Make sure the image was pushed to registry first.")


def _ensure_registry_base_path(client: Together, state: State) -> None:
    """Ensure registry base path is set in state"""
    if not state.registry_base_path:
        response = client._client.get("/image-repositories/base-path", headers=client.auth_headers)
        response.raise_for_status()
        data = response.json()
        # Strip protocol prefix - Docker tags don't support URLs
        state.registry_base_path = data["base-path"].removeprefix("http://").removeprefix("https://")
        state.save()


def _build_warm_image(base_image: str) -> None:
    """Run a warmup container to generate a cache, then rebuild with cache baked in.

    This runs the container with RUN_AND_EXIT=1 which triggers warmup_inputs in sprocket.
    The cache directory is mounted at /app/torch_cache and the user's code should set the
    appropriate env var (TORCHINDUCTOR_CACHE_DIR, TKCC_OUTPUT_DIR, etc.) to point there.
    """
    cache_dir = Path(".") / WARMUP_DEST
    # Clean any existing cache
    try:
        shutil.rmtree(cache_dir)
    except FileNotFoundError:
        pass
    cache_dir.mkdir(exist_ok=True)

    click.echo("\N{FIRE} Running warmup to generate compile cache...")

    # Run container with GPU and RUN_AND_EXIT=1
    # Mount current dir as /app so warmup_inputs can reference local weights
    # Mount cache dir for compile artifacts
    cmd = ["docker", "run", "--rm", "--gpus", "all", "-e", "RUN_AND_EXIT=1"]
    cmd.extend(["-e", f"{WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"])
    cmd.extend(["-v", f"{Path.cwd().absolute()}:/app"])
    # if MODEL_PRELOAD_PATH is set, also mount that (e.g. ~/.cache/huggingface)
    if weights_path := os.getenv("MODEL_PRELOAD_PATH"):
        cmd.extend(["-v", f"{weights_path}:{weights_path}"])
        cmd.extend(["-e", f"MODEL_PRELOAD_PATH={weights_path}"])
    cmd.append(base_image)

    click.echo(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Warmup failed with code {result.returncode}")

    # Check cache was generated
    cache_files = list(cache_dir.rglob("*"))
    if not cache_files:
        raise RuntimeError("Warmup completed but no cache files were generated")

    click.echo(f"\N{CHECK MARK} Warmup complete, {len(cache_files)} cache files generated")

    # Generate cache dockerfile - copy cache to same location used during warmup
    cache_dockerfile = Path("Dockerfile.cache")
    dockerfile_content = f"""FROM {base_image}
COPY {cache_dir.name} /app/{WARMUP_DEST}
ENV {WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"""
    cache_dockerfile.write_text(dockerfile_content)

    click.echo("\N{PACKAGE} Building final image with cache...")
    final_cmd = ["docker", "build", "--platform", "linux/amd64", "-t", base_image]
    final_cmd.extend(["-f", str(cache_dockerfile), "."])

    if subprocess.run(final_cmd).returncode != 0:
        cache_dockerfile.unlink(missing_ok=True)
        raise RuntimeError("Cache image build failed")
    cache_dockerfile.unlink(missing_ok=True)
    click.echo("\N{CHECK MARK} Final image with cache built")


def _get_current_revision_id(d: Deployment) -> str:
    """Extract current revision ID from deployment environment variables."""
    for var in d.environment_variables or []:
        if var.name == "TOGETHER_DEPLOYMENT_REVISION_ID":
            return str(var.value)
    return ""


def _print_replica_failure(event: ReplicaEvents) -> None:
    if event.replica_status_reason:
        click.echo(f"  Reason: {event.replica_status_reason}")
    if event.replica_status_message:
        click.echo(f"  Message: {event.replica_status_message}")


def _fetch_and_print_logs(client: Together, deployment_name: str, replica_id: str) -> None:
    click.echo(f"\n--- Logs for {replica_id} ---")
    try:
        if lines := client.beta.jig.retrieve_logs(deployment_name, replica_id=replica_id).lines:
            for line in lines:
                click.echo(line)
        else:
            click.echo("No logs available")
    except Exception as e:
        click.echo(f"Failed to fetch logs: {e}")
    click.echo("--- End of logs ---\n")


class ReplicaTrackingResult(str, Enum):
    """Result of processing a single replica event."""

    CONTINUE = "continue"
    SUCCESS = "success"
    FAILURE = "failure"


def _process_replica_event(
    replica_id: str,
    event: ReplicaEvents,
    states: set[str],
    replica_ready_wait_start: dict[str, float],
    ready_timeout: float,
    client: Together,
    deployment_name: str,
) -> ReplicaTrackingResult:
    """Process a single replica event and return the tracking result.

    Updates `states` and `replica_ready_wait_start` as side effects.
    """
    volume_done = not event.volume_preload_status or bool(event.volume_preload_completed_at)

    # Track volume preload progress
    if event.volume_preload_status:
        if "volume_preload_started" not in states:
            click.echo(f"\N{PACKAGE} [{replica_id}] Preloading volume contents...")
            states.add("volume_preload_started")
        elif volume_done and "volume_preload_completed" not in states:
            click.echo(
                f"\N{CHECK MARK}  [{replica_id}] Successfully preloaded volume contents. "
                "Attaching the volume to the container..."
            )
            states.add("volume_preload_completed")

    # Skip terminated replicas
    if event.replica_status == "Terminated":
        return ReplicaTrackingResult.CONTINUE

    # Check if ready - SUCCESS
    if event.replica_status == "Running" and event.replica_ready_since:
        click.echo(f"\N{CHECK MARK}  [{replica_id}] Container is running and ready")
        click.echo("\N{ROCKET} Deployment successful!")
        click.echo("Note: Additional replicas may still be scaling up.")
        return ReplicaTrackingResult.SUCCESS

    # Check for CrashLoopBackOff
    if event.replica_status_reason == "CrashLoopBackOff":
        click.echo(f"\N{CROSS MARK} [{replica_id}] Container is crash looping")
        _print_replica_failure(event)
        _fetch_and_print_logs(client, deployment_name, replica_id)
        return ReplicaTrackingResult.FAILURE

    # Check for stuck in Running state without becoming ready
    if event.replica_status == "Running" and volume_done:
        # If wait start time is not set, set it to now
        wait_start = replica_ready_wait_start.setdefault(replica_id, time.time())
        if time.time() - wait_start > ready_timeout:
            click.echo(
                f"\N{CROSS MARK}  [{replica_id}] Container is running but "
                f"not ready to serve requests after {ready_timeout} seconds"
            )
            _print_replica_failure(event)
            _fetch_and_print_logs(client, deployment_name, replica_id)
            click.echo(f"Deployment '{deployment_name}' may still be in progress.")
            return ReplicaTrackingResult.FAILURE

    # Print status updates deduplicated by status + reason
    # Skip all status updates while volume preload is in progress
    if volume_done and event.replica_status_reason:
        status_key = f"{event.replica_status}_{event.replica_status_reason}"
        if status_key not in states:
            states.add(status_key)
            click.echo(
                f"\N{HOURGLASS WITH FLOWING SAND} [{replica_id}] {event.replica_status}: {event.replica_status_reason}"
            )
            if event.replica_status_message:
                click.echo(f"  {event.replica_status_message}")

    return ReplicaTrackingResult.CONTINUE


def _track_deployment_progress(deployment_name: str, client: Together) -> dict[str, Any] | None:
    """Track deployment progress until ready or failed.

    Polls deployment status every 3 seconds until:
    - Success: At least one replica with the latest revision has replica_ready_since set
    - Failure: CrashLoopBackOff or Running without ready_since for > 2 minute
    - Timeout: 10 minutes elapsed
    """
    poll_interval = 3  # seconds
    timeout = 600  # 10 minutes
    ready_timeout = 120  # 2 minutes for Running without ready_since

    start_time = time.time()
    printed_states: dict[str, set[str]] = {}  # replica_id -> set of printed states
    # replica_id -> when we started waiting for ready
    replica_ready_wait_start: dict[str, float] = {}

    click.echo("\N{HOURGLASS WITH FLOWING SAND} Deployment in-progress...")

    try:
        while time.time() - start_time < timeout:
            deployment = client.beta.jig.retrieve(deployment_name)

            # Handle scale to zero - no replicas expected
            if deployment.min_replicas == 0 and deployment.desired_replicas == 0:
                if str(deployment.status) == "ScaledToZero":
                    click.echo("\N{CHECK MARK} Deployment scaled to zero replicas")
                    return None
                # Not yet scaled to zero, wait and retry
                time.sleep(poll_interval)
                continue

            current_revision_id = _get_current_revision_id(deployment)

            replica_events = deployment.replica_events or {}

            # Filter to replicas with matching revision
            relevant_replicas = {
                replica_id: event
                for replica_id, event in replica_events.items()
                if event.revision_id == current_revision_id
            }

            if not relevant_replicas:
                time.sleep(poll_interval)
                continue

            for replica_id, event in relevant_replicas.items():
                if replica_id not in printed_states:
                    printed_states[replica_id] = set()

                result = _process_replica_event(
                    replica_id=replica_id,
                    event=event,
                    states=printed_states[replica_id],
                    replica_ready_wait_start=replica_ready_wait_start,
                    ready_timeout=ready_timeout,
                    client=client,
                    deployment_name=deployment_name,
                )

                if result == ReplicaTrackingResult.SUCCESS:
                    return None
                if result == ReplicaTrackingResult.FAILURE:
                    raise SystemExit(1)

            time.sleep(poll_interval)

        # Timeout reached
        click.echo("\N{CROSS MARK} Deployment tracking timed out after 10 minutes")
        click.echo(f"Deployment '{deployment_name}' may still be in progress.")
        click.echo("Run 'jig status' to check current state.")
        raise SystemExit(1)

    except KeyboardInterrupt:
        click.echo("\n\N{WARNING SIGN} Deployment tracking interrupted")
        click.echo(f"Deployment '{deployment_name}' may still be in progress.")
        click.echo("Run 'jig status' to check current state.")
        raise SystemExit(130) from None


# --- CLI Commands ---


# Shared CLI decorator: pass_context + config option + api error handling
def jig_command(f: Callable[..., Any]) -> Any:
    f = click.option("-c", "--config", "config_path", default=None, help="Configuration file path")(f)
    f = handle_api_errors("Jig")(f)
    f = click.pass_context(f)
    f = click.command()(f)
    return f


@click.command()
def init() -> None:
    """Initialize jig configuration"""
    if (pyproject := Path("pyproject.toml")).exists():
        click.echo("pyproject.toml already exists")
        return

    content = """[project]
name = "my-model"
version = "0.1.0"
dependencies = ["torch", "transformers", "sprocket"]

[[tool.uv.index]]
name = "together-pypi"
url = "https://pypi.together.ai/"

[tool.uv.sources]
sprocket = { index = "together-pypi" }

[tool.jig.image]
python_version = "3.11"
system_packages = ["git", "libglib2.0-0"]
cmd = "python app.py"

[tool.jig.deploy]
description = "My model deployment"
gpu_type = "h100-80gb"
gpu_count = 1
"""
    with open(pyproject, "w") as f:
        f.write(content)
    click.echo("\N{CHECK MARK} Created pyproject.toml")
    click.echo("  Edit the configuration and run 'jig deploy'")


@click.command()
@click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
@handle_api_errors("Jig")
def dockerfile(config_path: str | None) -> None:
    """Generate Dockerfile"""
    config = Config.find(config_path)
    if _dockerfile(config):
        click.echo("\N{CHECK MARK} Generated Dockerfile")
    else:
        click.echo(
            f"ERROR: {config.dockerfile} exists and is not managed by jig. "
            f"Remove or rename the file to allow jig to manage dockerfile.",
            err=True,
        )


@jig_command
@click.option("--tag", default="latest", help="Image tag")
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option(
    "--docker-args",
    default=None,
    help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)",
)
def build(
    ctx: click.Context,
    tag: str,
    warmup: bool,
    docker_args: str | None,
    config_path: str | None,
) -> None:
    """Build container image"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)
    _ensure_registry_base_path(client, state)

    image = _get_image(state, config, tag)

    if _dockerfile(config):
        click.echo("\N{CHECK MARK} Generated Dockerfile")
    else:
        click.echo(f"\N{INFORMATION SOURCE} Using existing {config.dockerfile} (not managed by jig)")

    click.echo(f"Building {image}")
    cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
    if config.dockerfile != "Dockerfile":
        cmd.extend(["-f", config.dockerfile])

    # Add extra docker args from flag or env
    extra_args = docker_args or os.getenv("DOCKER_BUILD_EXTRA_ARGS", "")
    if extra_args:
        cmd.extend(shlex.split(extra_args))
    if subprocess.run(cmd).returncode != 0:
        raise RuntimeError("Build failed")

    click.echo("\N{CHECK MARK} Built")

    if warmup:
        _build_warm_image(image)


@jig_command
@click.option("--tag", default="latest", help="Image tag")
def push(ctx: click.Context, tag: str, config_path: str | None) -> None:
    """Push image to registry"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)
    _ensure_registry_base_path(client, state)

    image = _get_image(state, config, tag)

    registry = state.registry_base_path.split("/")[0]
    login_cmd = f"echo {client.api_key} | docker login {registry} --username user --password-stdin"
    if subprocess.run(login_cmd, shell=True, capture_output=True).returncode != 0:
        raise RuntimeError("Registry login failed")

    click.echo(f"Pushing {image}")
    if subprocess.run(["docker", "push", image]).returncode != 0:
        raise RuntimeError("Push failed")
    click.echo("\N{CHECK MARK} Pushed")


@jig_command
@click.option("--tag", default="latest", help="Image tag")
@click.option("--build-only", is_flag=True, help="Build and push only")
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option(
    "--docker-args",
    default=None,
    help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)",
)
@click.option(
    "--image",
    "existing_image",
    default=None,
    help="Use existing image (skip build/push)",
)
@click.option("--detach", "detach", is_flag=True, help="Do not wait for deployment to complete")
def deploy(
    ctx: click.Context,
    tag: str,
    build_only: bool,
    warmup: bool,
    detach: bool,
    docker_args: str | None,
    existing_image: str | None,
    config_path: str | None,
) -> dict[str, Any] | None:
    """Deploy model"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    state = State.load(config._path.parent, config.model_name)
    _ensure_registry_base_path(client, state)

    if existing_image:
        deployment_image = existing_image
    else:
        # Invoke build and push
        ctx.invoke(
            build,
            tag=tag,
            warmup=warmup,
            docker_args=docker_args,
            config_path=config_path,
        )
        ctx.invoke(push, tag=tag, config_path=config_path)
        deployment_image = _get_image_with_digest(state, config, tag)

    if build_only:
        click.echo("\N{CHECK MARK} Build complete (--build-only)")
        return None

    deploy_data: dict[str, Any] = {
        "name": config.model_name,
        "description": config.deploy.description,
        "image": deployment_image,
        "min_replicas": config.deploy.min_replicas,
        "max_replicas": config.deploy.max_replicas,
        "port": config.deploy.port,
        "gpu_type": config.deploy.gpu_type,
        "gpu_count": config.deploy.gpu_count,
        "cpu": config.deploy.cpu,
        "memory": config.deploy.memory,
        "storage": config.deploy.storage,
        "autoscaling": config.deploy.autoscaling,
        "termination_grace_period_seconds": config.deploy.termination_grace_period_seconds,
        "volumes": [asdict(vm) for vm in config.deploy.volume_mounts],
    }

    if config.deploy.health_check_path:
        deploy_data["health_check_path"] = config.deploy.health_check_path
    if config.deploy.command:
        deploy_data["command"] = config.deploy.command

    env_vars = [{"name": k, "value": v} for k, v in config.deploy.environment_variables.items()]
    env_vars.append({"name": "TOGETHER_API_BASE_URL", "value": _get_api_base_url(client)})

    if "TOGETHER_API_KEY" not in state.secrets:
        _set_secret(client, config, state, "TOGETHER_API_KEY", client.api_key, "Auth key for queue API")

    for name, secret_id in state.secrets.items():
        env_vars.append({"name": name, "value_from_secret": secret_id})

    deploy_data["environment_variables"] = env_vars

    if DEBUG:
        click.echo(json.dumps(deploy_data, indent=2))
    click.echo(f"Deploying model: {config.model_name}")

    def handle_create() -> Deployment:
        click.echo("\N{ROCKET} Creating new deployment")
        try:
            response = client.beta.jig.deploy(**deploy_data)
            click.echo(f"\N{CHECK MARK} Deployed: {config.model_name}")
            return response
        except APIStatusError as e:
            # all errors:
            # "min replicas cannot be greater than max replicas"
            # "storage cannot be more than %d GB"
            # "user does not have access to the specified image"
            # "invalid mount_path: %s"
            # "only one readOnly volume is allowed per deployment"
            # "volume not found"
            # gorm tx.Create(...).Save() err (internal server error?)
            # "failed to add deployment reference" (failed to add deployment reference to secret or "Failed to delete secret metadata from database",)
            # "failed to delete secret" ("Failed to delete secret metadata from database" in logs)
            # "failed to delete deployment from kubernetes: %w"
            # errors for toKubernetesEnvironmentVariables, toKubernetesVolumeMounts, getCustomScalers, ReconcileWithKubernetes
            error_body: Any = getattr(e, "body", None)
            error_message = (  # pyright: ignore
                error_body.get("error", "") if isinstance(error_body, dict) else ""  # pyright: ignore
            )
            if "already exists" in error_message or "must be unique" in error_message:
                raise RuntimeError(f"Deployment name must be unique. Tip: {config._unique_name_tip}") from None
            # TODO: helpful tips for more error cases
            raise

    try:
        existing = client.beta.jig.retrieve(config.model_name)
        old_revision_id = _get_current_revision_id(existing)
        was_scaled_to_zero = existing.ready_replicas == 0
        response = client.beta.jig.update(config.model_name, **deploy_data)
        click.echo("\N{CHECK MARK}  Applied new deployment configuration")
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        old_revision_id = ""
        was_scaled_to_zero = False
        response = handle_create()

    if detach:
        return response.model_dump()

    # Skip tracking if revision didn't change and not scaling up from zero
    new_revision_id = _get_current_revision_id(response)
    scaling_up = was_scaled_to_zero and response.min_replicas and response.min_replicas > 0
    if old_revision_id and old_revision_id == new_revision_id and not scaling_up:
        return None

    return _track_deployment_progress(config.model_name, client)


@jig_command
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON")
def status(ctx: click.Context, config_path: str | None, json_output: bool = False) -> None:
    """Get deployment status"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    response = client.beta.jig.retrieve(config.model_name)

    if json_output:
        click.echo(response.model_dump_json(indent=2))
    else:
        click.echo(format_deployment_status(response))


@jig_command
def endpoint(ctx: click.Context, config_path: str | None) -> None:
    """Get deployment endpoint URL"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    click.echo(f"{_get_api_base_url(client)}/v1/deployment-request/{config.model_name}")


@jig_command
@click.option("--follow", is_flag=True, help="Follow log output")
def logs(ctx: click.Context, follow: bool, config_path: str | None) -> None:
    """Get deployment logs"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    if not follow:
        if lines := client.beta.jig.retrieve_logs(config.model_name).lines:
            for line in lines:
                click.echo(line)
        else:
            click.echo("No logs available")
        return

    # Stream logs using SDK streaming response
    try:
        with client.beta.jig.with_streaming_response.retrieve_logs(config.model_name) as stream:
            for line in stream.iter_lines():
                if line:
                    for log_line in json.loads(line).get("lines", []):
                        click.echo(log_line)
    except KeyboardInterrupt:
        click.echo("\nStopped following logs")
    except Exception as e:
        click.echo(f"\nConnection ended: {e}")


@jig_command
def destroy(ctx: click.Context, config_path: str | None) -> None:
    """Destroy deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)
    client.beta.jig.destroy(config.model_name)
    click.echo(f"\N{WASTEBASKET} Destroyed {config.model_name}")


@jig_command
@click.option("--prompt", default=None, help="Job prompt")
@click.option("--payload", default=None, help="Job payload JSON")
@click.option("--watch", is_flag=True, help="Watch job status until completion")
def submit(
    ctx: click.Context,
    prompt: str | None,
    payload: str | None,
    watch: bool,
    config_path: str | None,
) -> None:
    """Submit a job to the deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    if not prompt and not payload:
        raise click.UsageError("Either --prompt or --payload required")

    raw_response = client.beta.jig.queue.with_raw_response.submit(
        model=config.model_name,
        payload=json.loads(payload) if payload else {"prompt": prompt},
        priority=1,
    )

    # Getting raw response and parsing ourselves here due to Stainless limitation with
    # Pydantic aliases not handled correctly (both fields are present in the model)
    submit_response = QueueSubmitResponse.model_validate_json(raw_response.read())

    click.echo("\N{CHECK MARK} Submitted job")
    click.echo(submit_response.model_dump_json(indent=2))

    if not watch or not submit_response.request_id:
        return

    click.echo(f"\nWatching job {submit_response.request_id}...")
    last_status: str | None = None
    while True:
        try:
            response = client.beta.jig.queue.retrieve(
                model=config.model_name,
                request_id=submit_response.request_id,
            )
            current_status = response.status
            if current_status != last_status:
                click.echo(response.model_dump_json(indent=2))
                last_status = current_status

            if current_status in ["done", "failed", "finished", "error", "canceled"]:
                if current_status != "done":
                    ctx.exit(1)
                break

            time.sleep(1)

        except KeyboardInterrupt:
            click.echo(f"\nStopped watching {submit_response.request_id}")
            ctx.exit(130)


@jig_command
@click.option("--request-id", required=True, help="Job request ID")
def job_status(ctx: click.Context, request_id: str, config_path: str | None) -> None:
    """Get status of a specific job"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client.beta.jig.queue.retrieve(
        model=config.model_name,
        request_id=request_id,
    )
    click.echo(response.model_dump_json(indent=2))


@jig_command
def queue_status(ctx: click.Context, config_path: str | None) -> None:
    """Get queue metrics for the deployment"""
    client: Together = ctx.obj
    config = Config.find(config_path)

    response = client.beta.jig.queue.with_raw_response.metrics(model=config.model_name)
    click.echo(json.dumps(response.json(), indent=2))


@click.command("list")
@handle_api_errors("Jig")
@click.pass_context
def list_deployments(ctx: click.Context) -> None:
    """List all deployments"""
    client: Together = ctx.obj
    response = client.beta.jig.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))
