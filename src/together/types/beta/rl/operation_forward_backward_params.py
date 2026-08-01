# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .loss_config_param import LossConfig
from .loss_inputs_param import LossInputs
from .model_input_param import ModelInput
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = ["OperationForwardBackwardParams", "Sample"]


class OperationForwardBackwardParams(TypedDict, total=False):
    loss: Required[LossConfig]
    """Loss function configuration"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples to process"""


class Sample(TypedDict, total=False):
    loss_inputs: Required[LossInputs]
    """Loss function inputs"""

    model_input: Required[ModelInput]
    """Model input"""

    policy_segments: Required[Iterable[PolicyVersionSegmentParam]]
    """Policy versions associated with this sample's tokens"""
