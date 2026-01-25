# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .deployment import Deployment

__all__ = ["JigListResponse"]


class JigListResponse(BaseModel):
    data: Optional[List[Deployment]] = None
    """Data is the array of deployment items"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "list")"""
