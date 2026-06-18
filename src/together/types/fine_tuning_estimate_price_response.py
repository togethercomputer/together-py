# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["FineTuningEstimatePriceResponse", "AvailableEstimate", "UnavailableEstimate"]


class AvailableEstimate(BaseModel):
    estimation_available: Literal[True]
    """Whether price estimation is available for the requested fine-tune job."""

    allowed_to_proceed: Optional[bool] = None
    """Whether you are allowed to proceed with the fine-tuning job."""

    estimated_eval_token_count: Optional[float] = None
    """The estimated number of tokens for evaluation"""

    estimated_total_price: Optional[float] = None
    """The price of the fine-tuning job"""

    estimated_train_token_count: Optional[float] = None
    """The estimated number of tokens to be trained"""

    user_limit: Optional[float] = None
    """Your credit limit in dollars."""


class UnavailableEstimate(BaseModel):
    estimation_available: Literal[False]
    """Whether price estimation is available for the requested fine-tune job."""

    unavailable_reason: str
    """Reason price estimation is unavailable for the requested fine-tune job."""


FineTuningEstimatePriceResponse: TypeAlias = Union[AvailableEstimate, UnavailableEstimate]
