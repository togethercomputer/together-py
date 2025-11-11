# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EvalCreateResponse"]


class EvalCreateResponse(BaseModel):
    status: Optional[Literal["pending"]] = None
    """Initial status of the job"""

    workflow_id: Optional[str] = None
    """The ID of the created evaluation job"""
