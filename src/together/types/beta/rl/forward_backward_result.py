# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ...._models import BaseModel

__all__ = ["ForwardBackwardResult"]


class ForwardBackwardResult(BaseModel):
    """Result of a forward-backward pass operation"""

    loss: float
    """Loss value"""

    metrics: Optional[Dict[str, float]] = None
    """Loss-specific metrics (e.g., KL divergence, clip fraction for GRPO)"""
