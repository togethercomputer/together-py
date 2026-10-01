# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .deployment_revision_event import DeploymentRevisionEvent

__all__ = ["DeploymentRevisionEventList"]


class DeploymentRevisionEventList(BaseModel):
    """Revision history events for a deployment, newest first."""

    data: List[DeploymentRevisionEvent]
    """Revision events, newest first."""

    object: Literal["list"]
    """The object type, which is always `list`."""
