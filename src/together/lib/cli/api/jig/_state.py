"""State management for jig deployment tool."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class State:
    """Persistent state stored in .jig.json"""

    _config_dir: Path
    username: str | None = None
    secrets: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, config_dir: Path) -> State:
        """Load state from .jig.json or create new state."""
        path = config_dir / ".jig.json"
        try:
            with open(path) as f:
                return cls(_config_dir=config_dir, **json.load(f))
        except FileNotFoundError:
            return cls(_config_dir=config_dir)

    def save(self) -> None:
        """Save state to .jig.json"""
        path = self._config_dir / ".jig.json"
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
