# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .loss_logprobs_param import LossLogprobsParam
from .loss_advantages_param import LossAdvantagesParam

__all__ = ["GrpoLossInputsParam"]


class GrpoLossInputsParam(TypedDict, total=False):
    advantages: Required[LossAdvantagesParam]
    """Per-token advantages for GRPO"""

    logprobs: Required[LossLogprobsParam]
    """Log probabilities for GRPO"""

    reference_logprobs: LossLogprobsParam
    """Reference model log probabilities (required if beta > 0)"""
