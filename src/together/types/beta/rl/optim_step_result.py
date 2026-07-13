# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from ...._models import BaseModel

__all__ = ["OptimStepResult"]


class OptimStepResult(BaseModel):
    """Result of an optimizer step operation"""

    step: Union[str, int]
    """Step number"""
