"""Configuration and state management for jig CLI."""

from __future__ import annotations

import os
import sys
import json
from typing import Any, Optional
from pathlib import Path
from dataclasses import field, asdict, dataclass

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

# --- Environment Configuration ---

TOGETHER_ENV = os.getenv("TOGETHER_ENV", "prod")
if TOGETHER_ENV == "prod":
    API_URL = "api.together.ai"
elif TOGETHER_ENV == "qa":
    API_URL = "api.qa.together.ai"
elif TOGETHER_ENV == "dev":
    API_URL = os.getenv("TOGETHER_API_URL", "")
    if not API_URL:
        print("ERROR: API_URL must be set in dev mode", file=sys.stderr)
        sys.exit(1)
else:
    print(f"ERROR: unknown together env {TOGETHER_ENV}", file=sys.stderr)
    sys.exit(1)

GENERATE_DOCKERFILE = os.getenv("GENERATE_DOCKERFILE", "0") != "0"
DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")

UPLOAD_CONCURRENCY_LIMIT = int(os.getenv("TOGETHER_UPLOAD_CONCURRENCY", "15"))
MULTIPART_CHUNK_SIZE_MB = int(os.getenv("TOGETHER_MULTIPART_CHUNK_SIZE_MB", "20"))
MULTIPART_THRESHOLD_MB = int(os.getenv("TOGETHER_MULTIPART_THRESHOLD_MB", "100"))
MAX_UPLOAD_RETRIES = 3


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
class DeployConfig:
    """Deployment configuration"""

    description: str = ""
    gpu_type: str = "h100-80gb"
    gpu_count: int = 1
    cpu: int = 1
    memory: int = 8
    min_replicas: int = 1
    max_replicas: int = 1
    port: int = 8000
    environment_variables: dict[str, str] = field(default_factory=dict)
    command: Optional[list[str]] = None
    autoscaling: dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeployConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class Config:
    """Main configuration from jig.toml or pyproject.toml"""

    model_name: str = ""
    dockerfile: str = "Dockerfile"
    image: ImageConfig = field(default_factory=ImageConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    _path: Path = field(default_factory=lambda: Path("pyproject.toml"))

    @classmethod
    def find(cls, config_path: Optional[str] = None, init: bool = False) -> Config:
        """Find specified config_path, pyproject.toml, or jig.toml"""
        if config_path:
            found_path = Path(config_path)
            if not found_path.exists():
                print(f"ERROR: Configuration file not found: {config_path}", file=sys.stderr)
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
        print(
            "ERROR: No pyproject.toml or jig.toml found, use --config to specify a config path.",
            file=sys.stderr,
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
                print(f"\N{PACKAGE} Name not set in config file or pyproject.toml - defaulting to {name}")

        if autoscaling := jig_config.get("autoscaling", {}):
            autoscaling["model"] = name
            jig_config["deploy"]["autoscaling"] = autoscaling

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
    registry_base_path: Optional[str] = None
    secrets: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, config_dir: Path) -> State:
        path = config_dir / ".jig.json"
        try:
            with open(path) as f:
                return cls(_config_dir=config_dir, **json.load(f))
        except FileNotFoundError:
            return cls(_config_dir=config_dir)

    def save(self) -> None:
        path = self._config_dir / ".jig.json"
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
