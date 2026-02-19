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
from functools import wraps
from itertools import groupby
from collections import defaultdict
from dataclasses import field, asdict, dataclass, is_dataclass
from urllib.parse import urlparse

import click

from together import Together
from together._exceptions import APIError, APIStatusError
from together.lib.cli.api._utils import handle_api_errors
from together.types.beta.deployment import Deployment, ReplicaEvents
from together.resources.beta.jig.jig import JigResource
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


# TODO: make state a property of config


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
                raise click.UsageError(f"Configuration file not found: {config_path}")
            return cls.load(tomllib.loads(found_path.read_text()), found_path)

        if (jigfile := Path("jig.toml")).exists():
            return cls.load(tomllib.loads(jigfile.read_text()), jigfile)

        if (pyproject_path := Path("pyproject.toml")).exists():
            data = tomllib.loads(pyproject_path.read_text())
            if "tool" in data and "jig" in data["tool"]:
                return cls.load(data, pyproject_path)

        if init:
            return cls()
        raise click.UsageError("No pyproject.toml or jig.toml found, use --config to specify a config path.")

    @classmethod
    def load(cls, data: dict[str, Any], path: Path) -> Config:
        """Load configuration from parsed TOML data"""
        # figure out config location and "Deployment name must be unique. Tip: update ..." message
        if path.name.endswith("pyproject.toml"):
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
        try:
            all_data = json.loads((config_dir / ".jig.json").read_text())
            # is our project in the nested state format?
            if isinstance(project_data := all_data.get(project_name), dict):
                return cls.from_dict(config_dir, project_name, **project_data)
            # top-level secrets/volumes project fields are set, but not migrated
            # (don't care about registry base path)
            if "secrets" in all_data or "volumes" in all_data:
                return cls.from_dict(config_dir, project_name, **all_data)
            # state exists but our project isn't in it
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
        all_data[self._project_name] = {k: v for k, v in asdict(self).items() if not k.startswith("_")}

        path.write_text(json.dumps(all_data, indent=2))


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
        status += (
            f"\n  Autoscaling: {d.autoscaling.get('metric', 'N/A')} {d.autoscaling.get('target', 'N/A')}(target)\n"
        )

    status += (
        "\n"
        f"  Replicas:\n"
        f"    {'Min/Max':<16}: {d.min_replicas}/{d.max_replicas}\n"
        f"    {'Ready/Desired':<16}: {d.ready_replicas}/{d.desired_replicas}\n"
    )

    status += (
        f"\nConfiguration:\n"
        f"  Port: {d.port}\n"
        f"  Command: {d.command}\n"
        f"  Args: {d.args}\n"
        f"  Health Check Path: {d.health_check_path}\n"
        f"  Resources: {d.cpu} core CPU ┃ {d.memory}GB Memory ┃ {d.storage}GB Storage \n"
    )

    if d.gpu_count and d.gpu_type:
        status += f"  GPU: {d.gpu_count}x {d.gpu_type}\n"

    if d.volumes:
        status += f"\n  Volumes:\n    {'NAME':<28} MOUNT_PATH\n"
        for vol in d.volumes:
            status += f"    {vol.name:<28} {vol.mount_path}\n"

    if d.environment_variables:
        secrets = [env for env in d.environment_variables if env.value_from_secret]
        env_vars = [env for env in d.environment_variables if not env.value_from_secret]

        if secrets:
            status += f"\n  Secrets: {[secret.name for secret in secrets]}\n"

        if env_vars:
            status += f"\n  Environment Variables:\n    {'NAME':<40} VALUE\n"
            for env in env_vars:
                status += f"    {env.name:<40} {env.value}\n"

    if d.replica_events:
        sorted_replicas = sorted(d.replica_events.items(), key=lambda item: item[1].image or "-", reverse=True)
        events_status = "\nReplica Events:\n"
        for image, group in groupby(sorted_replicas, key=lambda item: item[1].image or "-"):
            events_status += f"{_image_tag(image or '-')}:\n"
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


