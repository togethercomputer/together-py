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
from typing import TYPE_CHECKING, Any, TypeVar, Callable, cast
from pathlib import Path

from detect_agent import determine_agent
from cyclopts.exceptions import CycloptsError

if TYPE_CHECKING:
    from cyclopts import App

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


def flush_pending_events() -> None:
    for thread in _thread_pool:
        thread.join()
    _thread_pool.clear()


def track_cli(event_name: CliTrackingEvents, args: dict[str, Any]) -> threading.Thread | None:
    """
    Track a CLI event. Non-blocking (daemon thread).

    Returns the started thread, or None if telemetry is disabled (tests may ``join()`` the thread).
    """
    if not is_tracking_enabled():
        return None

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

    thread = threading.Thread(target=send_event, daemon=True)
    _thread_pool.append(thread)
    thread.start()
    return thread


def _long_option_names_in_tokens(tokens: list[str]) -> list[str]:
    names: list[str] = []
    for token in tokens:
        if token.startswith("--"):
            names.append(token.removeprefix("--").split("=", 1)[0])
    return names


def _legacy_command_before_first_option(tokens: list[str]) -> tuple[str, bool]:
    """Fallback when cyclopts cannot resolve a command chain (unknown invocations)."""
    parts: list[str] = []
    for token in tokens:
        if token.startswith("--"):
            break
        parts.append(token)
    is_beta_command = bool(parts and parts[0] == "beta")
    if is_beta_command:
        parts = parts[1:]
    return (" ".join(parts), is_beta_command)


# First subcommand token only (alias -> primary name) for stable telemetry.
_TELEMETRY_SUBCOMMAND_ALIASES: dict[str, str] = {"ft": "fine-tuning"}


def _canonical_telemetry_command(cmd: str) -> str:
    if not cmd:
        return cmd
    parts = cmd.split()
    primary = _TELEMETRY_SUBCOMMAND_ALIASES.get(parts[0])
    if primary is not None:
        parts[0] = primary
    parts = ["list" if p == "ls" else p for p in parts]
    parts = ["delete" if p == "-d" else p for p in parts]
    parts = ["create" if p == "-c" else p for p in parts]
    return " ".join(parts)


def parse_command_and_flags(app: App, tokens: list[str]) -> tuple[str, list[str], bool]:
    """
    Return telemetry-safe command path (registered subcommands only), argument *names* from
    cyclopts resolution (including positional parameters — values are never returned), and
    whether the invocation is under ``beta``.

    Subcommand aliases (e.g. ``ft``) are normalized to their primary names (e.g. ``fine-tuning``).
    The ``list`` alias ``ls`` is normalized to ``list`` in the returned command path.
    The ``delete`` alias ``-d`` is normalized to ``delete`` in the returned command path.
    The ``create`` alias ``-c`` is normalized to ``create`` in the returned command path.

    Requires the root cyclopts :class:`~cyclopts.App` so positional values are not mistaken
    for subcommand tokens (e.g. ``beta jig secrets set <name> <value>``).
    """
    argv = list(tokens)
    chain, _, rest_after_chain = app.parse_commands(argv, include_parent_meta=False)
    legacy_cmd, legacy_beta = _legacy_command_before_first_option(argv)

    if chain:
        is_beta_command = chain[0] == "beta"
        chain_tail = list(chain[1:] if is_beta_command else chain)
        parsed_command = " ".join(chain_tail)
        # ``beta`` alone matches first; remaining tokens are not nested beta subcommands (invalid path).
        if chain == ("beta",) and rest_after_chain:
            parsed_command = legacy_cmd
    else:
        parsed_command = legacy_cmd
        is_beta_command = legacy_beta

    explicit_args: list[str] = []
    try:
        _, bound, _unused, _ignored = app.parse_known_args(argv)
        explicit_args.extend(bound.arguments.keys())
    except CycloptsError:
        explicit_args.extend(_long_option_names_in_tokens(rest_after_chain))

    return (_canonical_telemetry_command(parsed_command), explicit_args, is_beta_command)


def _redact_secrets_in_error_text(s: str) -> str:
    """Apply secret redaction patterns to error text (run before length truncation)."""
    # `https://user:pass@host/...` and `http://...`
    s = re.sub(
        r"(?i)(https?://)([^:/?#\s]+):([^@]+)@",
        r"\1<redacted>:<redacted>@",
        s,
    )
    # Query / fragment: `?token=...`, `&api_key=...`, etc.
    s = re.sub(
        r"(?i)([?&#])(?:access_?token|id_?token|refresh_?token|api_?key|apikey|"
        r"password|passwd|client_?secret|token|secret|credentials)=([^&#\s]+)",
        r"\1<redacted>",
        s,
    )
    # JWT (header typically base64 of `{"` → eyJ; also long JWS / opaque three-part tokens)
    s = re.sub(
        r"(?i)\b(eyJ[a-z0-9_-]*\.[a-z0-9_-]*\.[a-z0-9_-]*)\b",
        "<redacted>",
        s,
    )
    s = re.sub(
        r"(?i)\b([a-z0-9_-]{20,}\.[a-z0-9_-]{20,}\.[a-z0-9_-]{20,})\b",
        "<redacted>",
        s,
    )
    # OpenAI / common `sk-…` API keys; Hugging Face `hf_…`; Together-style `tog_…`
    s = re.sub(r"(?i)(?<![a-z0-9_-])(sk-[a-z0-9_-]+)(?![a-z0-9_-])", "<redacted>", s)
    s = re.sub(r"(?i)(?<![a-z0-9_])(hf_[a-z0-9_-]+)(?![a-z0-9_])", "<redacted>", s)
    s = re.sub(r"(?i)(?<![a-z0-9_])(tgp_[a-z0-9_-]+)(?![a-z0-9_])", "<redacted>", s)
    s = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-/+]+", r"\1<redacted>", s)
    s = re.sub(
        r"(?i)(api[_-]?key\s*[\"':=]\s*|api[_-]?key\s+)([A-Za-z0-9._\-]{20,})",
        r"\1<redacted>",
        s,
    )
    s = re.sub(r"(?i)(Authorization:\s*)([^\s]+)", r"\1<redacted>", s)
    s = re.sub(
        r"(?i)(Basic\s+)([A-Za-z0-9+/=]{8,})",
        r"\1<redacted>",
        s,
    )
    return s


def sanitize_cli_error_message(msg: str) -> str:
    """Sanitize the error messages caught for telemetry to remove sensitive information."""
    s = _redact_secrets_in_error_text(msg.strip())
    if len(s) > _ERROR_MESSAGE_MAX_LEN:
        s = s[:_ERROR_MESSAGE_MAX_LEN] + "…"
    return s


def _env_telemetry_disabled() -> bool:
    """Check if telemetry is disabled by the environment variable."""
    v = os.getenv("TOGETHER_TELEMETRY_DISABLED", "").strip().lower()
    return v in _ENV_TELEMETRY_OFF


def _config_telemetry_disabled() -> bool:
    """Check if telemetry is disabled by the config file."""
    return load_telemetry_config().get("telemetry_enabled") is False


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
