# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .inference_instance_type import InferenceInstanceType

__all__ = ["HardwareListResponse"]


class HardwareListResponse(BaseModel):
    """Hardware instance types available for inference deployments."""

    data: List[InferenceInstanceType]
    """Instance types available for inference."""

    object: Literal["list"]
    """Object type. Always `list`."""

    next_cursor: Optional[str] = None
    """Cursor for the next page.

    Always null today because this catalog is returned in full.
    """
