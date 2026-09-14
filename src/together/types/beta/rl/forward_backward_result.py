# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ...._models import BaseModel
from .loss_fn_output import LossFnOutput

__all__ = ["ForwardBackwardResult"]


class ForwardBackwardResult(BaseModel):
    """Result of a scored forward or forward-backward operation"""

    loss: float
    """Loss value"""

    loss_fn_outputs: Optional[List[LossFnOutput]] = None
    """Per-sample loss function outputs, in request order.

    Empty unless the request set `return_loss_fn_outputs`.
    """

    metrics: Optional[Dict[str, float]] = None
    """Loss-specific metrics (e.g., KL divergence, clip fraction for GRPO)"""
