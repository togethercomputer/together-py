# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .loss_logprobs_param import LossLogprobs
from .loss_advantages_param import LossAdvantages

__all__ = ["PpoLossInputs"]


class PpoLossInputs(TypedDict, total=False):
    advantages: Required[LossAdvantages]
    """Per-token advantages for PPO"""

    logprobs: Required[LossLogprobs]
    """Log probabilities for PPO"""
