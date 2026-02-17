# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .secret import Secret
from ...._models import BaseModel

__all__ = ["SecretListResponse"]


class SecretListResponse(BaseModel):
    data: Optional[List[Secret]] = None
    """Data is the array of secret items"""

    object: Optional[Literal["list"]] = None
    """The object type, which is always `list`."""
