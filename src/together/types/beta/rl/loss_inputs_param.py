# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .weights_param import Weights
from .dro_loss_inputs_param import DroLossInputs
from .ppo_loss_inputs_param import PpoLossInputs
from .grpo_loss_inputs_param import GrpoLossInputs
from .cispo_loss_inputs_param import CispoLossInputs
from .loss_target_tokens_param import LossTargetTokens
from .routed_experts_param_param import RoutedExpertsParam
from .importance_sampling_loss_inputs_param import ImportanceSamplingLossInputs

__all__ = ["LossInputs"]


class LossInputs(TypedDict, total=False):
    """Token-level inputs used to compute the loss for one training sample."""

    target_tokens: Required[LossTargetTokens]
    """Target tokens for loss computation"""

    cispo_inputs: CispoLossInputs

    dro_inputs: DroLossInputs

    grpo_inputs: GrpoLossInputs
    """Inputs required when the loss type is GRPO"""

    importance_sampling_inputs: ImportanceSamplingLossInputs
    """Inputs required when the loss type is importance sampling"""

    ppo_inputs: PpoLossInputs

    routed_experts: RoutedExpertsParam
    """Optional MoE per-token routing captured at sample time.

    Replayed on every training operation, so expert selection matches the one used
    at sample time. Must cover the whole sample, or all but its last token.
    """

    weights: Weights
    """Per-token loss weights (>= 0), one weight per target token.

    Required for cross-entropy, which honors fractional weights; other loss types
    treat weights as a 0/1 mask.
    """
