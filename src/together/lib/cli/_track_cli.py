from __future__ import annotations

import os
import json
import time
import uuid
import threading
from enum import Enum
from typing import Any, TypeVar, Callable
from functools import wraps

import click
import httpx
import machineid

from together import __version__
from together.lib.utils import log_debug

F = TypeVar("F", bound=Callable[..., Any])

SESSION_ID = int(str(uuid.uuid4().int)[0:13])


def is_tracking_enabled() -> bool:
    # Users can opt-out of tracking with the environment variable.
    if os.getenv("TOGETHER_TELEMETRY_DISABLED"):
        log_debug("Analytics tracking disabled by environment variable")
        return False

    return True


class CliTrackingEvents(Enum):
    CommandStarted = "cli_command_started"
    CommandCompleted = "cli_commmand_completed"
    CommandFailed = "cli_command_failed"
    CommandUserAborted = "cli_command_user_aborted"
    ApiRequest = "cli_command_api_request"


def track_cli(event_name: CliTrackingEvents, args: dict[str, Any]) -> None:
    """Track a CLI event. Non-Blocking."""
    if is_tracking_enabled() == False:
        return

    def send_event() -> None:
        ANALYTICS_API_ENV_VAR = os.getenv("TOGETHER_TELEMETRY_API")
        ANALYTICS_API = (
            ANALYTICS_API_ENV_VAR if ANALYTICS_API_ENV_VAR else "https://api.together.ai/api/together-cli-events"
        )

        try:
            client = httpx.Client()
            client.post(
                ANALYTICS_API,
                headers={"content-type": "application/json", "user-agent": f"together-cli:{__version__}"},
                content=json.dumps(
                    {
                        "event_name": event_name.value,
                        "event_properties": {
                            "is_ci": os.getenv("CI") is not None,
                            **args,
                        },
                        "event_options": {
                            "time": int(time.time() * 1000),
                            "session_id": str(SESSION_ID),
                            "device_id": machineid.id().lower(),
                        },
                    }
                ),
            )
        except Exception as e:
            log_debug("Error sending analytics event", error=e)
            # No-op - this is not critical and we don't want to block the CLI
            pass

    threading.Thread(target=send_event).start()


def auto_track_command(command: str) -> Callable[[F], F]:
    """Decorator for click commands to automatically track CLI commands start/completion/failure."""

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            track_cli(CliTrackingEvents.CommandStarted, {"command": command, "arguments": kwargs})
            try:
                return f(*args, **kwargs)
            except click.Abort:
                # Doesn't seem like this is working any more
                track_cli(
                    CliTrackingEvents.CommandUserAborted,
                    {"command": command, "arguments": kwargs},
                )
            except Exception as e:
                track_cli(CliTrackingEvents.CommandFailed, {"command": command, "arguments": kwargs, "error": str(e)})
                raise e
            finally:
                track_cli(CliTrackingEvents.CommandCompleted, {"command": command, "arguments": kwargs})

        return wrapper  # type: ignore

    return decorator  # type: ignore
