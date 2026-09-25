# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .loss_config_param import LossConfig
from .model_input_param import ModelInput
from .tensor_data_param import TensorDataParam

__all__ = ["OperationForwardBackwardParams", "Sample"]


class OperationForwardBackwardParams(TypedDict, total=False):
    loss: Required[LossConfig]
    """Loss function configuration"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples to process"""

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="Idempotency-Key")]]
    """
    Required key that makes retries return the original operation; use a new key for
    changed request bodies.
    """

    forward_only: bool
    """
    Run the forward pass only: report the loss and metrics, and the per-sample
    outputs when requested, without accumulating gradients. Defaults to false. Pair
    it with `return_loss_fn_outputs` to score a batch and read back its per-token
    log-probabilities.
    """

    return_loss_fn_outputs: bool
    """
    Return the loss function's per-sample output tensors alongside the loss and
    metrics. Defaults to false. Enabling it increases the response size
    substantially for large batches and reduces step throughput, so leave it unset
    for ordinary training steps.
    """


class Sample(TypedDict, total=False):
    loss_fn_inputs: Required[Dict[str, TensorDataParam]]
    """Per-token loss tensors keyed by name.

    Include `target_tokens` and the inputs required by the selected loss. Each
    tensor must declare `int64` or `float32`, be one-dimensional, and have the same
    length.
    """

    model_input: Required[ModelInput]
    """Model input"""

    routed_experts_key: str
    """Opaque key returned with a sampled sequence.

    Pass it unchanged with the corresponding training sample to reuse the same
    expert selections. The selections must cover the entire training sample or all
    but its final token. Training fails if the key is no longer available.
    """
