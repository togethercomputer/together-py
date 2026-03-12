#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["together @ git+https://github.com/togethercomputer/together-py@next"]
# ///
"""Main jig CLI commands (deploy, build, push, etc.)"""

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
from typing import TYPE_CHECKING, Any, Union, Callable
from pathlib import Path
from datetime import datetime as dt
from functools import wraps, cached_property
from itertools import groupby
from dataclasses import field, asdict, dataclass, is_dataclass
from typing_extensions import override

import click
from click import Context, echo
from click.exceptions import Exit

from together import Together
from together._exceptions import APIError, NotFoundError, AuthenticationError
from together.types.beta.deployment import Deployment
from together.resources.beta.jig.jig import JigResource
from together.lib.cli.api.beta.jig._uploader import Uploader

if TYPE_CHECKING or sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

# managed dockerfile marker - if this is the first line, jig will regenerate the file
DOCKERFILE_MANAGED_MARKER = "# MANAGED BY JIG - Remove this line to prevent jig from overwriting this file"

DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")

WARMUP_ENV_NAME = os.getenv("WARMUP_ENV_NAME", "TORCHINDUCTOR_CACHE_DIR")
WARMUP_DEST = os.getenv("WARMUP_DEST", "torch_cache")

_TRACK_POLL_INTERVAL = 3
_TRACK_TIMEOUT = 600
_TRACK_READY_TIMEOUT = 120


class JigError(Exception):
    """Actionable runtime error"""


# == Configuration ==


@dataclass
class ImageConfig:
    """Container image configuration from pyproject.toml"""

    python_version: str = "3.11"
    # microsoft/pyright#10277 default_factory requirement
    system_packages: list[str] = field(default_factory=list[str])
    environment: dict[str, str] = field(default_factory=dict[str, str])
    run: list[str] = field(default_factory=list[str])
    cmd: str = "python app.py"
    copy: list[str] = field(default_factory=list[str])
    auto_include_git: bool = False
    dockerfile_path: str = "Dockerfile"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImageConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class VolumeMount:
    """Volume mount configuration"""

    name: str
    mount_path: str
    version: int = 0

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
    environment_variables: dict[str, str] = field(default_factory=dict[str, str])
    command: list[str] | None = None
    autoscaling: dict[str, Union[str, float, int]] = field(default_factory=dict[str, Union[str, float, int]])
    health_check_path: str = "/health"
    termination_grace_period_seconds: int = 300
    volume_mounts: list[VolumeMount] = field(default_factory=list[VolumeMount])
    image: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeployConfig:
        cfg = {k: v for k, v in data.items() if k in cls.__annotations__}
        if isinstance((mounts := cfg.get("volume_mounts")), list):
            cfg["volume_mounts"] = [VolumeMount.from_dict(vm) for vm in mounts]  # pyright: ignore
        return cls(**cfg)


def validate(value: Any, value_type: type, path: str = "") -> str | None:
    if value is None:  # toml can't produce None, must be default
        return None
    origin = typing.get_origin(value_type)
    args = typing.get_args(value_type)

    if origin is list:
        if not isinstance(value, list):
            return f"{path}: expected list, got {value!r}"
        for i, v in enumerate(value):  # pyright: ignore
            if err := validate(v, args[0], f"{path}[{i}]"):
                return err
        return None

    if origin is dict:
        if not isinstance(value, dict):
            return f"{path}: expected dict, got {value!r}"
        for k, v in value.items():  # pyright: ignore
            if err := validate(k, args[0], f"{path}.key({k!r})"):
                return err
            if err := validate(v, args[1], f"{path}[{k!r}]"):
                return err
        return None

    if origin is Union or origin is getattr(types, "UnionType", None):
        errs = [validate(value, a, path) for a in args if a is not type(None)]
        if not all(errs):
            return None
        return errs[0] if len(errs) == 1 else f"{path}: expected {value_type}, got {value!r}"

    if is_dataclass(value_type):
        if not isinstance(value, value_type):
            return f"{path}: expected {value_type.__name__}, got {value}"
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
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))
    _unique_name_hint: str = "Update project.name in pyproject.toml"

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
        raise click.UsageError("No pyproject.toml or jig.toml found, use --config to specify a config path")

    @classmethod
    def load(cls, data: dict[str, Any], path: Path) -> Config:
        """Load configuration from parsed TOML data"""
        # figure out config location and "Deployment name must be unique. Tip: update ..." message
        if path.name.endswith("pyproject.toml"):
            jig_config = data.get("tool", {}).get("jig", {})
            if name := jig_config.get("name"):
                hint = "update `name` in your pyproject.toml"
            elif name := data.get("project", {}).get("name", ""):
                hint = "update `project.name` in your pyproject.toml"
            else:
                name = path.resolve().parent.name
                hint = "rename your folder or add `project.name` to your pyproject.toml"
                echo(f"\N{WARNING SIGN} Name not set in {path} - defaulting to {name}")
        else:
            jig_config = data
            if name := jig_config.get("name"):
                hint = f"update `name` in {path}"
            else:
                name = path.resolve().parent.name
                hint = f"rename your folder or add `name` to {path}"
                echo(f"\N{WARNING SIGN} Name not set in {path} - defaulting to {name}")

        # support volume_mounts, autoscaling at jig level (merge into deploy config)
        deploy_config = jig_config.setdefault("deploy", {})
        allow_top_level = ["volume_mounts", "autoscaling"]
        for key in allow_top_level:
            if key in jig_config:
                deploy_config[key] = jig_config[key]
        if autoscaling := deploy_config.get("autoscaling"):
            autoscaling["model"] = name

        return cls(
            image=ImageConfig.from_dict(jig_config.get("image", {})),
            deploy=DeployConfig.from_dict(jig_config.get("deploy", {})),
            model_name=name,
            _path=path,
            _unique_name_hint=hint,
        )


