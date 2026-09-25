# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .d_type import DType
from ...._utils import PropertyInfo
from .model_input_param import ModelInput
from .tensor_data_param import TensorDataParam

__all__ = ["OperationCustomForwardBackwardParams", "Gradient", "Sample"]


class OperationCustomForwardBackwardParams(TypedDict, total=False):
    gradients: Required[Iterable[Gradient]]
    """Per-sample per-token gradients of the loss with respect to log-probabilities"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples"""

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="Idempotency-Key")]]
    """
    Required key that makes retries return the original operation; use a new key for
    changed request bodies.
    """


class Gradient(TypedDict, total=False):
    """Per-token gradients of the loss with respect to target log-probabilities"""

    data: Required[Iterable[float]]
    """Float array of per-token gradients (d loss / d log p)"""

    dtype: DType
    """Data type of the float array"""


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
