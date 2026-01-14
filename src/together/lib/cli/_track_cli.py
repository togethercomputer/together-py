
import os
import json
import uuid
import threading
from enum import Enum
from typing import Any, TypeVar, Callable
from datetime import datetime
from functools import wraps

import click
import httpx
import machineid

from together import __version__

F = TypeVar("F", bound=Callable[..., Any])

SESSION_ID = uuid.uuid4()

def is_tracking_enabled() -> bool:
    # TODO: add a way to disable tracking
    return True

class TrackingEvents(Enum):
    CLI_COMMAND_STARTED = "CLI_COMMAND_STARTED"
    CLI_COMMAND_COMPLETED = "CLI_COMMAND_COMPLETED"
    CLI_COMMAND_FAILED = "CLI_COMMAND_FAILED"
    CLI_COMMAND_USER_ABORTED = "CLI_COMMAND_USER_ABORTED"


def track_cli(event_name: TrackingEvents, args: Any) -> None:
    """ Track a CLI event. Non-Blocking. """
    if is_tracking_enabled() == False:
        return

    def send_event() -> None:
        ANALYTICS_API_ENV_VAR = os.getenv("TOGETHER_TELEMETRY_API")
        # ANALYTICS_API = ANALYTICS_API_ENV_VAR if ANALYTICS_API_ENV_VAR else "https://api.together.ai/v0/cli-events"
        ANALYTICS_API = ANALYTICS_API_ENV_VAR if ANALYTICS_API_ENV_VAR else "http://localhost:3000/api/together-cli-events"

        try:
            client = httpx.Client()
            client.post(
                ANALYTICS_API,
                headers={
                    "content-type": "application/json",
                    "user-agent": f"together-cli:{__version__}"
                },
                content=json.dumps({
                    "event_name": event_name.value,
                    "event_properties": args,
                    "event_options": {
                        "time": datetime.now().isoformat(),
                        "session_id": str(SESSION_ID),
                        "device_id": machineid.id(),
                    }
                })
            )
        except Exception:
            # No-op - this is not critical and we don't want to block the CLI
            pass

    threading.Thread(target=send_event).start()


def auto_track_command(command: str) -> Callable[[F], F]:
    """ Decorator for click commands to automatically track CLI commands start/completion/failure. """

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            track_cli(TrackingEvents.CLI_COMMAND_STARTED, { "command": command, "arguments": kwargs })
            try:
                return f(*args, **kwargs)
            except click.Abort:
                track_cli(TrackingEvents.CLI_COMMAND_USER_ABORTED, { "command": command, "arguments": kwargs, "error": "User aborted command" })
            except Exception as e:
                track_cli(TrackingEvents.CLI_COMMAND_FAILED, { "command": command, "arguments": kwargs, "error": e })
                raise e
            finally:
                track_cli(TrackingEvents.CLI_COMMAND_COMPLETED, { "command": command, "arguments": kwargs })
        return wrapper # type: ignore
    return decorator # type: ignore