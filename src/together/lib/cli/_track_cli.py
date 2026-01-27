from __future__ import annotations

import os
import re
import sys
import json
import time
import uuid
import platform
import threading
from enum import Enum
from typing import Any, TypeVar, Callable, cast
from pathlib import Path
from functools import wraps

import httpx
import machineid
from detect_agent import determine_agent

from together import __version__
from together.lib.utils import log_debug

F = TypeVar("F", bound=Callable[..., Any])

SESSION_ID = int(str(uuid.uuid4().int)[0:13])

_ENV_TELEMETRY_OFF = frozenset({"1", "true", "yes"})
_ERROR_MESSAGE_MAX_LEN = 500
_CONFIG_DIR_NAME = "together"
_CONFIG_FILE_NAME = "cli.json"


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
        return cast(dict[str, Any], data)
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


def track_cli(event_name: CliTrackingEvents, args: dict[str, Any]) -> None:
    """Track a CLI event. Non-Blocking."""
    if not is_tracking_enabled():
        return

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

            log_debug("Analytics event sending", event_name=event_name.value, args=args)

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
                    "session_id": str(SESSION_ID),
                    "device_id": machineid.id().lower(),
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
            with httpx.Client() as client:
                response = client.post(
                    analytics_api,
                    headers={
                        "content-type": "application/json",
                        "user-agent": f"together-cli:{__version__}",
                    },
                    content=body,
                )
                log_debug("Analytics event sent", response=response.text)
        except Exception as e:
            log_debug("Error sending analytics event", error=e)

    threading.Thread(target=send_event).start()


def auto_track_command(command: str) -> Callable[[F], F]:
    """Decorator for click commands to automatically track CLI commands start/completion/failure."""

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            track_cli(CliTrackingEvents.CommandStarted, {"command": command, "arguments": kwargs})
            try:
                result = f(*args, **kwargs)
            except KeyboardInterrupt as e:
                track_cli(
                    CliTrackingEvents.CommandUserAborted,
                    {"command": command, "arguments": kwargs},
                )
                raise e

            except Exception as e:
                track_cli(
                    CliTrackingEvents.CommandFailed,
                    {
                        "command": command,
                        "arguments": kwargs,
                        "error": _sanitize_cli_error_message(str(e)),
                    },
                )
                raise e

            track_cli(CliTrackingEvents.CommandCompleted, {"command": command, "arguments": kwargs})
            return result

        return wrapper  # type: ignore

    return decorator  # type: ignore


def _sanitize_cli_error_message(msg: str) -> str:
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
    v = os.getenv("TOGETHER_TELEMETRY_DISABLED", "").strip().lower()
    return v in _ENV_TELEMETRY_OFF


def _config_telemetry_disabled() -> bool:
    return load_telemetry_config().get("telemetry_enabled") is False
