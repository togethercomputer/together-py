# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType
from .model_input_param import ModelInput
from .tensor_data_param import TensorData
from .routed_experts_param_param import RoutedExpertsParam

__all__ = ["OperationCustomForwardBackwardParams", "Gradient", "Sample"]


class OperationCustomForwardBackwardParams(TypedDict, total=False):
    gradients: Required[Iterable[Gradient]]
    """Per-sample per-token gradients of the loss with respect to log-probabilities"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples"""


class Gradient(TypedDict, total=False):
    """Per-token gradients of the loss with respect to target log-probabilities"""

    data: Required[Iterable[float]]
    """Float array of per-token gradients (d loss / d log p)"""

    dtype: DType
    """Data type of the float array"""


class Sample(TypedDict, total=False):
    loss_fn_inputs: Required[Dict[str, TensorData]]
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