@dataclass
class State:
    """Persistent state stored in .jig.json"""

    _config_dir: Path
    _project_name: str
    _secrets_initialized: bool = False
    registry_base_path: str = ""
    secrets: dict[str, str] = field(default_factory=dict[str, str])

    @classmethod
    def from_dict(cls, config_dir: Path, project_name: str, **data: Any) -> State:
        filtered = {k: v for k, v in data.items() if k in cls.__annotations__ and not k.startswith("_")}
        state = cls(_config_dir=config_dir, _project_name=project_name, **filtered)
        state._secrets_initialized = "secrets" in data
        return state

    @classmethod
    def load(cls, config_dir: Path, project_name: str) -> State:
        """Load state for a specific project from .jig.json

        The state file structure is:
        {
          "project-name-1": {
            "registry_base_path": "...",
            "secrets": {...}
          },
          "project-name-2": {...}
        }
        """
        try:
            all_data = json.loads((config_dir / ".jig.json").read_text())
            # is our project in the nested state format?
            if isinstance(project_data := all_data.get(project_name), dict):
                return cls.from_dict(config_dir, project_name, **project_data)
            # top-level secrets project field is set, but not migrated
            # (don't care about registry base path)
            if "secrets" in all_data:
                return cls.from_dict(config_dir, project_name, **all_data)
            # state exists but our project isn't in it
            return cls(_config_dir=config_dir, _project_name=project_name)
        except FileNotFoundError:
            return cls(_config_dir=config_dir, _project_name=project_name)

    def save(self) -> None:
        """Save state for this project to .jig.json, preserves other projects' state"""
        path = self._config_dir / ".jig.json"

        # load existing file to preserve other projects
        try:
            all_data = json.loads(path.read_text())
        except FileNotFoundError:
            all_data = {}

        # update this project's state
        all_data[self._project_name] = {k: v for k, v in asdict(self).items() if not k.startswith("_")}

        path.write_text(json.dumps(all_data, indent=2))


