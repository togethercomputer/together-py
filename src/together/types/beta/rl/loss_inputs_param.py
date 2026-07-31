# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .weights_param import WeightsParam
from .dro_loss_inputs_param import DroLossInputsParam
from .ppo_loss_inputs_param import PpoLossInputsParam
from .grpo_loss_inputs_param import GrpoLossInputsParam
from .cispo_loss_inputs_param import CispoLossInputsParam
from .loss_target_tokens_param import LossTargetTokensParam
from .importance_sampling_loss_inputs_param import ImportanceSamplingLossInputsParam

__all__ = ["LossInputsParam"]


class LossInputsParam(TypedDict, total=False):
    """Token-level inputs used to compute the loss for one training sample."""

    target_tokens: Required[LossTargetTokensParam]
    """Target tokens for loss computation"""

    cispo_inputs: CispoLossInputsParam

    dro_inputs: DroLossInputsParam

    grpo_inputs: GrpoLossInputsParam
    """Inputs required when the loss type is GRPO"""

    importance_sampling_inputs: ImportanceSamplingLossInputsParam
    """Inputs required when the loss type is importance sampling"""

    ppo_inputs: PpoLossInputsParam

    weights: WeightsParam
    """Per-token weights (1=compute loss, 0=ignore)."""
