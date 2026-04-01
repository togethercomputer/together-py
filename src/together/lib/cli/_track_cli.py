from __future__ import annotations

import os
import re
import sys
import json
import time
import uuid
import platform
import threading
import urllib.error
import urllib.request
from enum import Enum
from typing import Any, TypeVar, Callable, cast
from pathlib import Path
from functools import wraps

import click
from click.core import ParameterSource
from detect_agent import determine_agent

from together import __version__
from together.lib.utils import log_debug

F = TypeVar("F", bound=Callable[..., Any])

_SESSION_ID = int(str(uuid.uuid4().int)[0:13])

_ENV_TELEMETRY_OFF = frozenset({"1", "true", "yes"})
_ERROR_MESSAGE_MAX_LEN = 500
_CONFIG_DIR_NAME = "together"
_CONFIG_FILE_NAME = "cli.json"

_thread_pool: list[threading.Thread] = []


def telemetry_config_path() -> Path:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Together" / _CONFIG_FILE_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / _CONFIG_DIR_NAME / _CONFIG_FILE_NAME
    return Path.home() / ".config" / _CONFIG_DIR_NAME / _CONFIG_FILE_NAME


def load_telemetry_config() -> dict[str, Any]:
    path = telemetry_config_path()
    if not path.is_file():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        config = cast(dict[str, Any], data)
        # Optimistic memory caching so no other code has to load the config file.
        global _cached_device_id
        _cached_device_id = config.get("device_id")
        return config
    except (OSError, json.JSONDecodeError):
        return {}


def save_telemetry_config(data: dict[str, Any]) -> None:
    path = telemetry_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    if sys.platform != "win32":
        try:
            path.chmod(0o600)
        except OSError:
            pass


def is_tracking_enabled() -> bool:
    if _env_telemetry_disabled():
        log_debug("Analytics tracking disabled by environment variable")
        return False
    if _config_telemetry_disabled():
        log_debug("Analytics tracking disabled by config file")
        return False
    return True


class CliTrackingEvents(Enum):
    CommandStarted = "cli_command_started"
    CommandCompleted = "cli_command_completed"
    CommandFailed = "cli_command_failed"
    CommandUserAborted = "cli_command_user_aborted"
    ApiRequest = "cli_command_api_request"


def invoked_subcommand_path() -> str:
    """Subcommand path after the top-level program name (e.g. ``evals list`` for ``together evals list``).

    Uses :attr:`click.Context.command_path` and strips the root context's ``info_name`` so the
    binary name can differ from ``together`` (entry points, ``python -m``, etc.).
    """
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return ""
    path = ctx.command_path
    root_name = (ctx.find_root().info_name or "").strip()
    if not root_name:
        return path
    prefix = root_name + " "
    if path.startswith(prefix):
        return path[len(prefix) :]
    return path


