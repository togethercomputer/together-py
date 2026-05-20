# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ClusterStorage"]


class ClusterStorage(BaseModel):
    size_tib: int
    """Size of the volume in TiB."""

    status: Literal[
        "scheduled", "available", "bound", "provisioning", "deleting", "failed", "access_revoked", "unknown"
    ]
    """Current status of the shared volume."""

    volume_id: str
    """ID of the volume."""

    volume_name: str
    """User provided name of the volume."""
