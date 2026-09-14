# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .deployment import Deployment

__all__ = ["JigListResponse"]


class JigListResponse(BaseModel):
    data: Optional[List[Deployment]] = None
    """Data is the array of deployment items"""

    object: Optional[Literal["list"]] = None
    """The object type, which is always `list`."""
