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
import concurrent.futures
from typing import TYPE_CHECKING, Any, Union, Callable, Optional, Annotated
from pathlib import Path
from datetime import datetime as dt
from functools import cached_property
from itertools import groupby
from dataclasses import field, asdict, dataclass, is_dataclass

import httpx
from cyclopts import Parameter

from together import Together
from together._exceptions import APIError, NotFoundError, AuthenticationError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.types.beta.deployment import Deployment
from together.lib.cli.utils._console import console
from together.resources.beta.jig.jig import JigResource
from together.lib.cli.components.list import ListTable
from together.lib.cli.api.beta.jig._uploader import Uploader
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

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
            raise e
            # TODO:
            # raise click.UsageError(f"Invalid volume mount {data}: {e}") from None


@dataclass
class DeployConfig:
    """Deployment configuration"""

    description: str = ""
    gpu_type: str = "h100-80gb"
    gpu_count: int = 1
    cpu: Union[int, float] = 1
    memory: Union[int, float] = 8
    storage: int = 100
    min_replicas: int = 1
    max_replicas: int = 1
    port: int = 8000
    environment_variables: dict[str, str] = field(default_factory=dict[str, str])
    command: list[str] = field(default_factory=list[str])
    autoscaling: dict[str, Union[str, float, int]] = field(default_factory=dict[str, Union[str, float, int]])
    health_check_path: str = "/health"
    termination_grace_period_seconds: int = 300
    volume_mounts: list[VolumeMount] = field(default_factory=list[VolumeMount])
    image: Optional[str] = None

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

    union_type = getattr(types, "UnionType", None)
    if origin is Union or (union_type is not None and origin is union_type):
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
class JigConfig:
    """Main configuration from jig.toml or pyproject.toml"""

    model_name: str = ""
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))
    _unique_name_hint: str = "Update project.name in pyproject.toml"

    def __post_init__(self) -> None:
        if err := validate(self, type(self)):
            raise JigError(f"Invalid {self._path}: {err}")

    @classmethod
    def find(cls, config_path: str | None = None, init: bool = False) -> JigConfig:
        """Find specified config_path, pyproject.toml, or jig.toml"""
        if config_path:
            found_path = Path(config_path)
            if not found_path.exists():
                raise JigError(f"Configuration file not found: {config_path}")
            return cls.load(tomllib.loads(found_path.read_text()), found_path)

        if (jigfile := Path("jig.toml")).exists():
            return cls.load(tomllib.loads(jigfile.read_text()), jigfile)

        if (pyproject_path := Path("pyproject.toml")).exists():
            data = tomllib.loads(pyproject_path.read_text())
            if "tool" in data and "jig" in data["tool"]:
                return cls.load(data, pyproject_path)

        if init:
            return cls()
        raise JigError("No pyproject.toml or jig.toml found, use --config to specify a config path")

    @classmethod
    def load(cls, data: dict[str, Any], path: Path) -> JigConfig:
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
                console.print(f"\N{WARNING SIGN} Name not set in {path} - defaulting to {name}")
        else:
            jig_config = data
            if name := jig_config.get("name"):
                hint = f"update `name` in {path}"
            else:
                name = path.resolve().parent.name
                hint = f"rename your folder or add `name` to {path}"
                console.print(f"\N{WARNING SIGN} Name not set in {path} - defaulting to {name}")

        # support volume_mounts, autoscaling at jig level (merge into deploy config)
        deploy_config = jig_config.setdefault("deploy", {})
        allow_top_level = ["volume_mounts", "autoscaling"]
        for key in allow_top_level:
            if key in jig_config:
                console.print(
                    f"\N{WARNING SIGN} [tool.jig.{key}] is deprecated, use [tool.jig.deploy.{key}] instead",
                )
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


Config = JigConfig


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


def _files_to_copy(config: JigConfig) -> list[str]:
    """Combine explicitly copied files with git files if requested and valid"""
    files = set(config.image.copy)
    if config.image.auto_include_git:
        try:
            if _run(["git", "status", "--porcelain"]).stdout.strip():
                raise JigError("Git repository has uncommitted changes: auto_include_git not allowed")
            git_files = _run(["git", "ls-files"]).stdout.strip().split("\n")
            files.update(f for f in git_files if f and f != ".")
        except subprocess.CalledProcessError:
            pass

    if "." in files:
        raise JigError("Copying '.' is not allowed. Please enumerate specific files")

    return sorted(files)


