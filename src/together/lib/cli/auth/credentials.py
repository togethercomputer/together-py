from __future__ import annotations

import os
import sys
import json
from typing import Any, Optional, cast
from pathlib import Path
from dataclasses import asdict, dataclass

from filelock import FileLock

_CONFIG_DIR_NAME = "together"
_CREDENTIALS_FILE_NAME = "credentials.json"
_LOCK_SUFFIX = ".lock"


@dataclass
class StoredCredentials:
    """Persisted OIDC tokens from `tg login`.

    Access tokens are short-lived (~5 minutes) and non-revocable; the CLI stores
    the refresh token and silently refreshes the access token before API calls.
    """

    access_token: str
    refresh_token: str
    expires_at: float  # unix timestamp (UTC)
    token_type: str = "Bearer"
    id_token: Optional[str] = None
    scope: Optional[str] = None
    client_id: Optional[str] = None
    token_endpoint: Optional[str] = None
    issuer: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoredCredentials:
        return cls(
            access_token=str(data["access_token"]),
            refresh_token=str(data["refresh_token"]),
            expires_at=float(data["expires_at"]),
            token_type=str(data.get("token_type") or "Bearer"),
            id_token=_optional_str(data.get("id_token")),
            scope=_optional_str(data.get("scope")),
            client_id=_optional_str(data.get("client_id")),
            token_endpoint=_optional_str(data.get("token_endpoint")),
            issuer=_optional_str(data.get("issuer")),
        )


def _optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def credentials_path() -> Path:
    """Return the path to the OIDC credentials file (XDG / APPDATA aware)."""
    override = os.environ.get("TOGETHER_CREDENTIALS_PATH")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Together" / _CREDENTIALS_FILE_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / _CONFIG_DIR_NAME / _CREDENTIALS_FILE_NAME
    return Path.home() / ".config" / _CONFIG_DIR_NAME / _CREDENTIALS_FILE_NAME


def credentials_lock_path(path: Optional[Path] = None) -> Path:
    target = path or credentials_path()
    return target.with_name(target.name + _LOCK_SUFFIX)


def credentials_lock(path: Optional[Path] = None) -> FileLock:
    lock_path = credentials_lock_path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    return FileLock(str(lock_path), timeout=60)  # type: ignore[return-value]


def load_credentials(path: Optional[Path] = None) -> Optional[StoredCredentials]:
    target = path or credentials_path()
    if not target.is_file():
        return None
    try:
        raw = target.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None
        payload = cast(dict[str, Any], data)
        if "access_token" not in payload or "refresh_token" not in payload or "expires_at" not in payload:
            return None
        return StoredCredentials.from_dict(payload)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def save_credentials(credentials: StoredCredentials, path: Optional[Path] = None) -> Path:
    target = path or credentials_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(json.dumps(credentials.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(target)
    if sys.platform != "win32":
        try:
            target.chmod(0o600)
        except OSError:
            pass
    return target


def clear_credentials(path: Optional[Path] = None) -> bool:
    """Remove stored credentials. Returns True if a file was removed."""
    target = path or credentials_path()
    try:
        target.unlink()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return False