# == Build ==


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run command and return captured output, raises CalledProcessError on failure"""
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def _files_to_copy(config: Config) -> list[str]:
    """Combine explicitly copied files with git files if requested and valid"""
    files = set(config.image.copy)
    if config.image.auto_include_git:
        try:
            if _run(["git", "status", "--porcelain"]).stdout.strip():
                raise click.UsageError("Git repository has uncommitted changes: auto_include_git not allowed")
            git_files = _run(["git", "ls-files"]).stdout.strip().split("\n")
            files.update(f for f in git_files if f and f != ".")
        except subprocess.CalledProcessError:
            pass

    if "." in files:
        raise click.UsageError("Copying '.' is not allowed. Please enumerate specific files")

    return sorted(files)


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

    copy = "\n".join(f"COPY {file} {file}" for file in _files_to_copy(config))

    # check if .git exists in current directory
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


def _dockerfile(config: Config) -> bool:
    """Generate or update managed Dockerfile, returns False if user-managed"""
    dockerfile_path = Path(config.image.dockerfile_path)
    if not dockerfile_path.exists():
        dockerfile_path.write_text(_generate_dockerfile(config))
        echo("\N{CHECK MARK} Generated Dockerfile")
        return True

    current = dockerfile_path.read_text()
    if not current.startswith(DOCKERFILE_MANAGED_MARKER):
        return False

    suggested = _generate_dockerfile(config)
    if current != suggested:
        dockerfile_path.write_text(suggested)
        echo("\N{CHECK MARK} Updated Dockerfile")
    return True


def _build_warm_image(base_image: str) -> None:
    """Run a warmup container to generate a compile cache, then rebuild with it baked in

    Runs the container with RUN_AND_EXIT=1 which triggers warmup_inputs in sprocket.
    The cache is mounted at /app/torch_cache; the user's code should set the appropriate
    env var (TORCHINDUCTOR_CACHE_DIR, TKCC_OUTPUT_DIR, etc.) to point there.
    """
    cache_dir = Path(WARMUP_DEST)
    # clean any existing cache
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(exist_ok=True)

    echo("\N{FIRE} Running warmup to generate compile cache...")

    # run container with GPU and RUN_AND_EXIT=1
    # mount current dir as /app so warmup_inputs can reference local weights
    # mount cache dir for compile artifacts
    # run as current user so cache files on the bind mount are not owned by root
    cmd = ["docker", "run", "--rm", "--gpus", "all", "--user", f"{os.getuid()}:{os.getgid()}", "-e", "RUN_AND_EXIT=1"]
    cmd.extend(["-e", f"{WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"])
    cmd.extend(["-v", f"{Path.cwd()}:/app"])
    # if MODEL_PRELOAD_PATH is set, also mount that (e.g. ~/.cache/huggingface)
    if weights_path := os.getenv("MODEL_PRELOAD_PATH"):
        cmd.extend(["-v", f"{weights_path}:{weights_path}"])
        cmd.extend(["-e", f"MODEL_PRELOAD_PATH={weights_path}"])
    cmd.append(base_image)

    echo(f"Running: {' '.join(cmd)}")
    if (code := subprocess.run(cmd).returncode) != 0:
        echo(f"\N{FIRE EXTINGUISHER} Warmup failed with code {code}")
        raise Exit(1)

    # check cache was generated
    cache_files = list(cache_dir.rglob("*"))
    if not cache_files:
        echo("\N{FIRE EXTINGUISHER} Warmup completed but no cache files were generated")
        raise Exit(1)

    echo(f"\N{CHECK MARK} Warmup complete, {len(cache_files)} cache files generated")

    # generate cache dockerfile - copy cache to same location used during warmup
    final_dockerfile = f"""FROM {base_image}