def _generate_dockerfile(config: JigConfig) -> str:
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

    pip = ""
    if Path("pyproject.toml").exists():
        pip = """COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \\
    uv pip install --system --compile-bytecode . && \\
    (python -c "import sprocket" 2>/dev/null || (echo "sprocket not found in pyproject.toml, installing from pypi.together.ai..." && uv pip install --system --extra-index-url https://pypi.together.ai/ sprocket))
"""

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
{pip}

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


def _dockerfile(config: JigConfig) -> bool:
    """Generate or update managed Dockerfile, returns False if user-managed"""
    dockerfile_path = Path(config.image.dockerfile_path)
    if not dockerfile_path.exists():
        dockerfile_path.write_text(_generate_dockerfile(config))
        console.print("\N{CHECK MARK} Generated Dockerfile")
        return True

    current = dockerfile_path.read_text()
    if not current.startswith(DOCKERFILE_MANAGED_MARKER):
        return False

    suggested = _generate_dockerfile(config)
    if current != suggested:
        dockerfile_path.write_text(suggested)
        console.print("\N{CHECK MARK} Updated Dockerfile")
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

    console.print("\N{FIRE} Running warmup to generate compile cache...")

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

    console.print(f"Running: {' '.join(cmd)}")
    if (code := subprocess.run(cmd).returncode) != 0:
        console.print(f"\N{FIRE EXTINGUISHER} Warmup failed with code {code}")
        sys.exit(1)
        # TODO:
        # raise Exit(1)

    # check cache was generated
    cache_files = list(cache_dir.rglob("*"))
    if not cache_files:
        console.print("\N{FIRE EXTINGUISHER} Warmup completed but no cache files were generated")
        sys.exit(1)
        # TODO:
        # raise Exit(1)

    console.print(f"\N{CHECK MARK} Warmup complete, {len(cache_files)} cache files generated")

    # generate cache dockerfile - copy cache to same location used during warmup
    final_dockerfile = f"""FROM {base_image}
COPY {cache_dir.name} /app/{WARMUP_DEST}
ENV {WARMUP_ENV_NAME}=/app/{WARMUP_DEST}"""

    console.print("\N{FIRE} Building final image with cache...")
    final_cmd = ["docker", "build", "--platform", "linux/amd64", "-t", base_image, "-f", "-", "."]

    if subprocess.run(final_cmd, input=final_dockerfile, text=True).returncode != 0:
        raise JigError("\N{FIRE EXTINGUISHER} Cache image build failed")
    console.print("\N{CHECK MARK} Final image with cache built")


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
    def config(self) -> JigConfig:
        return JigConfig.find(self._config_path)

    @cached_property
    def name(self) -> str:
        return self.config.model_name

    @cached_property
    def state(self) -> State:
        return State.load(self.config._path.parent, self.name)

    def registry(self) -> str:
        """Get registry and namespace for current user"""
        if not self.state.registry_base_path:
            res = self.together.get("/image-repositories/base-path", cast_to=httpx.Response)
            response = res.json()
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
            console.print(f"\N{CHECK MARK} Updated secret {name}")
        except NotFoundError:
            self.api.secrets.create(name=scoped_name, value=value, description=description)
            console.print(f"\N{CHECK MARK} Created secret {name}")

        self.state.secrets[name] = scoped_name
        self.state.save()

    def delete_secret(self, name: str) -> None:
        """Delete a secret and unset it locally"""
        scoped_name = f"{self.name}-{name}"

        try:
            self.api.secrets.delete(id=scoped_name)
            console.print(f"\N{CHECK MARK} Deleted secret {name}")
        except NotFoundError:
            console.print(f"\N{CROSS MARK} Secret {name} not found")

        if name in self.state.secrets:
            del self.state.secrets[name]
            self.state.save()

    # == Build / Push / Deploy / Track ==

    def build(self, tag: str = "latest", warmup: bool = False, docker_args: str | None = None) -> None:
        image = self.image(tag)

        if not _dockerfile(self.config):
            console.print(
                f"\N{INFORMATION SOURCE} Using existing {self.config.image.dockerfile_path} (not managed by jig)"
            )

        console.print(f"Building {image}")
        cmd = ["docker", "build", "--platform", "linux/amd64", "-t", image, "."]
        if self.config.image.dockerfile_path != "Dockerfile":
            cmd.extend(["-f", self.config.image.dockerfile_path])

        extra_args = docker_args or os.getenv("DOCKER_BUILD_EXTRA_ARGS", "")
        if extra_args:
            cmd.extend(shlex.split(extra_args))
        if subprocess.run(cmd).returncode != 0:
            raise JigError("Build failed")

        console.print("\N{CHECK MARK} Built")

        if warmup:
            _build_warm_image(image)

    def push(self, tag: str = "latest") -> None:
        image = self.image(tag)
        host = self.registry().split("/")[0]
        login_cmd = ["docker", "login", host, "--username", "user", "--password-stdin"]
        if subprocess.run(login_cmd, input=self.together.api_key, text=True).returncode != 0:
            raise JigError("Registry login failed")

        console.print(f"Pushing {image}")
        if subprocess.run(["docker", "push", image]).returncode != 0:
            raise JigError("Push failed")
        console.print("\N{CHECK MARK} Pushed")

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
            console.print(f"Deploying provided image {deployment_image}")
        elif deployment_image := self.config.deploy.image:
            console.print(f"Deploying configured image {deployment_image}")
        else:
            self.build(tag, warmup, docker_args)
            self.push(tag)
            deployment_image = self.image_with_digest(tag)

        if build_only:
            console.print("\N{CHECK MARK} Build complete (--build-only)")
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
            console.print(json.dumps(deploy_data, indent=2))
        console.print(f"Deploying model: {self.name}")

        no_track = False

        try:
            response = self.api.update(self.name, **deploy_data)
            no_track = str(response.status) == "Ready"
            console.print("\N{CHECK MARK} Applied new deployment configuration")
        except NotFoundError:
            try:
                response = self.api.deploy(**deploy_data)
                console.print(f"\N{CHECK MARK} Deployed: {self.name}")
            except APIError as e:
                if "already exists" in e.message:
                    raise JigError(f"Deployment name must be unique. Tip: {self.config._unique_name_hint}") from None
                raise

        if detach or no_track:
            console.print(json.dumps(response.model_dump(), indent=2))
            return

        self.track(response)

    def track(self, d: Deployment) -> None:
        """Poll deployment until first replica ready, failure, or timeout"""
        rev = next(v.value for v in d.environment_variables or [] if v.name == "TOGETHER_DEPLOYMENT_REVISION_ID")
        wait_start: dict[str, float] = {}
        printed: set[str] = set()
        start = time.time()

        if d.min_replicas == 0 and d.desired_replicas == 0 and d.status == "ScaledToZero":
            console.print("\N{CHECK MARK} Deployment scaled to zero replicas")
            return

        def once(msg: str, detail: str | None = None) -> None:
            if msg not in printed:
                printed.add(msg)
                console.print(f"{msg}\n  {detail}" if detail else msg)

        console.print("\N{HOURGLASS WITH FLOWING SAND} Deployment in-progress...")
        try:
            while time.time() - start < _TRACK_TIMEOUT:
                d = self.api.retrieve(self.name)

                for rid, event in (d.replica_events or {}).items():
                    if event.revision_id != rev:
                        continue

                    if event.replica_status == "Running" and event.replica_ready_since:
                        console.print(f"""\N{CHECK MARK} [{rid}] Container is running and ready
\N{ROCKET} Deployment successful!
Note: Additional replicas may still be scaling up.""")
                        return

                    if event.replica_status_reason == "CrashLoopBackOff":
                        console.print(f"\N{CROSS MARK} [{rid}] Container is crash looping")
                        console.print(self.logs(rid))
                        sys.exit(1)
                        # raise Exit(1) from None

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
                            console.print(f"Deployment '{self.name}' may still be in progress.")
                            console.print(f"\N{CROSS MARK} [{rid}] Running but not ready after {_TRACK_READY_TIMEOUT}s")
                            console.print(self.logs(rid))
                            sys.exit(1)
                            # raise Exit(1) from None

                time.sleep(_TRACK_POLL_INTERVAL)

            console.print(f"""\N{CROSS MARK} Deployment tracking timed out after 10 minutes
Deployment '{self.name}' may still be in progress.
Run 'jig status' to check current state.""")
            sys.exit(1)
            # raise Exit(1) from None
        except KeyboardInterrupt:
            console.print(f"""
\N{WARNING SIGN} Deployment tracking interrupted
Deployment '{self.name}' may still be in progress.
Run 'jig status' to check current state.""")
            sys.exit(130)
            # raise Exit(130) from None

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
                        console.print("\n".join(log_lines))
        except KeyboardInterrupt:
            console.print("\nStopped following logs")
        except (ConnectionError, OSError) as e:
            console.print(f"\nConnection ended: {e}")

    def submit(self, prompt: str | None, payload: str | None, watch: bool) -> None:
        """Submit a job and optionally watch for completion"""
        if not prompt and not payload:
            raise JigError("Either --prompt or --payload required")

        body: dict[str, Any] = json.loads(payload) if payload else {"prompt": prompt}  # pyright: ignore
        req = self.api.queue.with_raw_response.submit(model=self.name, payload=body, priority=1)
        raw = typing.cast(dict[str, Any], req.json())

        console.print("\N{CHECK MARK} Submitted job")
        console.print(json.dumps(raw, indent=2))

        if not watch or not (request_id := raw.get("requestId")):
            return

        console.print(f"\nWatching job {request_id}...")
        last_status = raw.get("status")
        while True:
            try:
                response = self.api.queue.retrieve(model=self.name, request_id=request_id)
                if response.status != last_status:
                    console.print(response.model_dump_json(indent=2))
                    last_status = response.status
                if response.status in ("done", "finished"):
                    return
                if response.status in ("failed", "error", "canceled"):
                    sys.exit(1)
                    # raise Exit(1) from None
                time.sleep(1)
            except KeyboardInterrupt:
                console.print(f"\nStopped watching {request_id}")
                sys.exit(130)
                # raise Exit(130) from None

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
  Created : {_age(d.created_at.isoformat() if d.created_at else None)} ┃ Updated : {_age(d.updated_at.isoformat() if d.updated_at else None)}"""
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

TomlConfigParameter = Annotated[
    Optional[str],
    Parameter(name=["-c", "--config"], help="Configuration file path"),
]


def _sync_together_from_config(config: CLIConfig) -> Together:
    return Together(
        api_key=config.client.api_key,
        base_url=str(config.client.base_url),
        timeout=config.client.timeout,
        max_retries=config.client.max_retries,
    )


def _print_cli_result(result: Any) -> None:
    if result is None:
        return
    if isinstance(result, str):
        console.print(result)
    elif hasattr(result, "json") and callable(result.json):
        console.print(json.dumps(result.json(), indent=2))
    else:
        console.print(str(result))


def _jig_fail(msg: str) -> None:
    console.print(f"[blue]Jig:[/blue] [red]Failed[/red] {msg}")
    sys.exit(1)


def _asyncio_run_upload(coro: typing.Coroutine[typing.Any, typing.Any, None]) -> None:
    """Run async upload; safe when an event loop is already running (e.g. Cyclopts async launcher)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
    else:

        def _run_in_thread() -> None:
            asyncio.run(coro)

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(_run_in_thread).result()


