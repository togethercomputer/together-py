# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ClusterStorage"]


class ClusterStorage(BaseModel):
    size_tib: int

    status: Literal[
        "scheduled", "available", "bound", "provisioning", "deleting", "failed", "access_revoked", "unknown"
    ]
    """Current status of the shared volume."""

    volume_id: str

    volume_name: str
