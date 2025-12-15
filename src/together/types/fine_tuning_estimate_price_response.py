# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["FineTuningEstimatePriceResponse"]


class FineTuningEstimatePriceResponse(BaseModel):
    allowed_to_proceed: Optional[bool] = None
    """Whether the user is allowed to proceed with the fine-tuning job"""

    estimated_eval_token_count: Optional[float] = None
    """The estimated number of tokens for evaluation"""

    estimated_total_price: Optional[float] = None
    """The price of the fine-tuning job"""

    estimated_train_token_count: Optional[float] = None
    """The estimated number of tokens to be trained"""

    user_limit: Optional[float] = None
    """The user's credit limit in dollars"""