COPY {cache_dir.name} /app/{WARMUP_DEST}
ENV {WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"""

    echo("\N{FIRE} Building final image with cache...")
    final_cmd = ["docker", "build", "--platform", "linux/amd64", "-t", base_image, "-f", "-", "."]

    if subprocess.run(final_cmd, input=final_dockerfile, text=True).returncode != 0:
        raise JigError("\N{FIRE EXTINGUISHER} Cache image build failed")
    echo("\N{CHECK MARK} Final image with cache built")


# == Jig ==


def _age(t: str | None) -> str:
    """ISO8601 string to relative age, e.g. '4d11h', max 2 units"""
    try:
        s = int(time.time() - dt.fromisoformat((t or "").replace("Z", "+00:00")).timestamp())
    except ValueError:
        return "-"
    parts: list[str] = []
    for unit, label in [(30 * 86400, "mo"), (86400, "d"), (3600, "h"), (60, "m"), (1, "s")]:
        if s >= unit:
            parts.append(f"{s // unit}{label}")
            s %= unit
    return "".join(parts[:2]) or "0s"


class Jig:
    """Holds Together client, config, and state"""

    def __init__(self, client: Together, config_path: str | None = None) -> None:
        self.together = client
        self.api: JigResource = client.beta.jig
        self._config_path = config_path

    @cached_property
    def config(self) -> Config:
        return Config.find(self._config_path)

    @cached_property
    def name(self) -> str:
        return self.config.model_name

    @cached_property
    def state(self) -> State:
        return State.load(self.config._path.parent, self.name)

    def registry(self) -> str:
        """Get registry and namespace for current user"""
        if not self.state.registry_base_path:
            response = self.together.get("/image-repositories/base-path", cast_to=dict[str, str])
            # strip protocol for docker image format
            self.state.registry_base_path = response["base-path"].split("://", 1)[-1]
            self.state.save()
        return self.state.registry_base_path + "/"

    def image(self, tag: str) -> str:
        return f"{self.registry()}{self.name}:{tag}"

    def image_with_digest(self, tag: str = "latest") -> str:
        image = self.image(tag)
        if tag != "latest":
            return image
        try:
            cmd = ["docker", "inspect", "--format={{json .RepoDigests}}", image]
            if (repo_digests := _run(cmd).stdout.strip()) and repo_digests != "null":
                for digest in json.loads(repo_digests):
                    if digest.startswith(self.registry()):
                        return str(digest)
        except subprocess.CalledProcessError as e:
            msg = e.stderr.strip() if e.stderr else "Docker command failed"
            raise JigError(f"Failed to get digest for {image}: {msg}") from e
        raise JigError(f"No registry digest found for {image}. Make sure the image was pushed to registry first")

    def sync_secrets_from_deployment(self) -> None:
        """Sync remote secrets into local state if secrets have never been tracked.

        On a fresh checkout (no "secrets" key in .jig.json), fetches the deployment's
        env vars from the API and populates state.secrets so they aren't silently
        removed on the next deploy.  Once state has been initialized, it is authoritative.
        """
        if self.state._secrets_initialized:
            return
        try:
            for var in self.api.retrieve(self.name).environment_variables or []:
                if var.value_from_secret:
                    self.state.secrets.setdefault(var.name, var.value_from_secret)
        except NotFoundError:
            pass
        self.state._secrets_initialized = True
        self.state.save()

    def set_secret(self, name: str, value: str, description: str) -> None:
        """Set secret for the deployment (create or update)"""
        self.sync_secrets_from_deployment()
        scoped_name = f"{self.name}-{name}"

        try:
            self.api.secrets.update(id=scoped_name, name=scoped_name, description=description, value=value)
            echo(f"\N{CHECK MARK} Updated secret {name}")
        except NotFoundError:
            self.api.secrets.create(name=scoped_name, value=value, description=description)
            echo(f"\N{CHECK MARK} Created secret {name}")

        self.state.secrets[name] = scoped_name
        self.state.save()

    # == Build / Push / Deploy / Track ==

    def build(self, tag: str = "latest", warmup: bool = False, docker_args: str | None = None) -> None:
        image = self.image(tag)

        if not _dockerfile(self.config):
            echo(f"\N{INFORMATION SOURCE} Using existing {self.config.image.dockerfile_path} (not managed by jig)")

        echo(f"Building {image}")
        cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
        if self.config.image.dockerfile_path != "Dockerfile":
            cmd.extend(["-f", self.config.image.dockerfile_path])

        extra_args = docker_args or os.getenv("DOCKER_BUILD_EXTRA_ARGS", "")
        if extra_args:
            cmd.extend(shlex.split(extra_args))
        if subprocess.run(cmd).returncode != 0:
            raise JigError("Build failed")

        echo("\N{CHECK MARK} Built")

        if warmup:
            _build_warm_image(image)

    def push(self, tag: str = "latest") -> None:
        image = self.image(tag)
        host = self.registry().split("/")[0]
        login_cmd = ["docker", "login", host, "--username", "user", "--password-stdin"]
        if subprocess.run(login_cmd, input=self.together.api_key, text=True).returncode != 0:
            raise JigError("Registry login failed")

        echo(f"Pushing {image}")
        if subprocess.run(["docker", "push", image]).returncode != 0:
            raise JigError("Push failed")
        echo("\N{CHECK MARK} Pushed")

    def deploy(
        self,
        tag: str = "latest",
        build_only: bool = False,
        warmup: bool = False,
        detach: bool = False,
        docker_args: str | None = None,
        existing_image: str | None = None,
    ) -> None:
        if deployment_image := existing_image:
            echo(f"Deploying provided image {deployment_image}")
        elif deployment_image := self.config.deploy.image:
            echo(f"Deploying configured image {deployment_image}")
        else:
            self.build(tag, warmup, docker_args)
            self.push(tag)
            deployment_image = self.image_with_digest(tag)

        if build_only:
            echo("\N{CHECK MARK} Build complete (--build-only)")
            return

        deploy_data: dict[str, Any] = {
            "name": self.name,
            "description": self.config.deploy.description,
            "image": deployment_image,
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

        self.sync_secrets_from_deployment()
        if "TOGETHER_API_KEY" not in self.state.secrets:
            self.set_secret("TOGETHER_API_KEY", self.together.api_key, "Auth key for queue API")

        env_dict = dict(self.config.deploy.environment_variables)
        if self.together.base_url.host not in ("api.together.ai", "api.together.xyz"):
            env_dict["TOGETHER_API_BASE_URL"] = str(self.together.base_url.copy_with(path=""))

        env_list = [{"name": k, "value": v} for k, v in env_dict.items()]
        secret_list = [{"name": k, "value_from_secret": v} for k, v in self.state.secrets.items()]
        deploy_data["environment_variables"] = env_list + secret_list

        if DEBUG:
            echo(json.dumps(deploy_data, indent=2))
        echo(f"Deploying model: {self.name}")

        no_track = False

        try:
            response = self.api.update(self.name, **deploy_data)
            no_track = str(response.status) == "Ready"
            echo("\N{CHECK MARK} Applied new deployment configuration")
        except NotFoundError:
            try:
                response = self.api.deploy(**deploy_data)
                echo(f"\N{CHECK MARK} Deployed: {self.name}")
            except APIError as e:
                if "already exists" in e.message:
                    raise JigError(f"Deployment name must be unique. Tip: {self.config._unique_name_hint}") from None
                raise

        if detach or no_track:
            echo(json.dumps(response.model_dump(), indent=2))
            return

        self.track(response)

    def track(self, d: Deployment) -> None:
        """Poll deployment until first replica ready, failure, or timeout"""
        rev = next(v.value for v in d.environment_variables or [] if v.name == "TOGETHER_DEPLOYMENT_REVISION_ID")
        wait_start: dict[str, float] = {}
        printed: set[str] = set()
        start = time.time()

        if d.min_replicas == 0 and d.desired_replicas == 0 and d.status == "ScaledToZero":
            echo("\N{CHECK MARK} Deployment scaled to zero replicas")
            return

        def once(msg: str, detail: str | None = None) -> None:
            if msg not in printed:
                printed.add(msg)
                echo(f"{msg}\n  {detail}" if detail else msg)

        echo("\N{HOURGLASS WITH FLOWING SAND} Deployment in-progress...")
        try:
            while time.time() - start < _TRACK_TIMEOUT:
                d = self.api.retrieve(self.name)

                for rid, event in (d.replica_events or {}).items():
                    if event.revision_id != rev:
                        continue

                    if event.replica_status == "Running" and event.replica_ready_since:
                        echo(f"""\N{CHECK MARK} [{rid}] Container is running and ready
\N{ROCKET} Deployment successful!
Note: Additional replicas may still be scaling up.""")
                        return

                    if event.replica_status_reason == "CrashLoopBackOff":
                        echo(f"\N{CROSS MARK} [{rid}] Container is crash looping")
                        echo(self.logs(rid))
                        raise Exit(1) from None

                    if event.volume_preload_status:
                        if not event.volume_preload_completed_at:
                            once(f"\N{PACKAGE} [{rid}] Preloading volume contents...")
                            continue
                        once(
                            f"\N{CHECK MARK} [{rid}] Successfully preloaded volume contents. Attaching the volume to the container..."
                        )

                    if event.replica_status_reason:
                        once(
                            f"\N{HOURGLASS WITH FLOWING SAND} [{rid}] {event.replica_status}: {event.replica_status_reason}",
                            event.replica_status_message,
                        )

                    if event.replica_status == "Running":
                        if rid not in wait_start:
                            wait_start[rid] = time.time()
                        if time.time() - wait_start[rid] > _TRACK_READY_TIMEOUT:
                            echo(f"Deployment '{self.name}' may still be in progress.")
                            echo(f"\N{CROSS MARK} [{rid}] Running but not ready after {_TRACK_READY_TIMEOUT}s")
                            echo(self.logs(rid))
                            raise Exit(1) from None

                time.sleep(_TRACK_POLL_INTERVAL)

            echo(f"""\N{CROSS MARK} Deployment tracking timed out after 10 minutes
Deployment '{self.name}' may still be in progress.
Run 'jig status' to check current state.""")
            raise Exit(1)
        except KeyboardInterrupt:
            echo(f"""
\N{WARNING SIGN} Deployment tracking interrupted
Deployment '{self.name}' may still be in progress.
Run 'jig status' to check current state.""")
            raise Exit(130) from None

    # == Query ==

    def logs(self, rid: str | None = None) -> str:
        if not rid:
            return "\n".join(self.api.retrieve_logs(self.name).lines or []) or "No logs available"
        body = "\n".join(self.api.retrieve_logs(self.name, replica_id=rid).lines or [])
        return f"\n--- Logs for {rid} ---\n{body or 'No logs available'}\n--- End of logs ---\n"

    def follow_logs(self) -> None:
        try:
            with self.api.with_streaming_response.retrieve_logs(self.name) as stream:
                for line in stream.iter_lines():
                    if line:
                        log_lines = json.loads(line).get("lines", [])
                        echo("\n".join(log_lines))
        except KeyboardInterrupt:
            echo("\nStopped following logs")
        except (ConnectionError, OSError) as e:
            echo(f"\nConnection ended: {e}")

    def submit(self, prompt: str | None, payload: str | None, watch: bool) -> None:
        """Submit a job and optionally watch for completion"""
        if not prompt and not payload:
            raise click.UsageError("Either --prompt or --payload required")

        body: dict[str, Any] = json.loads(payload) if payload else {"prompt": prompt}  # pyright: ignore
        req = self.api.queue.with_raw_response.submit(model=self.name, payload=body, priority=1)
        raw = typing.cast(dict[str, Any], req.json())

        echo("\N{CHECK MARK} Submitted job")
        echo(json.dumps(raw, indent=2))

        if not watch or not (request_id := raw.get("requestId")):
            return

        echo(f"\nWatching job {request_id}...")
        last_status = raw.get("status")
        while True:
            try:
                response = self.api.queue.retrieve(model=self.name, request_id=request_id)
                if response.status != last_status:
                    echo(response.model_dump_json(indent=2))
                    last_status = response.status
                if response.status in ("done", "finished"):
                    return
                if response.status in ("failed", "error", "canceled"):
                    raise Exit(1)
                time.sleep(1)
            except KeyboardInterrupt:
                echo(f"\nStopped watching {request_id}")
                raise Exit(130) from None

    # == Display ==

    def short_image(self, image: str) -> str:
        """Strip our registry prefix and truncate sha256 digests"""
        name, sep, digest = image.removeprefix(self.registry()).partition("sha256:")
        return f"{name}{sep}{digest[:8]}"

    def format_status(self, d: Deployment) -> str:
        """Format deployment status for CLI display"""
        image = self.short_image(d.image or "-")
        lines = [
            f"""App:
  Name    : {d.name} ┃ ID: {d.id}
  Image   : {image}
  Status  : {d.status}
  Created : {_age(d.created_at)} ┃ Updated : {_age(d.updated_at)}"""
        ]

        if a := d.autoscaling:
            lines.append(f"  Autoscaling: {a.metric or 'N/A'} {a.target or 'N/A'} (target)")
        lines.append(f"""  Replicas: {d.ready_replicas}/{d.desired_replicas} ready (min {d.min_replicas}, max {d.max_replicas})

Configuration:""")
        if d.gpu_count and d.gpu_type:
            lines.append(f"  GPU: {d.gpu_count}x {d.gpu_type}")
        vol = d.volumes[0] if d.volumes else None
        lines.append(f"  Volume: {vol.name} \N{RIGHTWARDS ARROW} {vol.mount_path}" if vol else "  Volume: (none)")
        storage = f" ┃ {d.storage}GB Storage" if d.storage else ""
        lines.append(f"  Resources: {d.cpu} core CPU ┃ {d.memory}GB Memory{storage}")

        if d.command:
            lines.append(f"  Command: {d.command}")
        if d.args:
            lines.append(f"  Args: {d.args}")
        if d.port != 8000:
            lines.append(f"  Port: {d.port}")
        if d.health_check_path:
            lines.append(f"  Health Check Path: {d.health_check_path}")

        all_env = d.environment_variables or []
        if secret_list := [e for e in all_env if e.value_from_secret]:
            lines.append(f"  Secrets: {', '.join(s.name for s in secret_list)}")
        if env_list := [e for e in all_env if e.value and e.name != "TOGETHER_DEPLOYMENT_REVISION_ID"]:
            lines += ["  Environment Variables:", "    NAME                                     VALUE"]
            lines += [f"    {e.name:<40} {e.value}" for e in env_list]
        if d.replica_events:
            sorted_replicas = sorted(d.replica_events.items(), key=lambda item: item[1].image or "-", reverse=True)
            lines += ["", "Replica Events:"]
            for image, group in groupby(sorted_replicas, key=lambda item: item[1].image or "-"):
                lines.append(f"{self.short_image(image)}:")
                for rid, r in group:
                    if r.volume_preload_status and not r.volume_preload_completed_at:
                        lines.append(f"  {rid}: Volume Preloading")
                    elif r.replica_status == "Running" and r.replica_ready_since:
                        lines.append(f"  {rid}: Running, ready {_age(r.replica_ready_since)}")
                    else:
                        lines.append(f"  {rid}: {r.replica_status}")

        return "\n".join(lines) + "\n"


# == CLI ==


class JigGroup(click.Group):
    """Click groups stop at the first non-option token (the subcommand), so
    `jig --config foo deploy` would fail — --config is a per-command option, not
    a group option. We move it past the subcommand before parsing."""

    @override
    def parse_args(self, ctx: Context, args: list[str]) -> list[str]:
        args = list(args)
        for i, arg in enumerate(args):
            if arg in ("-c", "--config") and i + 1 < len(args):
                # move flag + value to end: [--config, foo, deploy, ...] -> [deploy, ..., --config, foo]
                args.extend([args.pop(i), args.pop(i)])
                break
        return super().parse_args(ctx, args)


def _command(f: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap command: create Jig from context, catch errors, display return values"""

    @click.pass_context
    @click.option("-c", "--config", "config_path", default=None, help="Configuration file path")
    @wraps(f)
    def wrapper(ctx: Context, config_path: str | None, *args: Any, **kwargs: Any) -> None:
        try:
            result = f(Jig(ctx.obj, config_path), *args, **kwargs)
        except (Exit, click.Abort, click.ClickException):
            raise
        except AuthenticationError:
            msg = "Invalid or missing API key. Set TOGETHER_API_KEY or use --api-key."
        except APIError as e:
            body = e.body
            if isinstance(body, dict):
                err = body.get("error", body)  # type: ignore
                msg = str(err) if isinstance(err, str) else str(err.get("message", err))  # type: ignore
            else:
                msg = e.message
        except JigError as e:
            msg = str(e)
        except Exception as e:
            if DEBUG:
                raise
            msg = f"Unexpected error: {e}"
        else:
            if result is not None:
                echo(result if isinstance(result, str) else json.dumps(result.json(), indent=2))
            return
        prefix = click.style("Jig: ", fg="blue")
        echo(prefix + click.style("Failed", fg="red"), err=True)
        echo(prefix + click.style(msg, fg="red"), err=True)
        raise Exit(1) from None

    return wrapper


@click.group(cls=JigGroup)
@click.pass_context
def jig(ctx: Context) -> None:
    """Deploy and manage containers on Together AI"""
    if ctx.obj is None:
        ctx.obj = Together()


def _jig_command(f: Callable[..., Any]) -> click.Command:
    return jig.command()(_command(f))


@jig.command()
def init() -> None:
    """Initialize jig configuration"""
    if (pyproject := Path("pyproject.toml")).exists():
        echo("pyproject.toml already exists")
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
    echo("""\N{CHECK MARK} Created pyproject.toml
  Edit the configuration and run 'jig deploy'""")


@_jig_command
def dockerfile(jig: Jig) -> None:
    """Generate Dockerfile"""
    if not _dockerfile(jig.config):
        msg = f"{jig.config.image.dockerfile_path} exists and is not managed by jig. Remove or rename the file to allow jig to manage dockerfile."
        raise JigError(msg)


_tag_option = click.option("--tag", default="latest", help="Image tag")


def _build_options(f: Callable[..., Any]) -> Callable[..., Any]:
    f = click.option(
        "--docker-args", default=None, help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)"
    )(f)
    f = click.option("--warmup", is_flag=True, help="Run warmup to build torch compile cache")(f)
    return _tag_option(f)


