# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from .model_input_param import ModelInput
from .tensor_data_param_param import TensorDataParam
from .routed_experts_param_param import RoutedExpertsParam

__all__ = ["OperationForwardParams", "Sample"]


class OperationForwardParams(TypedDict, total=False):
    samples: Required[Iterable[Sample]]
    """Batch of training samples for which to compute per-token log-probabilities"""


class Sample(TypedDict, total=False):
    loss_fn_inputs: Required[Dict[str, TensorDataParam]]
    """Per-token loss tensors keyed by name.

    Include `target_tokens` and the inputs required by the selected loss. Each
    tensor must declare `int64` or `float32`, be one-dimensional, and have the same
    length.
    """

    model_input: Required[ModelInput]
    """Model input"""

    routed_experts: RoutedExpertsParam
    """Optional MoE per-token routing captured at sample time.

    Replayed on every training operation, so expert selection matches the one used
    at sample time. Must cover the whole sample, or all but its last token.
    """
