# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["VideoCreateResponse"]


class VideoCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the video job."""