def _api_error_message(e: APIError) -> str:
    body = e.body
    if isinstance(body, dict):
        err = body.get("error", body)  # type: ignore[assignment]
        return str(err) if isinstance(err, str) else str(err.get("message", err))  # type: ignore[union-attr]
    return e.message


def _run_jig_cmd(config: CLIConfig, config_path: str | None, fn: Callable[[Jig], Any]) -> None:
    try:
        jig = Jig(_sync_together_from_config(config), config_path)
        result = fn(jig)
        _print_cli_result(result)
    except (KeyboardInterrupt, SystemExit):
        raise
    except AuthenticationError:
        _jig_fail("Invalid or missing API key. Set TOGETHER_API_KEY or use --api-key.")
    except APIError as e:
        _jig_fail(_api_error_message(e))
    except JigError as e:
        _jig_fail(str(e))
    except Exception as e:
        if DEBUG:
            raise
        _jig_fail(f"Unexpected error: {e}")


def init(
    *,
    config: CLIConfigParameter,
) -> None:
    """Initialize jig configuration."""
    _ = config
    if (pyproject := Path("pyproject.toml")).exists():
        console.print("pyproject.toml already exists")
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
    console.print("""\N{CHECK MARK} Created pyproject.toml
  Edit the configuration and run 'jig deploy'""")