def flush_pending_events(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        finally:
            for thread in _thread_pool:
                thread.join()

    return wrapper


def track_cli(event_name: CliTrackingEvents, args: dict[str, Any]) -> None:
    """
    Track a CLI event. Non-Blocking.
    """
    if not is_tracking_enabled():
        return

    # Intentionally loading device id here so we don't have to do it in the background thread and have race conditions.
    device_id = _load_device_id()

    def send_event() -> None:
        analytics_api_env = os.getenv("TOGETHER_TELEMETRY_API")
        analytics_api = (
            analytics_api_env if analytics_api_env else "https://api.together.ai/together/gateway/pub/v1/httpRequest"
        )

        try:
            agent_info = determine_agent()
            agent_name = ""
            if agent_info["agent"]:
                agent_name = agent_info["agent"]["name"]

            log_debug("Analytics event sending", event_name=event_name.value, args=args, device_id=device_id)

            payload = {
                "event_source": "cli",
                "event_type": event_name.value,
                "event_properties": {
                    "is_ci": os.getenv("CI") is not None,
                    "is_agent": agent_info["is_agent"],
                    "agent_name": agent_name,
                    **args,
                },
                "context": {
                    "session_id": str(_SESSION_ID),
                    "device_id": device_id,
                    "time": int(time.time() * 1000),
                    "runtime": {
                        "name": "together-cli",
                        "version": __version__,
                        "os": platform.system(),
                        "arch": platform.machine() or "",
                    },
                },
            }
            body = json.dumps(payload)
            log_debug("Analytics event sending", body=body, device_id=device_id)
            req = urllib.request.Request(
                analytics_api,
                data=body.encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"together-cli:{__version__}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1.0):
                pass
        except Exception as e:
            if isinstance(e, urllib.error.HTTPError):
                try:
                    e.read()
                finally:
                    e.close()
            log_debug("Error sending analytics event", error=e, device_id=device_id)

    thread = threading.Thread(target=send_event)
    _thread_pool.append(thread)
    thread.start()


def auto_track_command(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for click commands to automatically track CLI commands start/completion/failure.

    Every command should be decorated with this decorator.
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cmd = invoked_subcommand_path()
        explicit = _get_explicit_cli_parameter_names()
        is_beta_command = cmd.startswith("beta ")
        # If command starts with "beta " remove that from the start of the command name
        if is_beta_command:
            cmd = cmd[len("beta ") :]
        track_cli(CliTrackingEvents.CommandStarted, {"command": cmd, "arguments": explicit})
        try:
            result = f(*args, **kwargs)
        except KeyboardInterrupt as e:
            track_cli(
                CliTrackingEvents.CommandUserAborted,
                {"command": cmd, "arguments": explicit, "is_beta_command": is_beta_command},
            )
            raise e

        # Some commands use sys.exit(1) to exit the program.
        # We need to track these so we can see if they are failing.
        except SystemExit as e:
            if e.code == 0:
                track_cli(
                    CliTrackingEvents.CommandCompleted,
                    {"command": cmd, "arguments": explicit, "is_beta_command": is_beta_command},
                )
                raise e

            track_cli(
                CliTrackingEvents.CommandFailed,
                {
                    "command": cmd,
                    "arguments": explicit,
                    "is_beta_command": is_beta_command,
                    "error": _sanitize_cli_error_message(str(e)),
                },
            )
            raise e

        except Exception as e:
            track_cli(
                CliTrackingEvents.CommandFailed,
                {
                    "command": cmd,
                    "arguments": explicit,
                    "is_beta_command": is_beta_command,
                    "error": _sanitize_cli_error_message(str(e)),
                },
            )
            raise e

        track_cli(
            CliTrackingEvents.CommandCompleted,
            {"command": cmd, "arguments": explicit, "is_beta_command": is_beta_command},
        )
        return result

    return wrapper  # type: ignore


def _sanitize_cli_error_message(msg: str) -> str:
    """Sanitize the error messages caught for telemetry to remove sensitive information."""
    s = msg.strip()
    if len(s) > _ERROR_MESSAGE_MAX_LEN:
        s = s[:_ERROR_MESSAGE_MAX_LEN] + "…"
    s = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-/+]{20,}", r"\1<redacted>", s)
    s = re.sub(
        r"(?i)(api[_-]?key\s*[\"':=]\s*|api[_-]?key\s+)([A-Za-z0-9._\-]{20,})",
        r"\1<redacted>",
        s,
    )
    s = re.sub(r"(?i)(Authorization:\s*)([^\s]+)", r"\1<redacted>", s)
    return s


def _env_telemetry_disabled() -> bool:
    """Check if telemetry is disabled by the environment variable."""
    v = os.getenv("TOGETHER_TELEMETRY_DISABLED", "").strip().lower()
    return v in _ENV_TELEMETRY_OFF


def _config_telemetry_disabled() -> bool:
    """Check if telemetry is disabled by the config file."""
    return load_telemetry_config().get("telemetry_enabled") is False


def _get_explicit_cli_parameter_names() -> list[str]:
    """Names of Click options/arguments whose values came from the user's argv (not defaults/env).

    These are Python parameter names (e.g. ``json`` for ``--json``), not the literal flag spellings.
    """
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return []
    names: list[str] = []
    for name in ctx.params:
        if ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE:
            names.append(name)
    return sorted(names)


_CATCH_ALL_DEVICE_ID = "1a41ab33-35d0-420a-ba28-182fddd249c9"
_cached_device_id: None | str = None


def _load_device_id() -> str:
    """
    Loads a uuid for this device that is stored in the config file.

    If the config file does not contain one, we generate and save it.
    """
    global _cached_device_id
    if _cached_device_id is not None:
        return _cached_device_id
    try:
        config = load_telemetry_config()
        if "device_id" in config:
            return cast(str, config["device_id"])

        _cached_device_id = str(uuid.uuid4())
        config["device_id"] = _cached_device_id
        save_telemetry_config(config)
        return _cached_device_id
    except Exception:
        return _CATCH_ALL_DEVICE_ID
