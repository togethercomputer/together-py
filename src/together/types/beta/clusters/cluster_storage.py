# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ClusterStorage"]


class ClusterStorage(BaseModel):
    size_tib: int
    """Size of the volume in whole tebibytes (TiB)."""

    status: Literal["available", "bound", "provisioning"]
    """Deployment status of the volume."""

    volume_id: str
    """ID of the volume."""

    volume_name: str
    """Provided name of the volume."""