def dockerfile(jig: Jig) -> None:
    """Generate Dockerfile"""
    if not _dockerfile(jig.config):
        msg = f"{jig.config.image.dockerfile_path} exists and is not managed by jig. Remove or rename the file to allow jig to manage dockerfile."
        raise JigError(msg)


def build(jig: Jig, tag: str, warmup: bool, docker_args: str | None) -> None:
    """Build container image"""
    jig.build(tag, warmup, docker_args)


def push(jig: Jig, tag: str) -> None:
    """Push image to registry"""
    jig.push(tag)


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


def status(jig: Jig, json_output: bool = False) -> Any:
    """Get deployment status"""
    raw = jig.api.with_raw_response.retrieve(jig.name)
    if json_output:
        return raw
    return jig.format_status(raw.parse())


def endpoint(jig: Jig) -> str:
    """Get deployment endpoint URL"""
    return f"https://api.together.ai/v1/deployment-request/{jig.name}"


def logs(jig: Jig, follow: bool) -> str | None:
    """Get deployment logs"""
    return jig.follow_logs() if follow else jig.logs()


def destroy(jig: Jig) -> str:
    """Destroy deployment"""
    jig.api.destroy(jig.name)
    return f"\N{WASTEBASKET} Destroyed {jig.name}"


def submit(jig: Jig, prompt: str | None, payload: str | None, watch: bool) -> None:
    """Submit a job to the deployment"""
    jig.submit(prompt, payload, watch)


