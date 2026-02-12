"""Configuration and state management for jig CLI."""

from __future__ import annotations

import json
import os
import sys
import typing
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import click

if TYPE_CHECKING:
    import tomli as tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

# --- Environment Configuration ---

DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")

UPLOAD_CONCURRENCY_LIMIT = int(os.getenv("TOGETHER_UPLOAD_CONCURRENCY", "15"))
MULTIPART_CHUNK_SIZE_MB = int(os.getenv("TOGETHER_MULTIPART_CHUNK_SIZE_MB", "20"))
MULTIPART_THRESHOLD_MB = int(os.getenv("TOGETHER_MULTIPART_THRESHOLD_MB", "100"))
MAX_UPLOAD_RETRIES = 3

# Warmup configuration (for torch compile cache)
WARMUP_ENV_NAME = os.getenv("WARMUP_ENV_NAME", "TORCHINDUCTOR_CACHE_DIR")
WARMUP_DEST = os.getenv("WARMUP_DEST", "torch_cache")


# --- Configuration Dataclasses ---


@dataclass
class ImageConfig:
    """Container image configuration from pyproject.toml"""

    python_version: str = "3.11"
    system_packages: list[str] = field(default_factory=list[str])
    environment: dict[str, str] = field(default_factory=dict[str, str])
    run: list[str] = field(default_factory=list[str])
    cmd: str = "python app.py"
    copy: list[str] = field(default_factory=list[str])
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
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


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
    command: Optional[list[str]] = None
    autoscaling: dict[str, str] = field(default_factory=dict[str, str])
    health_check_path: str = "/health"
    termination_grace_period_seconds: int = 300
    volume_mounts: list[VolumeMount] = field(default_factory=list[VolumeMount])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeployConfig:
        deploy_config = {k: v for k, v in data.items() if k in cls.__annotations__}
        if isinstance(deploy_config.get("volume_mounts"), list):
            deploy_config["volume_mounts"] = [VolumeMount.from_dict(vm) for vm in deploy_config["volume_mounts"]]
        return cls(**deploy_config)


def validate(value: Any, value_type: type, path: str = "") -> str | None:
    origin = typing.get_origin(value_type)
    args = typing.get_args(value_type)

    if origin is list:
        if not isinstance(value, list):
            return f"{path}: expected list, got {type(value).__name__}"
        for i, v in enumerate(value):
            if err := validate(v, args[0], f"{path}[{i}]"):
                return err
        return None

    if origin is dict:
        if not isinstance(value, dict):
            return f"{path}: expected dict, got {type(value).__name__}"
        for k, v in value.items():
            if err := validate(k, args[0], f"{path}.key({k!r})"):
                return err
            if err := validate(v, args[1], f"{path}[{k!r}]"):
                return err
        return None

    if origin is Union:
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
        return f"{path}: expected {type(value).__name__}, got {value!r}"
    return None


@dataclass
class Config:
    """Main configuration from jig.toml or pyproject.toml"""

    model_name: str = ""
    dockerfile: str = "Dockerfile"
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))

    def __post_init__(self):
        if err := validate(self, type(self)):
            raise click.UsageError(f"Invalid {self._path}: {err}")

    @classmethod
    def find(cls, config_path: Optional[str] = None, init: bool = False) -> Config:
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
        is_pyproject = path.name == "pyproject.toml"

        jig_config = data.get("tool", {}).get("jig", {}) if is_pyproject else data

        name = jig_config.get("name")
        if name is None:
            if is_pyproject:
                name = data.get("project", {}).get("name", "")
            else:
                name = path.resolve().parent.name
                click.echo(f"\N{PACKAGE} Name not set in config file or pyproject.toml - defaulting to {name}")

        if autoscaling := jig_config.get("autoscaling", {}):
            autoscaling["model"] = name
            jig_config["deploy"]["autoscaling"] = autoscaling

        # Support volume_mounts at jig level (merge into deploy config)
        jig_config["deploy"]["volume_mounts"] = jig_config.get("volume_mounts", [])

        return cls(
            image=ImageConfig.from_dict(jig_config.get("image", {})),
            deploy=DeployConfig.from_dict(jig_config.get("deploy", {})),
            dockerfile=jig_config.get("dockerfile", "Dockerfile"),
            model_name=name,
            _path=path,
        )


# --- State Management ---


@dataclass
class State:
    """Persistent state stored in .jig.json"""

    _config_dir: Path
    registry_base_path: str = ""
    secrets: dict[str, str] = field(default_factory=dict[str, str])
    volumes: dict[str, str] = field(default_factory=dict[str, str])

    @classmethod
    def load(cls, config_dir: Path) -> State:
        path = config_dir / ".jig.json"
        try:
            with open(path) as f:
                data = {k: v for k, v in json.load(f).items() if k in cls.__annotations__ and not k.startswith("_")}
                return cls(_config_dir=config_dir, **data)
        except FileNotFoundError:
            return cls(_config_dir=config_dir)

    def save(self) -> None:
        path = self._config_dir / ".jig.json"
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
