# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr
from .loss_config_param import LossConfigParam
from .loss_inputs_param import LossInputsParam
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = [
    "OperationForwardBackwardParams",
    "Sample",
    "SampleModelInput",
    "SampleModelInputChunk",
    "SampleModelInputChunkEncodedText",
]


class OperationForwardBackwardParams(TypedDict, total=False):
    loss: Required[LossConfigParam]
    """Loss function configuration"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples to process"""


class SampleModelInputChunkEncodedText(TypedDict, total=False):
    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""


class SampleModelInputChunk(TypedDict, total=False):
    encoded_text: SampleModelInputChunkEncodedText


class SampleModelInput(TypedDict, total=False):
    """Model input"""

    chunks: Required[Iterable[SampleModelInputChunk]]
    """Input chunks for the model"""


class Sample(TypedDict, total=False):
    loss_inputs: Required[LossInputsParam]
    """Loss function inputs"""

    model_input: Required[SampleModelInput]
    """Model input"""

    policy_segments: Required[Iterable[PolicyVersionSegmentParam]]
    """Policy versions associated with this sample's tokens"""