def job_status(jig: Jig, request_id: str) -> Any:
    """Get status of a specific job"""
    return jig.api.queue.with_raw_response.retrieve(model=jig.name, request_id=request_id)


def queue_status(jig: Jig) -> Any:
    """Get queue metrics for the deployment"""
    return jig.api.queue.with_raw_response.metrics(model=jig.name)


def list_deployments(jig: Jig) -> Any:
    """List all deployments"""
    return jig.api.with_raw_response.list()


def secrets_set(jig: Jig, name: str, value: str, description: str) -> None:
    """Set a secret (create or update)"""
    jig.set_secret(name, value, description)


def secrets_unset(jig: Jig, name: str) -> None:
    """Remove a secret from local state"""
    jig.sync_secrets_from_deployment()
    try:
        del jig.state.secrets[name]
        jig.state.save()
        console.print(f"\N{CHECK MARK} Removed secret {name} from the deployment")
    except KeyError:
        console.print(f"\N{CROSS MARK} Secret {name} is not set")


def secrets_delete(jig: Jig, name: str) -> None:
    """Delete a secret and unset it locally"""
    jig.delete_secret(name)


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
        console.print(f"\N{INFORMATION SOURCE} No secrets configured for deployment {jig.name}")
        return

    console.print(f"\N{INFORMATION SOURCE} Secrets for deployment {jig.name}:\n")

    for name in sorted(local_secrets | remote_secrets):
        in_local = name in local_secrets
        in_remote = name in remote_secrets

        if in_local and in_remote:
            status = "[green]synced[/green]"
        elif in_local:
            status = "[yellow]local only[/yellow]"
        else:
            status = "[yellow]remote only[/yellow]"

        console.print(f"  - {name} [{status}]")


