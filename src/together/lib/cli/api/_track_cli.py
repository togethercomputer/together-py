
from enum import Enum
from typing import Any
from datetime import datetime
import threading
import uuid
import httpx
import json
import os

from together import __version__

ANALYTICS_API_ENV_VAR = os.getenv("TOGETHER_TELEMETRY_API")
# ANALYTICS_API = ANALYTICS_API_ENV_VAR if ANALYTICS_API_ENV_VAR else "https://api.together.ai/v0/cli-events"
ANALYTICS_API = ANALYTICS_API_ENV_VAR if ANALYTICS_API_ENV_VAR else "http://localhost:3000/v0/cli-events"

SESSION_ID = uuid.uuid4()

def is_tracking_enabled() -> bool:
    return True

class TrackingEvents(Enum):
    CLI_COMMAND_STARTED = "CLI_COMMAND_STARTED"
    CLI_COMMAND_COMPLETED = "CLI_COMMAND_COMPLETED"
    CLI_COMMAND_FAILED = "CLI_COMMAND_FAILED"


def _track_cli_async(event_name: TrackingEvents, args: Any) -> None:
    client = httpx.Client()

    client.post(
        ANALYTICS_API,
        headers={
            "content-type": "application/json",
            "user-agent": f"together-cli:{__version__}"
        },
        content=json.dumps({
            "event_name": event_name,
            "event_properties": args,
            "event_options": {
                "time": datetime.now().isoformat(),
                "session_id": str(SESSION_ID),
                "device_id": "", # todo: get machine id
            }
        })
    )

def track_cli(event_name: TrackingEvents, args: Any) -> None:
    if is_tracking_enabled() == False:
        return

    threading.Thread(target=_track_cli_async, args=(event_name, args)).start()
