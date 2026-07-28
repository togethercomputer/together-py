from __future__ import annotations

import os
import sys
import json
import time
import shlex
import shutil
import asyncio
import subprocess
import urllib.request
from typing import cast
from pathlib import Path

from rich.markup import escape as escape_rich_markup

from together import __version__
from together.lib.utils import log_debug
from together.lib.cli.utils._prompt import confirm
from together.lib.cli.utils._console import error_console

_PYPI_URL = "https://pypi.org/pypi/together/json"
_CACHE_TTL_SECONDS = 24 * 60 * 60
_REQUEST_TIMEOUT_SECONDS = 1.0
_RESOLUTION_TIMEOUT_SECONDS = _REQUEST_TIMEOUT_SECONDS + 0.5
_DISABLE_ENV_VAR = "TOGETHER_DISABLE_VERSION_CHECK"
_TRUTHY_ENV_VALUES = frozenset({"1", "true", "yes"})


def _parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid Together CLI version: {version}")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def _is_newer_version(latest_version: str, current_version: str) -> bool:
    return _parse_version(latest_version) > _parse_version(current_version)


def _cache_path() -> Path:
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "Together" / "version-check.json"

    cache_home = os.environ.get("XDG_CACHE_HOME")
    if cache_home:
        return Path(cache_home) / "together" / "version-check.json"
    return Path.home() / ".cache" / "together" / "version-check.json"


def _load_cache() -> dict[str, object] | None:
    try:
        data: object = json.loads(_cache_path().read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return cast(dict[str, object], data)
    except (OSError, ValueError):  # JSONDecodeError and UnicodeDecodeError are both ValueError
        return None


def _write_cache(cache: dict[str, object]) -> None:
    path = _cache_path()
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(
            json.dumps(cache, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)
    except OSError as exc:
        log_debug("Unable to cache Together CLI version-check state", error=exc)
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _is_fresh_timestamp(timestamp: object, now: float) -> bool:
    if not isinstance(timestamp, (int, float)):
        return False
    return 0 <= now - timestamp < _CACHE_TTL_SECONDS


def _read_cached_version(now: float) -> str | None:
    cache = _load_cache()
    if cache is None:
        return None

    checked_at = cache.get("checked_at")
    latest_version = cache.get("latest_version")
    if not isinstance(latest_version, str) or not _is_fresh_timestamp(checked_at, now):
        return None

    try:
        _parse_version(latest_version)
    except ValueError:
        return None
    return latest_version


def _write_cached_version(latest_version: str, now: float) -> None:
    cache = _load_cache() or {}
    payload: dict[str, object] = {
        "checked_at": now,
        "latest_version": latest_version,
    }
    informed_at = cache.get("informed_at")
    if isinstance(informed_at, (int, float)):
        payload["informed_at"] = informed_at
    _write_cache(payload)


def _was_informed_recently(now: float) -> bool:
    cache = _load_cache()
    if cache is None:
        return False
    return _is_fresh_timestamp(cache.get("informed_at"), now)


def _mark_informed(now: float) -> None:
    cache = _load_cache() or {}
    cache["informed_at"] = now
    _write_cache(cache)


def _fetch_latest_version() -> str:
    request = urllib.request.Request(
        _PYPI_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": f"together-cli:{__version__}",
        },
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        payload: object = json.load(response)

    if not isinstance(payload, dict):
        raise ValueError("PyPI returned an invalid response")
    response_data = cast(dict[str, object], payload)
    info = response_data.get("info")
    if not isinstance(info, dict):
        raise ValueError("PyPI response did not include package info")
    package_info = cast(dict[str, object], info)
    latest_version = package_info.get("version")
    if not isinstance(latest_version, str):
        raise ValueError("PyPI response did not include a package version")

    _parse_version(latest_version)
    return latest_version


def _latest_version() -> str:
    now = time.time()
    cached = _read_cached_version(now)
    if cached is not None:
        return cached

    latest = _fetch_latest_version()
    _write_cached_version(latest, now)
    return latest


def _path_contains(path: Path, *parts: str) -> bool:
    normalized = tuple(part.casefold() for part in path.parts)
    expected = tuple(part.casefold() for part in parts)
    return any(normalized[index : index + len(expected)] == expected for index in range(len(normalized)))


def _upgrade_command() -> list[str]:
    executable = Path(sys.executable)
    if shutil.which("uv") and _path_contains(executable, "uv", "tools"):
        return ["uv", "tool", "install", "together", "--upgrade"]
    if shutil.which("pipx") and _path_contains(executable, "pipx", "venvs"):
        return ["pipx", "upgrade", "together"]
    return [sys.executable, "-m", "pip", "install", "--upgrade", "together"]


def _format_command(command: list[str]) -> str:
    if sys.platform == "win32":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def _version_check_disabled() -> bool:
    return os.getenv(_DISABLE_ENV_VAR, "").strip().lower() in _TRUTHY_ENV_VALUES


class VersionCheck:
    """Resolve the latest CLI version in parallel, then inform the user when requested."""

    def __init__(self) -> None:
        self._latest_version: asyncio.Future[str] | None = None
        if not _version_check_disabled():
            self._latest_version = asyncio.get_running_loop().run_in_executor(None, _latest_version)

    async def inform(self, *, non_interactive: bool, allow_prompt: bool) -> None:
        if self._latest_version is None:
            return

        try:
            latest_version = await asyncio.wait_for(
                self._latest_version,
                timeout=_RESOLUTION_TIMEOUT_SECONDS,
            )
            if not _is_newer_version(latest_version, __version__):
                return

            # PyPI lookups are cached separately; this gate ensures we only prompt/inform
            # the user once per day even when every command reuses a cached "outdated" result.
            now = time.time()
            if _was_informed_recently(now):
                return
            _mark_informed(now)

            command = _upgrade_command()
            command_text = escape_rich_markup(_format_command(command))
            error_console.print(
                f"[dim]\nA new Together CLI version is available: {__version__} → {latest_version}.[/dim]"
            )

            if non_interactive or not allow_prompt:
                error_console.print(f"Upgrade with: [bold]{command_text}[/bold]")
                return

            if not await confirm("Upgrade the Together CLI now?"):
                error_console.print(f"Upgrade later with: [bold]{command_text}[/bold]")
                return

            result = await asyncio.to_thread(subprocess.run, command, check=False)
            if result.returncode == 0:
                error_console.print("[success]Together CLI upgraded. The new version will be used next time.[/success]")
            else:
                error_console.print(f"[error]Upgrade failed.[/error] Run manually: [bold]{command_text}[/bold]")
        except KeyboardInterrupt:
            return
        except Exception as exc:
            log_debug("Unable to check for a Together CLI update", error=exc)