def volumes_create(jig: Jig, name: str, source: Path) -> None:
    """Create a volume and upload files"""
    source_prefix = f"{name}/0"

    console.print(f"\N{ROCKET} Creating volume {name} with source prefix {source_prefix}")
    try:
        volume = jig.api.volumes.create(
            name=name, type="readOnly", content={"type": "files", "source_prefix": source_prefix}
        )
        console.print(f"\N{CHECK MARK} Volume created: {volume.id}")
    except APIError as e:
        if "already exists" in e.message:
            raise JigError(f"Volume {name} already exists, use 'jig volumes update' instead") from None
        raise JigError(f"Failed to create volume: {e}") from e

    try:
        _asyncio_run_upload(Uploader(jig.together).upload_files(source, source_prefix))
    except Exception as e:
        console.print(f"\N{CROSS MARK} Upload failed: {e}")
        console.print(f"\N{WASTEBASKET} Cleaning up volume {name}")
        try:
            jig.api.volumes.delete(name)
        except Exception as cleanup_error:
            console.print(f"\N{WARNING SIGN} Failed to delete volume: {cleanup_error}")
        sys.exit(1)
        # raise Exit(1) from None


def volumes_update(jig: Jig, name: str, source: Path) -> None:
    """Update a volume and re-upload files"""
    try:
        volume_data = jig.api.volumes.with_raw_response.retrieve(name).json()
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None

    new_version = int(volume_data.get("current_version", 0)) + 1  # type: ignore
    remote_prefix = f"{name}/{new_version}"

    console.print(f"\N{INFORMATION SOURCE} Uploading files for volume {name}")
    _asyncio_run_upload(Uploader(jig.together).upload_files(source, remote_prefix))

    console.print(f"\N{INFORMATION SOURCE} Updating volume {name}, version {new_version} from {source}")
    jig.api.volumes.update(name, content={"type": "files", "source_prefix": remote_prefix})
    console.print("\N{CHECK MARK} Volume updated successfully")


def volumes_delete(jig: Jig, name: str) -> None:
    """Delete a volume"""
    try:
        jig.api.volumes.delete(name)
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None
    console.print(f"\N{CHECK MARK} Deleted volume {name}")


def volumes_describe(jig: Jig, name: str) -> Any:
    """Describe a volume"""
    try:
        return jig.api.volumes.with_raw_response.retrieve(name)
    except NotFoundError:
        raise JigError(f"Volume {name} not found") from None


async def jig_volumes_list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List all volumes."""
    list_resp = await config.client.beta.jig.volumes.list()

    data, next_cursor = mock_pagination(list_resp.data or [], cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(list_resp).decode())
        return

    table = ListTable()

    table.add_primary_column("ID")
    table.add_column("Name")
    table.add_column("Created At")
    table.add_column("Updated At")

    for volume in data:
        table.add_row(volume.id, volume.name, volume.created_at, volume.updated_at)

    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta jig volumes list --after {next_cursor}[/white]")


async def jig_volumes_describe(
    name: Annotated[str, Parameter(name="--name", help="Volume name")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Describe a volume."""
    try:
        vol = await config.client.beta.jig.volumes.retrieve(name)
    except NotFoundError:
        _jig_fail(f"Volume {name} not found")
    else:
        console.print_json(openapi_dumps(vol).decode())


def dockerfile_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Generate Dockerfile."""
    _run_jig_cmd(config, toml_config, dockerfile)


def build_cli(
    tag: Annotated[str, Parameter(help="Image tag")] = "latest",
    warmup: Annotated[bool, Parameter(help="Run warmup to build torch compile cache", negative=())] = False,
    docker_args: Annotated[
        Optional[str],
        Parameter(name="--docker-args", help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)"),
    ] = None,
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Build container image."""
    _run_jig_cmd(config, toml_config, lambda jig: build(jig, tag, warmup, docker_args))