@_jig_command
@_build_options
def build(jig: Jig, tag: str, warmup: bool, docker_args: str | None) -> None:
    """Build container image"""
    jig.build(tag, warmup, docker_args)


@_jig_command
@_tag_option
def push(jig: Jig, tag: str) -> None:
    """Push image to registry"""
    jig.push(tag)


@_jig_command
@_build_options
@click.option("--build-only", is_flag=True, help="Build and push only")
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


@_jig_command
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON")
def status(jig: Jig, json_output: bool = False) -> Any:
    """Get deployment status"""
    raw = jig.api.with_raw_response.retrieve(jig.name)
    if json_output:
        return raw
    return jig.format_status(raw.parse())


@_jig_command
def endpoint(jig: Jig) -> str:
    """Get deployment endpoint URL"""
    return f"https://api.together.ai/v1/deployment-request/{jig.name}"


@_jig_command
@click.option("--follow", is_flag=True, help="Follow log output")
def logs(jig: Jig, follow: bool) -> str | None:
    """Get deployment logs"""
    return jig.follow_logs() if follow else jig.logs()


@_jig_command
def destroy(jig: Jig) -> str:
    """Destroy deployment"""
    jig.api.destroy(jig.name)
    return f"\N{WASTEBASKET} Destroyed {jig.name}"


