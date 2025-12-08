# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EndpointListResponse", "Data"]


class Data(BaseModel):
    """Details about an endpoint when listed via the list endpoint"""

    id: str
    """Unique identifier for the endpoint"""

    created_at: datetime
    """Timestamp when the endpoint was created"""

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

    type: Literal["serverless", "dedicated"]
    """The type of endpoint"""


class EndpointListResponse(BaseModel):
    data: List[Data]

    object: Literal["list"]
