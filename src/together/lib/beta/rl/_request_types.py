"""Stable handwritten request types shared across generated operation variants."""

from __future__ import annotations

from collections.abc import Mapping
from typing_extensions import Required, TypedDict

from ....types.beta.rl.loss_type import LossType
from ....types.beta.rl.dro_loss_params import DroLossParams
from ....types.beta.rl.ppo_loss_params import PpoLossParams
from ....types.beta.rl.grpo_loss_params import GrpoLossParams
from ....types.beta.rl.cispo_loss_params import CispoLossParams
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.tensor_data_param import TensorDataParam as TensorData
from ....types.beta.rl.routed_experts_param import RoutedExpertsParam
from ....types.beta.rl.cross_entropy_loss_params import CrossEntropyLossParams


class LossConfig(TypedDict, total=False):
    """Loss selector and built-in loss parameters.

    Attributes:
        type: Selects the loss, and with it which ``*_params`` field is read. Setting
            a params field belonging to another loss is rejected client-side: it is
            always a mistake, and the server would otherwise drop it silently.
        cross_entropy_params: Read when ``type`` is ``LOSS_TYPE_CROSS_ENTROPY``.
        grpo_params: Read when ``type`` is ``LOSS_TYPE_GRPO``.
        ppo_params: Read when ``type`` is ``LOSS_TYPE_PPO``.
        cispo_params: Read when ``type`` is ``LOSS_TYPE_CISPO``.
        dro_params: Read when ``type`` is ``LOSS_TYPE_DRO``.
    """

    type: Required[LossType]
    cross_entropy_params: CrossEntropyLossParams
    grpo_params: GrpoLossParams
    ppo_params: PpoLossParams
    cispo_params: CispoLossParams
    dro_params: DroLossParams


class Sample(TypedDict, total=False):
    """One training sample in a forward or forward-backward request.

    Attributes:
        model_input: The tokens the sample is scored against.
        loss_fn_inputs: Per-token loss tensors keyed by their public input names. At runtime
            each value may also be a one-dimensional torch tensor, numpy array, or numeric
            list; the clients coerce it to a ``TensorData`` before submitting. The annotation
            stays narrow, as tinker's own ``LossFnInputs`` does, so a type-checked caller
            passing an array needs a ``cast``.
        routed_experts: Optional per-token expert routing for MoE models.
    """

    model_input: Required[ModelInput]
    loss_fn_inputs: Required[Mapping[str, TensorData]]
    routed_experts: RoutedExpertsParam
