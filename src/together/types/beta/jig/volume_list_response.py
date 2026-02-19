# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .volume import Volume
from ...._models import BaseModel

__all__ = ["VolumeListResponse"]


class VolumeListResponse(BaseModel):
    data: Optional[List[Volume]] = None
    """Data is the array of volume items"""

    object: Optional[Literal["list"]] = None
    """The object type, which is always `list`."""
