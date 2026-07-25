# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .loss_inputs_param import LossInputsParam
from .model_input_param import ModelInput
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = ["OperationForwardParams", "Sample"]


class OperationForwardParams(TypedDict, total=False):
    samples: Required[Iterable[Sample]]
    """Batch of training samples for which to compute per-token log-probabilities"""


class Sample(TypedDict, total=False):
    loss_inputs: Required[LossInputsParam]
    """Loss function inputs"""

    model_input: Required[ModelInput]
    """Model input"""

    policy_segments: Required[Iterable[PolicyVersionSegmentParam]]
    """Policy versions associated with this sample's tokens"""
