# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = [
    "OperationForwardParams",
    "Sample",
    "SampleLossInputs",
    "SampleLossInputsTargetTokens",
    "SampleLossInputsGrpoInputs",
    "SampleLossInputsGrpoInputsAdvantages",
    "SampleLossInputsGrpoInputsGeneratorLogprobs",
    "SampleLossInputsGrpoInputsReferenceLogprobs",
    "SampleLossInputsLossMask",
    "SampleModelInput",
    "SampleModelInputChunk",
    "SampleModelInputChunkEncodedText",
]


class OperationForwardParams(TypedDict, total=False):
    samples: Required[Iterable[Sample]]
    """Batch of training samples for which to compute per-token log-probabilities"""


class SampleLossInputsTargetTokens(TypedDict, total=False):
    """Target tokens for loss computation"""

    data: Required[SequenceNotStr[Union[str, int]]]
    """Integer array of target tokens"""

    dtype: DType
    """Data type of the integer array"""


class SampleLossInputsGrpoInputsAdvantages(TypedDict, total=False):
    """Per-token advantages for GRPO"""

    data: Required[Iterable[float]]
    """Float array of per-token advantages"""

    dtype: DType
    """Data type of the float array (D_TYPE_FLOAT32 or D_TYPE_BFLOAT16)"""


class SampleLossInputsGrpoInputsGeneratorLogprobs(TypedDict, total=False):
    """Generator log probabilities for GRPO"""

    data: Required[Iterable[float]]
    """Float array of per-token log probabilities"""

    dtype: DType
    """Data type of the float array (D_TYPE_FLOAT32 or D_TYPE_BFLOAT16)"""


class SampleLossInputsGrpoInputsReferenceLogprobs(TypedDict, total=False):
    """Reference model log probabilities (required if beta > 0)"""

    data: Required[Iterable[float]]
    """Float array of per-token log probabilities"""

    dtype: DType
    """Data type of the float array (D_TYPE_FLOAT32 or D_TYPE_BFLOAT16)"""


class SampleLossInputsGrpoInputs(TypedDict, total=False):
    advantages: Required[SampleLossInputsGrpoInputsAdvantages]
    """Per-token advantages for GRPO"""

    generator_logprobs: Required[SampleLossInputsGrpoInputsGeneratorLogprobs]
    """Generator log probabilities for GRPO"""

    reference_logprobs: SampleLossInputsGrpoInputsReferenceLogprobs
    """Reference model log probabilities (required if beta > 0)"""


class SampleLossInputsLossMask(TypedDict, total=False):
    """Per-token loss mask (1=compute loss, 0=ignore)"""

    data: Required[SequenceNotStr[Union[str, int]]]
    """Integer array of per-token mask values (0s and 1s)"""

    dtype: DType
    """Data type of the integer array (must be D_TYPE_INT64)"""


class SampleLossInputs(TypedDict, total=False):
    """Loss function inputs"""

    target_tokens: Required[SampleLossInputsTargetTokens]
    """Target tokens for loss computation"""

    grpo_inputs: SampleLossInputsGrpoInputs

    loss_mask: SampleLossInputsLossMask
    """Per-token loss mask (1=compute loss, 0=ignore)"""


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
    loss_inputs: Required[SampleLossInputs]
    """Loss function inputs"""

    model_input: Required[SampleModelInput]
    """Model input"""

    policy_segments: Iterable[PolicyVersionSegmentParam]
    """Policy versions that produced this sample's tokens.

    Echo back from `SampleResult.policy_segments`.
    """
