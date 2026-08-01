# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType
from .loss_inputs_param import LossInputs
from .model_input_param import ModelInput
from .policy_version_segment_param import PolicyVersionSegmentParam

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
    loss_inputs: Required[LossInputs]
    """Loss function inputs"""

    model_input: Required[ModelInput]
    """Model input"""

    policy_segments: Required[Iterable[PolicyVersionSegmentParam]]
    """Policy versions associated with this sample's tokens"""
