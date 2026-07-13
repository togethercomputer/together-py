# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ModelResourceListParams"]


class ModelResourceListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination"""

    limit: int
    """Maximum number of resources to return (1-100)"""

    status: List[
        Literal[
            "MODEL_RESOURCES_STATUS_PENDING",
            "MODEL_RESOURCES_STATUS_CREATING",
            "MODEL_RESOURCES_STATUS_READY",
            "MODEL_RESOURCES_STATUS_ERROR",
            "MODEL_RESOURCES_STATUS_STOPPED",
            "MODEL_RESOURCES_STATUS_STOPPING",
        ]
    ]
    """Status filters. When omitted, resources in any status are returned."""