@_jig_command
@click.option("--prompt", default=None, help="Job prompt")
@click.option("--payload", default=None, help="Job payload JSON")
@click.option("--watch", is_flag=True, help="Watch job status until completion")
def submit(jig: Jig, prompt: str | None, payload: str | None, watch: bool) -> None:
    """Submit a job to the deployment"""
    jig.submit(prompt, payload, watch)


@_jig_command
@click.option("--request-id", required=True, help="Job request ID")
def job_status(jig: Jig, request_id: str) -> Any:
    """Get status of a specific job"""
    return jig.api.queue.with_raw_response.retrieve(model=jig.name, request_id=request_id)


@_jig_command
def queue_status(jig: Jig) -> Any:
    """Get queue metrics for the deployment"""
    return jig.api.queue.with_raw_response.metrics(model=jig.name)


@jig.command("list")
@_command
def list_deployments(jig: Jig) -> Any:
    """List all deployments"""
    return jig.api.with_raw_response.list()


# -- Secrets --


@jig.group()
def secrets() -> None:
    """Manage deployment secrets"""


@secrets.command("set")
@_command
@click.option("--name", required=True, help="Secret name")
@click.option("--value", required=True, help="Secret value")
@click.option("--description", default="", help="Secret description")
def secrets_set(jig: Jig, name: str, value: str, description: str) -> None:
    """Set a secret (create or update)"""
    jig.set_secret(name, value, description)


