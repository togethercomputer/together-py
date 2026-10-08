# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .loss_type import LossType
from .dro_loss_params import DroLossParams
from .ppo_loss_params import PpoLossParams
from .dppo_loss_params import DppoLossParams
from .grpo_loss_params import GrpoLossParams
from .cispo_loss_params import CispoLossParams
from .cross_entropy_loss_params import CrossEntropyLossParams

__all__ = ["LossConfig"]


class LossConfig(TypedDict, total=False):
    type: Required[LossType]
    """Type of loss function to use"""

    cispo_params: CispoLossParams

    cross_entropy_params: CrossEntropyLossParams
    """Cross-entropy loss parameters (currently empty)."""

    dppo_params: DppoLossParams
    """Parameters for DPPO loss. Only valid when `type` is `LOSS_TYPE_DPPO`."""

    dro_params: DroLossParams

    grpo_params: GrpoLossParams

    ppo_params: PpoLossParams
