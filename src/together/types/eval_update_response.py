# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["EvalUpdateResponse"]


class EvalUpdateResponse(BaseModel):
    status: Optional[str] = None

    workflow_id: Optional[str] = None