@secrets.command("unset")
@_command
@click.option("--name", required=True, help="Secret name to remove")
def secrets_unset(jig: Jig, name: str) -> None:
    """Remove a secret from local state"""
    jig.sync_secrets_from_deployment()
    try:
        del jig.state.secrets[name]
        jig.state.save()
        echo(f"\N{CHECK MARK} Deleted secret {name}")
    except KeyError:
        echo(f"\N{CROSS MARK} Secret {name} is not set")


@secrets.command("list")
@_command
def secrets_list(jig: Jig) -> None:
    """List all secrets with sync status"""
    prefix = f"{jig.name}-"

    local_secrets = set(jig.state.secrets.keys())
    remote_secrets: set[str] = set()
    # get all remote secrets then filter for this deployment
    for secret in jig.api.secrets.list().data or []:
        if (name := secret.name) and name.startswith(prefix):
            # strip prefix to get local name
            remote_secrets.add(name.removeprefix(prefix))

    if not local_secrets and not remote_secrets:
        echo(f"\N{INFORMATION SOURCE} No secrets configured for deployment {jig.name}")
        return

    echo(f"\N{INFORMATION SOURCE} Secrets for deployment {jig.name}:\n")

    for name in sorted(local_secrets | remote_secrets):
        in_local = name in local_secrets
        in_remote = name in remote_secrets

        if in_local and in_remote:
            status = click.style("synced", fg="green")
        elif in_local:
            status = click.style("local only", fg="yellow")
        else:
            status = click.style("remote only", fg="yellow")

        echo(f"  - {name} [{status}]")


