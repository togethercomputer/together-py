# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DeploymentRevisionEvent"]


class DeploymentRevisionEvent(BaseModel):
    """One entry in a deployment's revision history."""

    action: Literal["create", "update", "system", "rollback"]
    """How this revision became active."""

    activated_at: datetime
    """Time when this revision became active."""

    event_number: int
    """Monotonic event number in the deployment's revision history."""

    image: str
    """Container image of the revision activated by this event."""

    object: Literal["revision_event"]
    """The object type, which is always `revision_event`."""

    revision_id: str
    """Revision ID activated by this event."""

    revision_number: int
    """Human-readable per-deployment revision counter."""
