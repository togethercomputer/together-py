"""Configuration and state management for jig CLI."""

from __future__ import annotations

import os
import sys
import json
from typing import Any, Optional
from pathlib import Path
from dataclasses import field, asdict, dataclass

import click

# Python 3.11+ has tomllib in stdlib, older versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
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
    _explicit_fields: set[str] = field(default_factory=lambda: set[str](), repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImageConfig:
        instance = cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
        instance._explicit_fields = set(data.keys())
        return instance

    def merge(self, other: "ImageConfig") -> "ImageConfig":
        """Merge this config with another, where other takes precedence for explicitly set fields"""
        return ImageConfig(
            python_version=other.python_version if "python_version" in other._explicit_fields else self.python_version,
            system_packages=other.system_packages if "system_packages" in other._explicit_fields else self.system_packages,
            environment={**self.environment, **other.environment},
            run=other.run if "run" in other._explicit_fields else self.run,
            cmd=other.cmd if "cmd" in other._explicit_fields else self.cmd,
            copy=list(set(self.copy + other.copy)),
            auto_include_git=other.auto_include_git if "auto_include_git" in other._explicit_fields else self.auto_include_git,
            _explicit_fields=self._explicit_fields | other._explicit_fields,
        )


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

    name: Optional[str] = None  # Explicit deployment name override
    description: str = ""
    gpu_type: str = "h100-80gb"
    gpu_count: int = 1
    cpu: float = 1
    memory: float = 8
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
    _explicit_fields: set[str] = field(default_factory=lambda: set[str](), repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeployConfig:
        deploy_config = {k: v for k, v in data.items() if k in cls.__annotations__}
        if isinstance(deploy_config.get("volume_mounts"), list):
            deploy_config["volume_mounts"] = [VolumeMount.from_dict(vm) for vm in deploy_config["volume_mounts"]]
        instance = cls(**deploy_config)
        instance._explicit_fields = set(data.keys())
        return instance

    def merge(self, other: "DeployConfig") -> "DeployConfig":
        """Merge this config with another, where other takes precedence for explicitly set fields"""
        # Merge volume_mounts from both configs
        merged_volume_mounts = list({vm.name: vm for vm in self.volume_mounts + other.volume_mounts}.values())

        return DeployConfig(
            name=other.name if "name" in other._explicit_fields else self.name,
            description=other.description if "description" in other._explicit_fields else self.description,
            gpu_type=other.gpu_type if "gpu_type" in other._explicit_fields else self.gpu_type,
            gpu_count=other.gpu_count if "gpu_count" in other._explicit_fields else self.gpu_count,
            cpu=other.cpu if "cpu" in other._explicit_fields else self.cpu,
            memory=other.memory if "memory" in other._explicit_fields else self.memory,
            storage=other.storage if "storage" in other._explicit_fields else self.storage,
            min_replicas=other.min_replicas if "min_replicas" in other._explicit_fields else self.min_replicas,
            max_replicas=other.max_replicas if "max_replicas" in other._explicit_fields else self.max_replicas,
            port=other.port if "port" in other._explicit_fields else self.port,
            environment_variables={**self.environment_variables, **other.environment_variables},
            command=other.command if "command" in other._explicit_fields else self.command,
            autoscaling={**self.autoscaling, **other.autoscaling},
            health_check_path=other.health_check_path if "health_check_path" in other._explicit_fields else self.health_check_path,
            termination_grace_period_seconds=other.termination_grace_period_seconds if "termination_grace_period_seconds" in other._explicit_fields else self.termination_grace_period_seconds,
            volume_mounts=merged_volume_mounts,
            _explicit_fields=self._explicit_fields | other._explicit_fields,
        )


@dataclass
class Config:
    """Main configuration from jig.toml or pyproject.toml with profile support"""

    model_name: str = ""
    dockerfile: str = "Dockerfile"
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))
    _profile: Optional[str] = None

    @classmethod
    def find(cls, config_path: Optional[str] = None, profile: Optional[str] = None, init: bool = False) -> Config:
        """Find specified config_path, pyproject.toml, or jig.toml with profile support

        Profile resolution priority:
        1. --profile flag (highest priority)
        2. JIG_PROFILE environment variable
        3. "default" profile
        """
        # Resolve profile: CLI flag > env var > default
        resolved_profile = profile or os.getenv("JIG_PROFILE")

        if config_path:
            found_path = Path(config_path)
            if not found_path.exists():
                click.echo(f"ERROR: Configuration file not found: {config_path}", err=True)
                sys.exit(1)
            return cls.load(tomllib.load(found_path.open("rb")), found_path, resolved_profile)

        if (jigfile := Path("jig.toml")).exists():
            return cls.load(tomllib.load(jigfile.open("rb")), jigfile, resolved_profile)

        if (pyproject_path := Path("pyproject.toml")).exists():
            data = tomllib.load(pyproject_path.open("rb"))
            if "tool" in data and "jig" in data["tool"]:
                return cls.load(data, pyproject_path, resolved_profile)

        if init:
            return cls()
        click.echo(
            "ERROR: No pyproject.toml or jig.toml found, use --config to specify a config path.",
            err=True,
        )
        sys.exit(1)

    @classmethod
    def load(cls, data: dict[str, Any], path: Path, profile: Optional[str] = None) -> Config:
        """Load configuration from parsed TOML data with profile merging logic

        Profile structure:
        - All profiles follow [tool.jig.PROFILE.*] pattern (including "default")
        - When no --profile specified, uses "default" profile
        - For backwards compatibility, falls back to [tool.jig.*] if [tool.jig.default.*] doesn't exist

        Merging hierarchy (when profile != "default"):
        1. Load [tool.jig.default.*] (or [tool.jig.*] as fallback)
        2. Merge with [tool.jig.PROFILE.*]
        """
        is_pyproject = path.name == "pyproject.toml"
        root_config = data.get("tool", {}).get("jig", {}) if is_pyproject else data

        # Get base project name from [project].name
        base_name = data.get("project", {}).get("name", "") if is_pyproject else path.resolve().parent.name
        if not base_name:
            base_name = path.resolve().parent.name
            click.echo(f"\N{PACKAGE} Name not set in config file - defaulting to {base_name}")

        # Use "default" as the profile when none specified
        effective_profile = profile or "default"

        # Check if we're using the new structure ([tool.jig.default.*]) or old structure ([tool.jig.*])
        has_default_profile = "default" in root_config

        # Load base/default configuration
        if has_default_profile:
            # New structure: use [tool.jig.default.*]
            default_config = root_config["default"]
            base_image = ImageConfig.from_dict(default_config.get("image", {}))
            base_deploy = DeployConfig.from_dict(default_config.get("deploy", {}))
            base_autoscaling = default_config.get("autoscaling", {})
        else:
            # Old structure: fallback to [tool.jig.*] for backwards compatibility
            base_image = ImageConfig.from_dict(root_config.get("image", {}))
            base_deploy = DeployConfig.from_dict(root_config.get("deploy", {}))
            base_autoscaling = root_config.get("autoscaling", {})

        # If a specific profile is requested (and it's not "default"), merge with it
        image_config = base_image
        deploy_config = base_deploy
        autoscaling_config = base_autoscaling

        if effective_profile != "default" and effective_profile in root_config:
            profile_config = root_config[effective_profile]
            if "image" in profile_config:
                image_config = image_config.merge(ImageConfig.from_dict(profile_config["image"]))
            if "deploy" in profile_config:
                deploy_config = deploy_config.merge(DeployConfig.from_dict(profile_config["deploy"]))
            if "autoscaling" in profile_config:
                autoscaling_config = {**autoscaling_config, **profile_config["autoscaling"]}

        # Determine final deployment name
        if deploy_config.name:
            # Explicit name override in deploy config
            model_name = deploy_config.name
        elif effective_profile != "default":
            # Auto-suffix with profile name
            model_name = f"{base_name}-{effective_profile}"
        else:
            # Use base name for default profile
            model_name = base_name

        # Add model name to autoscaling config
        if autoscaling_config:
            autoscaling_config["model"] = model_name
            deploy_config.autoscaling = autoscaling_config

        return cls(
            model_name=model_name,
            dockerfile=root_config.get("dockerfile", "Dockerfile"),
            image=image_config,
            deploy=deploy_config,
            _path=path,
            _profile=effective_profile,
        )