# -- Volumes --


@jig.group()
def volumes() -> None:
    """Manage volumes"""


_volume_name_option = click.option("--name", required=True, help="Volume name")


_source_dir = click.Path(exists=True, file_okay=False, path_type=Path)


@volumes.command("create")
@_command
@_volume_name_option
@click.option("--source", required=True, type=_source_dir, help="Source directory path")
def volumes_create(jig: Jig, name: str, source: Path) -> None:
    """Create a volume and upload files"""
    source_prefix = f"{name}/0"

    echo(f"\N{ROCKET} Creating volume {name} with source prefix {source_prefix}")
    try:
        volume = jig.api.volumes.create(
            name=name, type="readOnly", content={"type": "files", "source_prefix": source_prefix}
        )
        echo(f"\N{CHECK MARK} Volume created: {volume.id}")
    except APIError as e:
        if "already exists" in e.message:
            raise JigError(f"Volume {name} already exists, use 'jig volumes update' instead") from None
        raise JigError(f"Failed to create volume: {e}") from e

    try:
        asyncio.run(Uploader(jig.together).upload_files(source, source_prefix))
    except Exception as e:
        echo(f"\N{CROSS MARK} Upload failed: {e}")
        echo(f"\N{WASTEBASKET} Cleaning up volume {name}")
        try:
            jig.api.volumes.delete(name)
        except Exception as cleanup_error:
            echo(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        raise Exit(1) from None


@volumes.command("update")
@_command
@_volume_name_option
@click.option("--source", required=True, type=_source_dir, help="New source directory path")
def volumes_update(jig: Jig, name: str, source: Path) -> None:
    """Update a volume and re-upload files"""
    try:
        volume_data = jig.api.volumes.with_raw_response.retrieve(name).json()
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None

    new_version = int(volume_data.get("current_version", 0)) + 1  # type: ignore
    remote_prefix = f"{name}/{new_version}"

    echo(f"\N{INFORMATION SOURCE} Uploading files for volume {name}")
    asyncio.run(Uploader(jig.together).upload_files(source, remote_prefix))

    echo(f"\N{INFORMATION SOURCE} Updating volume {name}, version {new_version} from {source}")
    jig.api.volumes.update(name, content={"type": "files", "source_prefix": remote_prefix})
    echo("\N{CHECK MARK} Volume updated successfully")


@volumes.command("delete")
@_command
@_volume_name_option
def volumes_delete(jig: Jig, name: str) -> None:
    """Delete a volume"""
    try:
        jig.api.volumes.delete(name)
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None
    echo(f"\N{CHECK MARK} Deleted volume {name}")


@volumes.command("describe")
@_command
@_volume_name_option
def volumes_describe(jig: Jig, name: str) -> Any:
    """Describe a volume"""
    try:
        return jig.api.volumes.with_raw_response.retrieve(name)
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None


@volumes.command("list")
@_command
def volumes_list(jig: Jig) -> Any:
    """List all volumes"""
    return jig.api.volumes.with_raw_response.list()


if __name__ == "__main__":
    jig()
