# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .autoscaling import Autoscaling

__all__ = ["DedicatedEndpoint"]


class DedicatedEndpoint(BaseModel):
    """Details about a dedicated endpoint deployment"""

    id: str
    """Unique identifier for the endpoint"""

    autoscaling: Autoscaling
    """Configuration for automatic scaling of the endpoint"""

    created_at: datetime
    """Timestamp when the endpoint was created"""

    display_name: str
    """Human-readable name for the endpoint"""

    hardware: str
    """The hardware configuration used for this endpoint"""

    model: str
    """The model deployed on this endpoint"""

    name: str
    """System name for the endpoint"""

    object: Literal["endpoint"]
    """The type of object"""

    owner: str
    """The owner of this endpoint"""

    state: Literal["PENDING", "STARTING", "STARTED", "STOPPING", "STOPPED", "ERROR"]
    """Current state of the endpoint"""

    type: Literal["dedicated"]
    """The type of endpoint"""
