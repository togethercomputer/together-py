# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .secret import Secret
from ...._models import BaseModel

__all__ = ["SecretListResponse"]


class SecretListResponse(BaseModel):
    data: Optional[List[Secret]] = None
    """Data is the array of secret items"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "list")"""