# --- State Management ---


@dataclass
class State:
    """Persistent state stored in profile-specific .jig*.json files"""

    _config_dir: Path
    _profile: Optional[str] = None
    registry_base_path: str = ""
    secrets: dict[str, str] = field(default_factory=dict[str, str])
    volumes: dict[str, str] = field(default_factory=dict[str, str])

    @classmethod
    def load(cls, config_dir: Path, profile: Optional[str] = None) -> State:
        """Load state from profile-specific file

        Uses .jig.json for default profile, .jig-PROFILE.json for named profiles

        Profile resolution priority:
        1. Passed profile parameter (from --profile flag)
        2. JIG_PROFILE environment variable
        3. "default" profile
        """
        # Resolve profile: parameter > env var > default
        effective_profile = profile or os.getenv("JIG_PROFILE") or "default"

        if effective_profile == "default":
            filename = ".jig.json"
        else:
            filename = f".jig-{effective_profile}.json"

        path = config_dir / filename
        try:
            with open(path) as f:
                data = {k: v for k, v in json.load(f).items() if k in cls.__annotations__ and not k.startswith("_")}
                return cls(_config_dir=config_dir, _profile=effective_profile, **data)
        except FileNotFoundError:
            return cls(_config_dir=config_dir, _profile=effective_profile)

    def save(self) -> None:
        """Save state to profile-specific file

        Uses .jig.json for default profile, .jig-PROFILE.json for named profiles
        """
        if self._profile == "default":
            filename = ".jig.json"
        else:
            filename = f".jig-{self._profile}.json"

        path = self._config_dir / filename
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