def _set_secret(jig: Jig, name: str, value: str, description: str) -> None:
    """Set secret for the deployment"""
    scoped_name = f"{jig.config.model_name}-{name}"

    try:
        jig.api.secrets.retrieve(scoped_name)
        jig.api.secrets.update(id=scoped_name, name=scoped_name, description=description, value=value)
        click.echo(f"\N{CHECK MARK} Updated secret: '{name}'")
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo("\N{ROCKET} Creating new secret")
        jig.api.secrets.create(name=scoped_name, value=value, description=description)
        click.echo(f"\N{CHECK MARK} Created secret: {name}")

    jig.state.secrets[name] = scoped_name
    jig.state.save()


# should this have the same prefix behavior as handle_api_errors?
def _print_errors(f: Callable[..., Any]) -> Any:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            f(*args, **kwargs)
        except (click.Abort, click.ClickException):
            raise
        except APIError as e:
            msg = getattr(e.body, "message", str(e.body)) if e.body is not None else str(e)
            click.echo(msg, err=True)
            raise SystemExit(1) from None
        except Exception as e:
            click.echo(str(e), err=True)
            raise SystemExit(1) from None

    return wrapper


def _pass_jig(f: Callable[..., Any]) -> Any:
    @click.pass_context
    @click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
    @_print_errors
    @wraps(f)
    def wrapper(ctx: click.Context, config_path: str | None, *args: Any, **kwargs: Any) -> None:
        f(Jig(ctx.obj, config_path), *args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Manage deployment secrets"""
    pass


@secrets.command("set")
@_pass_jig
@_print_errors
@click.option("--name", required=True, help="Secret name")
@click.option("--value", required=True, help="Secret value")
@click.option("--description", default="", help="Secret description")
def secrets_set(jig: Jig, name: str, value: str, description: str) -> None:
    """Set a secret (create or update)"""
    _set_secret(jig, name, value, description)


@secrets.command("unset")
@_pass_jig
@_print_errors
@click.option("--name", required=True, help="Secret name to remove")
def secrets_unset(jig: Jig, name: str) -> None:
    """Remove a secret from both remote and local state"""
    try:
        del jig.state.secrets[name]
        jig.state.save()
        click.echo(f"\N{CHECK MARK} Deleted secret '{name}' from local state")
    except KeyError:
        click.echo(f"\N{CROSS MARK} Secret '{name}' is not set")


@secrets.command("list")
@_pass_jig
@_print_errors
def secrets_list(jig: Jig) -> None:
    """List all secrets with sync status"""
    prefix = f"{jig.config.model_name}-"

    local_secrets = set(jig.state.secrets.keys())
    remote_secrets: set[str] = set()
    # Get all remote secrets then filter for this deployment
    for secret in jig.api.secrets.list().data or []:
        if (name := secret.name) and name.startswith(prefix):
            # Strip prefix to get local name
            remote_secrets.add(name.removeprefix(prefix))

    if not local_secrets and not remote_secrets:
        click.echo(f"\N{INFORMATION SOURCE} No secrets configured for deployment '{jig.config.model_name}'")
        return

    click.echo(f"\N{INFORMATION SOURCE} Secrets for deployment '{jig.config.model_name}':")
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


async def _create_volume(client: JigResource, name: str, source: str) -> None:
    """Create a volume and upload files"""
    source_path = Path(source)
    _validate_source(source_path)
    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{ROCKET} Creating volume '{name}' with source prefix '{source_prefix}'")
    try:
        volume_response = client.volumes.create(
            name=name,
            type="readOnly",
            content={"type": "files", "source_prefix": source_prefix},
        )
        click.echo(f"\N{CHECK MARK} Volume created: {volume_response.id}")
    except Exception as e:
        raise RuntimeError(f"Failed to create volume: {e}") from e

    try:
        await Uploader(client._client).upload_files(source_path, volume_name=name)
    except Exception as e:
        click.echo(f"\N{CROSS MARK} Upload failed: {e}")
        click.echo(f"\N{WASTEBASKET} Cleaning up volume '{name}'")
        try:
            client.volumes.delete(name)
        except Exception as cleanup_error:
            click.echo(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise


async def _update_volume(client: JigResource, name: str, source: str) -> None:
    """Update a volume and re-upload files"""
    source_path = Path(source)
    _validate_source(source_path)
    try:
        client.volumes.retrieve(name)
    except APIStatusError as e:
        if e.status_code == 404:
            raise ValueError(f"Volume '{name}' does not exist") from e
        raise

    source_prefix = f"{name}/{source_path.name}"

    click.echo(f"\N{INFORMATION SOURCE} Uploading files for volume '{name}'")
    await Uploader(client._client).upload_files(source_path, volume_name=name)

    click.echo(f"\N{INFORMATION SOURCE} Updating volume '{name}' with source prefix '{source_prefix}'")
    client.volumes.update(name, content={"type": "files", "source_prefix": source_prefix})
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
@handle_api_errors("Volumes")  # fixme
def volumes_create(ctx: click.Context, name: str, source: str) -> None:
    """Create a volume and upload files"""
    client: JigResource = ctx.obj.beta.jig
    asyncio.run(_create_volume(client, name, source))


@volumes.command("update")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@click.option("--source", required=True, help="New source directory path")
@handle_api_errors("Volumes")  # fixme
def volumes_update(ctx: click.Context, name: str, source: str) -> None:
    """Update a volume and re-upload files"""
    client: JigResource = ctx.obj.beta.jig
    asyncio.run(_update_volume(client, name, source))


@volumes.command("delete")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")  # fixme
def volumes_delete(ctx: click.Context, name: str) -> None:
    """Delete a volume"""
    client: JigResource = ctx.obj.beta.jig

    try:
        client.volumes.delete(name)
        click.echo(f"\N{CHECK MARK} Deleted volume '{name}'")
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo(f"\N{CROSS MARK} Volume '{name}' not found")


@volumes.command("describe")
@click.pass_context
@click.option("--name", required=True, help="Volume name")
@handle_api_errors("Volumes")  # fixme
def volumes_describe(
    ctx: click.Context,
    name: str,
) -> None:
    """Describe a volume"""
    client: JigResource = ctx.obj.beta.jig

    try:
        response = client.volumes.with_raw_response.retrieve(name)
        click.echo(json.dumps(response.json(), indent=2))
    except APIStatusError as e:
        if e.status_code != 404:
            raise
        click.echo(f"\N{CROSS MARK} Volume '{name}' not found")


@volumes.command("list")
@click.pass_context
@handle_api_errors("Volumes")  # fixme
def volumes_list(ctx: click.Context) -> None:
    """List all volumes"""
    client: JigResource = ctx.obj.beta.jig
    response = client.volumes.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))


# == Main CLI ==
# --- Helper Functions ---


def _get_api_base_url(client: Together) -> str:
    """Extract base URL (scheme://host) from client, stripping any path like /v1"""
    parsed = urlparse(str(client.base_url))
    return f"{parsed.scheme}://{parsed.netloc}"


def _run(cmd: list[str], *, input: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run subprocess. Captures output unless input is provided."""
    if input is not None:
        return subprocess.run(cmd, input=input, text=True)
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


def _build_warm_image(base_image: str) -> None:
    """Run a warmup container to generate a cache, then rebuild with cache baked in.

    This runs the container with RUN_AND_EXIT=1 which triggers warmup_inputs in sprocket.
    The cache directory is mounted at /app/torch_cache and the user's code should set the
    appropriate env var (TORCHINDUCTOR_CACHE_DIR, TKCC_OUTPUT_DIR, etc.) to point there.
    """
    cache_dir = Path(WARMUP_DEST)
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
    cmd.extend(["-v", f"{Path.cwd()}:/app"])
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
    final_dockerfile = f"""FROM {base_image}
COPY {cache_dir.name} /app/{WARMUP_DEST}
ENV {WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"""

    click.echo("\N{PACKAGE} Building final image with cache...")
    final_cmd = ["docker", "build", "--platform", "linux/amd64", "-t", base_image, "-f", "-", "."]

    if _run(final_cmd, input=final_dockerfile).returncode != 0:
        raise RuntimeError("Cache image build failed")
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


def _fetch_and_print_logs(client: JigResource, deployment_name: str, replica_id: str) -> None:
    click.echo(f"\n--- Logs for {replica_id} ---")
    try:
        if lines := client.retrieve_logs(deployment_name, replica_id=replica_id).lines:
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


@dataclass
class Tracker:
    client: JigResource
    deployment_name: str

    poll_interval: int = 3  # seconds
    timeout: int = 600  # 10 minutes
    ready_timeout: int = 120  # 2 minutes for Running without ready_since

    # replica_id -> set of printed states
    printed_states: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    # replica_id -> when we started waiting for ready
    replica_wait_start: dict[str, float] = field(default_factory=lambda: defaultdict(time.time))

    def track_deployment_progress(self) -> None:
        """Track deployment progress until ready or failed.

        Polls deployment status every 3 seconds until:
        - Success: At least one replica with the latest revision has replica_ready_since set
        - Failure: CrashLoopBackOff or Running without ready_since for > 2 minute
        - Timeout: 10 minutes elapsed
        """
        start_time = time.time()

        click.echo("\N{HOURGLASS WITH FLOWING SAND} Deployment in-progress...")

        try:
            while time.time() - start_time < self.timeout:
                deployment = self.client.retrieve(self.deployment_name)

                # Handle scale to zero - no replicas expected
                if deployment.min_replicas == 0 and deployment.desired_replicas == 0:
                    if str(deployment.status) == "ScaledToZero":
                        click.echo("\N{CHECK MARK} Deployment scaled to zero replicas")
                        return
                    # Not yet scaled to zero, wait and retry
                    time.sleep(self.poll_interval)
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
                    time.sleep(self.poll_interval)
                    continue

                for replica_id, event in relevant_replicas.items():
                    result = self.process_replica_event(replica_id=replica_id, event=event)

                    if result == ReplicaTrackingResult.SUCCESS:
                        return
                    if result == ReplicaTrackingResult.FAILURE:
                        raise SystemExit(1)

                time.sleep(self.poll_interval)

            # Timeout reached
            click.echo("\N{CROSS MARK} Deployment tracking timed out after 10 minutes")
            click.echo(f"Deployment '{self.deployment_name}' may still be in progress.")
            click.echo("Run 'jig status' to check current state.")
            raise SystemExit(1)

        except KeyboardInterrupt:
            click.echo("\n\N{WARNING SIGN} Deployment tracking interrupted")
            click.echo(f"Deployment '{self.deployment_name}' may still be in progress.")
            click.echo("Run 'jig status' to check current state.")
            raise SystemExit(130) from None

    def process_replica_event(self, replica_id: str, event: ReplicaEvents) -> ReplicaTrackingResult:
        """Process a single replica event and return the tracking result."""
        states = self.printed_states[replica_id]

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
            _fetch_and_print_logs(self.client, self.deployment_name, replica_id)
            return ReplicaTrackingResult.FAILURE

        # Check for stuck in Running state without becoming ready
        if event.replica_status == "Running" and volume_done:
            # replica_wait_start will default to time.time()
            if time.time() - self.replica_wait_start[replica_id] > self.ready_timeout:
                click.echo(
                    f"\N{CROSS MARK}  [{replica_id}] Container is running but "
                    f"not ready to serve requests after {self.ready_timeout} seconds"
                )
                _print_replica_failure(event)
                _fetch_and_print_logs(self.client, self.deployment_name, replica_id)
                click.echo(f"Deployment '{self.deployment_name}' may still be in progress.")
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


# --- Jig class: shared state + operations ---


def _is_not_unique_error(e: APIStatusError) -> bool:
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
    msg = e.body.get("error", "") if isinstance(e.body, dict) else "" # type: ignore
    return "already exists" in msg


# TODO: merge Tracker into Jig


class Jig:
    """Holds Together client, config, and state. Methods implement the core jig operations."""

    def __init__(self, client: Together, config_path: str | None = None) -> None:
        self.together = client
        self.api: JigResource = client.beta.jig
        self.config = Config.find(config_path)
        self.state = State.load(self.config._path.parent, self.config.model_name)

    def _ensure_registry(self) -> None:
        """Ensure registry base path is set in state"""
        if not self.state.registry_base_path:
            response = self.together._client.get("/image-repositories/base-path", headers=self.together.auth_headers)
            response.raise_for_status()
            data = response.json()
            # Strip protocol prefix - Docker tags don't support URLs
            self.state.registry_base_path = data["base-path"].removeprefix("http://").removeprefix("https://")
            self.state.save()

    def _image(self, tag: str = "latest") -> str:
        return f"{self.state.registry_base_path}/{self.config.model_name}:{tag}"

    def _image_with_digest(self, tag: str = "latest") -> str:
        image_name = self._image(tag)
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
        raise RuntimeError(
            f"No registry digest found for {image_name}. Make sure the image was pushed to registry first."
        )

    # == Build / Push / Deploy ==

    def build(self, tag: str = "latest", warmup: bool = False, docker_args: str | None = None) -> None:
        self._ensure_registry()
        image = self._image(tag)

        if _dockerfile(self.config):
            click.echo("\N{CHECK MARK} Generated Dockerfile")
        else:
            click.echo(f"\N{INFORMATION SOURCE} Using existing {self.config.dockerfile} (not managed by jig)")

        click.echo(f"Building {image}")
        cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
        if self.config.dockerfile != "Dockerfile":
            cmd.extend(["-f", self.config.dockerfile])

        extra_args = docker_args or os.getenv("DOCKER_BUILD_EXTRA_ARGS", "")
        if extra_args:
            cmd.extend(shlex.split(extra_args))
        if subprocess.run(cmd).returncode != 0:
            raise RuntimeError("Build failed")

        click.echo("\N{CHECK MARK} Built")

        if warmup:
            _build_warm_image(image)

    def push(self, tag: str = "latest") -> None:
        self._ensure_registry()
        image = self._image(tag)

        registry = self.state.registry_base_path.split("/")[0]
        login_cmd = ["docker", "login", registry, "--username", "user", "--password-stdin"]
        if _run(login_cmd, input=self.together.api_key).returncode != 0:
            raise RuntimeError("Registry login failed")

        click.echo(f"Pushing {image}")
        if subprocess.run(["docker", "push", image]).returncode != 0:
            raise RuntimeError("Push failed")
        click.echo("\N{CHECK MARK} Pushed")

    def _build_deploy_data(self, image: str) -> dict[str, Any]:
        """Build the deployment API payload."""
        deploy_data: dict[str, Any] = {
            "name": self.config.model_name,
            "description": self.config.deploy.description,
            "image": image,
            "min_replicas": self.config.deploy.min_replicas,
            "max_replicas": self.config.deploy.max_replicas,
            "port": self.config.deploy.port,
            "gpu_type": self.config.deploy.gpu_type,
            "gpu_count": self.config.deploy.gpu_count,
            "cpu": self.config.deploy.cpu,
            "memory": self.config.deploy.memory,
            "storage": self.config.deploy.storage,
            "autoscaling": self.config.deploy.autoscaling,
            "termination_grace_period_seconds": self.config.deploy.termination_grace_period_seconds,
            "volumes": [asdict(vm) for vm in self.config.deploy.volume_mounts],
        }

        if self.config.deploy.health_check_path:
            deploy_data["health_check_path"] = self.config.deploy.health_check_path
        if self.config.deploy.command:
            deploy_data["command"] = self.config.deploy.command

        if (base_url := _get_api_base_url(self.together)) != "https://api.together.ai":
            self.config.deploy.environment_variables["TOGETHER_API_BASE_URL"] = base_url

        env_vars = [{"name": k, "value": v} for k, v in self.config.deploy.environment_variables.items()]

        if "TOGETHER_API_KEY" not in self.state.secrets:
            _set_secret(self, "TOGETHER_API_KEY", self.together.api_key, "Auth key for queue API")

        for name, secret_id in self.state.secrets.items():
            env_vars.append({"name": name, "value_from_secret": secret_id})

        deploy_data["environment_variables"] = env_vars
        return deploy_data

    def deploy(
        self,
        tag: str = "latest",
        build_only: bool = False,
        warmup: bool = False,
        detach: bool = False,
        docker_args: str | None = None,
        existing_image: str | None = None,
    ) -> None:
        self._ensure_registry()

        if existing_image:
            deployment_image = existing_image
        else:
            self.build(tag, warmup, docker_args)
            self.push(tag)
            deployment_image = self._image_with_digest(tag)

        if build_only:
            click.echo("\N{CHECK MARK} Build complete (--build-only)")
            return

        deploy_data = self._build_deploy_data(deployment_image)

        if DEBUG:
            click.echo(json.dumps(deploy_data, indent=2))
        click.echo(f"Deploying model: {self.config.model_name}")

        try:
            existing = self.api.retrieve(self.config.model_name)
            old_revision_id = _get_current_revision_id(existing)
            was_scaled_to_zero = existing.ready_replicas == 0
            response = self.api.update(self.config.model_name, **deploy_data)
            click.echo("\N{CHECK MARK}  Applied new deployment configuration")
        except APIStatusError as e:
            if e.status_code != 404:
                raise
            old_revision_id = ""
            was_scaled_to_zero = False
            click.echo("\N{ROCKET} Creating new deployment")
            try:
                response = self.api.deploy(**deploy_data)
                click.echo(f"\N{CHECK MARK} Deployed: {self.config.model_name}")
            except APIStatusError as e:
                if _is_not_unique_error(e):
                    raise RuntimeError(f"Deployment name must be unique. Tip: {self.config._unique_name_tip}") from None
                # TODO: helpful tips for more error cases
                raise

        if detach:
            click.echo(json.dumps(response.model_dump(), indent=2))
            return

        new_revision_id = _get_current_revision_id(response)
        scaling_up = was_scaled_to_zero and response.min_replicas and response.min_replicas > 0
        if old_revision_id and old_revision_id == new_revision_id and not scaling_up:
            return

        Tracker(self.api, self.config.model_name).track_deployment_progress()

    # == Query commands ==

    def status(self, json_output: bool = False) -> None:
        response = self.api.retrieve(self.config.model_name)
        if json_output:
            click.echo(response.model_dump_json(indent=2))
        else:
            click.echo(format_deployment_status(response))

    def endpoint(self) -> None:
        base = _get_api_base_url(self.together)
        click.echo(f"{base}/v1/deployment-request/{self.config.model_name}")

    def logs(self, follow: bool = False) -> None:
        if not follow:
            if lines := self.api.retrieve_logs(self.config.model_name).lines:
                for line in lines:
                    click.echo(line)
            else:
                click.echo("No logs available")
            return

        try:
            with self.api.with_streaming_response.retrieve_logs(self.config.model_name) as stream:
                for line in stream.iter_lines():
                    if line:
                        for log_line in json.loads(line).get("lines", []):
                            click.echo(log_line)
        except KeyboardInterrupt:
            click.echo("\nStopped following logs")
        except Exception as e:
            click.echo(f"\nConnection ended: {e}")

    def destroy(self) -> None:
        self.api.destroy(self.config.model_name)
        click.echo(f"\N{WASTEBASKET} Destroyed {self.config.model_name}")

    def submit(self, prompt: str | None, payload: str | None, watch: bool) -> None:
        """Submit a job and optionally watch for completion."""
        if not prompt and not payload:
            raise click.UsageError("Either --prompt or --payload required")

        raw_response = self.api.queue.with_raw_response.submit(
            model=self.config.model_name,
            payload=json.loads(payload) if payload else {"prompt": prompt},
            priority=1,
        )

        # Raw response due to Stainless limitation with Pydantic aliases
        submit_response = QueueSubmitResponse.model_validate_json(raw_response.read())

        click.echo("\N{CHECK MARK} Submitted job")
        click.echo(submit_response.model_dump_json(indent=2))

        if not watch or not submit_response.request_id:
            return

        click.echo(f"\nWatching job {submit_response.request_id}...")
        last_status: str | None = None
        while True:
            try:
                response = self.api.queue.retrieve(
                    model=self.config.model_name,
                    request_id=submit_response.request_id,
                )
                current_status = response.status
                if current_status != last_status:
                    click.echo(response.model_dump_json(indent=2))
                    last_status = current_status

                if current_status in ["done", "failed", "finished", "error", "canceled"]:
                    if current_status != "done":
                        raise SystemExit(1)
                    return

                time.sleep(1)

            except KeyboardInterrupt:
                click.echo(f"\nStopped watching {submit_response.request_id}")
                raise SystemExit(130) from None

    def job_status(self, request_id: str) -> None:
        response = self.api.queue.retrieve(model=self.config.model_name, request_id=request_id)
        click.echo(response.model_dump_json(indent=2))

    def queue_status(self) -> None:
        response = self.api.queue.with_raw_response.metrics(model=self.config.model_name)
        click.echo(json.dumps(response.json(), indent=2))


# --- CLI Commands ---


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
    pyproject.write_text(content)
    click.echo("\N{CHECK MARK} Created pyproject.toml")
    click.echo("  Edit the configuration and run 'jig deploy'")


@click.command()
@_pass_jig
@_print_errors
def dockerfile(jig: Jig) -> None:
    """Generate Dockerfile"""
    if _dockerfile(jig.config):
        click.echo("\N{CHECK MARK} Generated Dockerfile")
    else:
        msg = f"ERROR: {jig.config.dockerfile} exists and is not managed by jig. Remove or rename the file to allow jig to manage dockerfile."
        click.echo(msg, err=True)


@click.command()
@_pass_jig
@_print_errors
@click.option("--tag", default="latest", help="Image tag")
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option("--docker-args", default=None, help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)")
def build(jig: Jig, tag: str, warmup: bool, docker_args: str | None) -> None:
    """Build container image"""
    jig.build(tag, warmup, docker_args)


@click.command()
@_pass_jig
@_print_errors
@click.option("--tag", default="latest", help="Image tag")
def push(jig: Jig, tag: str) -> None:
    """Push image to registry"""
    jig.push(tag)


@click.command()
@_pass_jig
@_print_errors
@click.option("--tag", default="latest", help="Image tag")
@click.option("--build-only", is_flag=True, help="Build and push only")
@click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")
@click.option("--docker-args", default=None, help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)")
@click.option("--image", "existing_image", default=None, help="Use existing image (skip build/push)")
@click.option("--detach", "detach", is_flag=True, help="Do not wait for deployment to complete")
def deploy(
    jig: Jig,
    tag: str,
    build_only: bool,
    warmup: bool,
    detach: bool,
    docker_args: str | None,
    existing_image: str | None,
) -> None:
    """Deploy model"""
    jig.deploy(tag, build_only, warmup, detach, docker_args, existing_image)


@click.command()
@_pass_jig
@_print_errors
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON")
def status(jig: Jig, json_output: bool = False) -> None:
    """Get deployment status"""
    jig.status(json_output)


@click.command()
@_pass_jig
@_print_errors
def endpoint(jig: Jig) -> None:
    """Get deployment endpoint URL"""
    jig.endpoint()


@click.command()
@_pass_jig
@_print_errors
@click.option("--follow", is_flag=True, help="Follow log output")
def logs(jig: Jig, follow: bool) -> None:
    """Get deployment logs"""
    jig.logs(follow)


@click.command()
@_pass_jig
@_print_errors
def destroy(jig: Jig) -> None:
    """Destroy deployment"""
    jig.destroy()


@click.command()
@_pass_jig
@_print_errors
@click.option("--prompt", default=None, help="Job prompt")
@click.option("--payload", default=None, help="Job payload JSON")
@click.option("--watch", is_flag=True, help="Watch job status until completion")
def submit(jig: Jig, prompt: str | None, payload: str | None, watch: bool) -> None:
    """Submit a job to the deployment"""
    jig.submit(prompt, payload, watch)


@click.command()
@_pass_jig
@_print_errors
@click.option("--request-id", required=True, help="Job request ID")
def job_status(jig: Jig, request_id: str) -> None:
    """Get status of a specific job"""
    jig.job_status(request_id)


@click.command()
@_pass_jig
@_print_errors
def queue_status(jig: Jig) -> None:
    """Get queue metrics for the deployment"""
    jig.queue_status()


@click.command("list")
@handle_api_errors("Jig")  # fixme
@click.pass_context
def list_deployments(ctx: click.Context) -> None:
    """List all deployments"""
    client: JigResource = ctx.obj.beta.jig
    response = client.with_raw_response.list()
    click.echo(json.dumps(response.json(), indent=2))
