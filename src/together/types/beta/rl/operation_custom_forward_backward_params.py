# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr
from .loss_inputs_param import LossInputsParam
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = [
    "OperationCustomForwardBackwardParams",
    "Gradient",
    "Sample",
    "SampleModelInput",
    "SampleModelInputChunk",
    "SampleModelInputChunkEncodedText",
]


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

    policy_segments: Iterable[PolicyVersionSegmentParam]
    """Policy versions that produced this sample's tokens.

    Echo back from `SampleResult.policy_segments`.
    """