def push_cli(
    tag: Annotated[str, Parameter(help="Image tag")] = "latest",
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Push image to registry."""
    _run_jig_cmd(config, toml_config, lambda jig: push(jig, tag))


def deploy_cli(
    tag: Annotated[str, Parameter(help="Image tag")] = "latest",
    build_only: Annotated[bool, Parameter(help="Build and push only", negative=())] = False,
    warmup: Annotated[bool, Parameter(help="Run warmup to build torch compile cache", negative=())] = False,
    detach: Annotated[bool, Parameter(help="Do not wait for deployment to complete", negative=())] = False,
    docker_args: Annotated[
        Optional[str],
        Parameter(name="--docker-args", help="Extra args for docker build (or use DOCKER_BUILD_EXTRA_ARGS env)"),
    ] = None,
    image: Annotated[Optional[str], Parameter(name="--image", help="Use existing image (skip build/push)")] = None,
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Deploy model."""
    _run_jig_cmd(
        config,
        toml_config,
        lambda jig: deploy(jig, tag, build_only, warmup, detach, docker_args, image),
    )


def status_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Get deployment status."""
    _run_jig_cmd(config, toml_config, lambda jig: status(jig, config.json))


def endpoint_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Get deployment endpoint URL."""
    _run_jig_cmd(config, toml_config, endpoint)


def logs_cli(
    follow: Annotated[bool, Parameter(help="Follow log output", negative=())] = False,
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Get deployment logs."""
    _run_jig_cmd(config, toml_config, lambda jig: logs(jig, follow))


def destroy_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Destroy deployment."""
    _run_jig_cmd(config, toml_config, destroy)


def submit_cli(
    prompt: Annotated[Optional[str], Parameter(help="Job prompt")] = None,
    payload: Annotated[Optional[str], Parameter(help="Job payload JSON")] = None,
    watch: Annotated[bool, Parameter(help="Watch job status until completion", negative=())] = False,
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Submit a job to the deployment."""
    _run_jig_cmd(config, toml_config, lambda jig: submit(jig, prompt, payload, watch))


def job_status_cli(
    request_id: Annotated[str, Parameter(name="--request-id", help="Job request ID")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Get status of a specific job."""
    _run_jig_cmd(config, toml_config, lambda jig: job_status(jig, request_id))


def queue_status_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Get queue metrics for the deployment."""
    _run_jig_cmd(config, toml_config, queue_status)


def list_deployments_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """List all deployments."""
    _run_jig_cmd(config, toml_config, list_deployments)


def secrets_set_cli(
    name: Annotated[str, Parameter(name="--name", help="Secret name")],
    value: Annotated[str, Parameter(name="--value", help="Secret value")],
    description: Annotated[str, Parameter(help="Secret description")] = "",
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Set a secret (create or update)."""
    _run_jig_cmd(config, toml_config, lambda jig: secrets_set(jig, name, value, description))


def secrets_unset_cli(
    name: Annotated[str, Parameter(name="--name", help="Secret name to remove")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Remove a secret from local state."""
    _run_jig_cmd(config, toml_config, lambda jig: secrets_unset(jig, name))


def secrets_delete_cli(
    name: Annotated[str, Parameter(name="--name", help="Secret name to delete")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Delete a secret and unset it locally."""
    _run_jig_cmd(config, toml_config, lambda jig: secrets_delete(jig, name))


def secrets_list_cli(
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """List all secrets with sync status."""

    def inner(jig: Jig) -> Any:
        if config.json:
            return jig.api.secrets.with_raw_response.list()
        secrets_list(jig)
        return None

    _run_jig_cmd(config, toml_config, inner)


def jig_volumes_create_cli(
    name: Annotated[str, Parameter(name="--name", help="Volume name")],
    source: Annotated[Path, Parameter(name="--source", help="Source directory path")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Create a volume and upload files."""
    if not source.is_dir():
        _jig_fail(f"Not a directory: {source}")
    _run_jig_cmd(config, toml_config, lambda jig: volumes_create(jig, name, source))


def jig_volumes_update_cli(
    name: Annotated[str, Parameter(name="--name", help="Volume name")],
    source: Annotated[Path, Parameter(name="--source", help="New source directory path")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Update a volume and re-upload files."""
    if not source.is_dir():
        _jig_fail(f"Not a directory: {source}")
    _run_jig_cmd(config, toml_config, lambda jig: volumes_update(jig, name, source))


def jig_volumes_delete_cli(
    name: Annotated[str, Parameter(name="--name", help="Volume name")],
    *,
    config: CLIConfigParameter,
    toml_config: TomlConfigParameter = None,
) -> None:
    """Delete a volume."""
    _run_jig_cmd(config, toml_config, lambda jig: volumes_delete(jig, name))
