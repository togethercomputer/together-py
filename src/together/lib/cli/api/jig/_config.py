"""Configuration classes for jig deployment tool."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]


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

    model_name: Optional[str] = None
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
                print(
                    f"ERROR: Configuration file not found: {config_path}",
                    file=sys.stderr,
                )
                sys.exit(1)
            with found_path.open("rb") as f:
                return cls.load(tomllib.load(f), found_path)

        jigfile = Path("jig.toml")
        if jigfile.exists():
            with jigfile.open("rb") as f:
                return cls.load(tomllib.load(f), jigfile)

        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
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
        """Load configuration from parsed TOML data."""
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
            jig_config.setdefault("deploy", {})["autoscaling"] = autoscaling

        return cls(
            image=ImageConfig.from_dict(jig_config.get("image", {})),
            deploy=DeployConfig.from_dict(jig_config.get("deploy", {})),
            dockerfile=jig_config.get("dockerfile", "Dockerfile"),
            model_name=name,
            _path=path,
        )
