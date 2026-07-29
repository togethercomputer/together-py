# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["SessionListParams"]


class SessionListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination (ID of the last session from the previous page)"""

    created_by: str
    """Filter sessions in the current project by the creator ID.

    Pass "me" to show sessions you created.
    """

    limit: int
    """Maximum number of sessions to return (1-100)"""

    model_resources_id: str
    """Filter sessions by the model resource they are attached to"""

    status: List[
        Literal[
            "TRAINING_SESSION_STATUS_CREATING",
            "TRAINING_SESSION_STATUS_RUNNING",
            "TRAINING_SESSION_STATUS_STOPPED",
            "TRAINING_SESSION_STATUS_STOPPING",
            "TRAINING_SESSION_STATUS_ERROR",
            "TRAINING_SESSION_STATUS_EXPIRED",
        ]
    ]
    """Status filters. When omitted, sessions in any status are returned."""
