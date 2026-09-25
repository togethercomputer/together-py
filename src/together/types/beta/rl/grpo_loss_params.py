# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .grpo_loss_ratio_type import GrpoLossRatioType
from .grpo_loss_aggregation_type import GrpoLossAggregationType

__all__ = ["GrpoLossParams"]


class GrpoLossParams(TypedDict, total=False):
    agg_type: GrpoLossAggregationType
    """Aggregation type for loss computation"""

    beta: float
    """KL penalty coefficient"""

    clip_high_threshold: float
    """Upper clip threshold for the importance-sampling ratio.

    The ratio is clamped to this bound; tighter clipping makes policy updates more
    conservative. Must be >= 1.
    """

    clip_low_threshold: float
    """Lower clip threshold for the importance-sampling ratio.

    The ratio is clamped to this bound; tighter clipping makes policy updates more
    conservative. Must be <= 1.
    """

    ratio_type: GrpoLossRatioType
    """Controls how the importance-sampling ratio is computed in GRPO loss.

    Defaults to token-level ratios, which is the standard GRPO behavior. Use
    sequence-level ratios to enable GSPO-style loss calculation instead.
    """
