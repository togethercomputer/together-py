from __future__ import annotations

from typing import List, cast
from typing_extensions import Literal, TypeAlias

from together import Omit, omit
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils._console import console

ResourceStatusName: TypeAlias = Literal["pending", "creating", "ready", "error", "stopped", "stopping"]
SessionStatusName: TypeAlias = Literal["creating", "running", "stopped", "stopping", "error", "expired"]

ResourceStatusQuery: TypeAlias = Literal[
    "MODEL_RESOURCES_STATUS_PENDING",
    "MODEL_RESOURCES_STATUS_CREATING",
    "MODEL_RESOURCES_STATUS_READY",
    "MODEL_RESOURCES_STATUS_ERROR",
    "MODEL_RESOURCES_STATUS_STOPPED",
    "MODEL_RESOURCES_STATUS_STOPPING",
]
SessionStatusQuery: TypeAlias = Literal[
    "TRAINING_SESSION_STATUS_CREATING",
    "TRAINING_SESSION_STATUS_RUNNING",
    "TRAINING_SESSION_STATUS_STOPPED",
    "TRAINING_SESSION_STATUS_STOPPING",
    "TRAINING_SESSION_STATUS_ERROR",
    "TRAINING_SESSION_STATUS_EXPIRED",
]

_RESOURCE_STATUS: dict[ResourceStatusName, ResourceStatusQuery] = {
    "pending": "MODEL_RESOURCES_STATUS_PENDING",
    "creating": "MODEL_RESOURCES_STATUS_CREATING",
    "ready": "MODEL_RESOURCES_STATUS_READY",
    "error": "MODEL_RESOURCES_STATUS_ERROR",
    "stopped": "MODEL_RESOURCES_STATUS_STOPPED",
    "stopping": "MODEL_RESOURCES_STATUS_STOPPING",
}
_SESSION_STATUS: dict[SessionStatusName, SessionStatusQuery] = {
    "creating": "TRAINING_SESSION_STATUS_CREATING",
    "running": "TRAINING_SESSION_STATUS_RUNNING",
    "stopped": "TRAINING_SESSION_STATUS_STOPPED",
    "stopping": "TRAINING_SESSION_STATUS_STOPPING",
    "error": "TRAINING_SESSION_STATUS_ERROR",
    "expired": "TRAINING_SESSION_STATUS_EXPIRED",
}


def require_positive_limit(limit: int | None) -> None:
    if limit is not None and limit < 1:
        console.print("[red]×[/red] --limit must be at least 1.")
        raise CliDiagnosticExit("--limit must be at least 1")


def resource_status_query(values: list[ResourceStatusName] | None) -> List[ResourceStatusQuery] | Omit:
    if not values:
        return omit
    return cast(List[ResourceStatusQuery], [_RESOURCE_STATUS[value] for value in values])


def session_status_query(values: list[SessionStatusName] | None) -> List[SessionStatusQuery] | Omit:
    if not values:
        return omit
    return cast(List[SessionStatusQuery], [_SESSION_STATUS[value] for value in values])
