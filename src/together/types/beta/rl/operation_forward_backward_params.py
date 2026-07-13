# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr
from .loss_type import LossType
from .grpo_loss_aggregation_type import GrpoLossAggregationType
from .policy_version_segment_param import PolicyVersionSegmentParam

__all__ = [
    "OperationForwardBackwardParams",
    "Loss",
    "LossGrpoParams",
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


class OperationForwardBackwardParams(TypedDict, total=False):
    loss: Required[Loss]
    """Loss function configuration"""

    samples: Required[Iterable[Sample]]
    """Batch of training samples to process"""


class LossGrpoParams(TypedDict, total=False):
    agg_type: GrpoLossAggregationType
    """Aggregation type for loss computation"""

    beta: float
    """KL penalty coefficient"""

    clip_high: float
    """Upper clip bound for importance ratio"""

    clip_low: float
    """Lower clip bound for importance ratio"""

    ratio_type: Literal["GRPO_LOSS_RATIO_TYPE_TOKEN", "GRPO_LOSS_RATIO_TYPE_SEQUENCE"]
    """Controls how the importance-sampling ratio is computed in GRPO loss.

    Defaults to token-level ratios, which is the standard GRPO behavior. Use
    sequence-level ratios to enable GSPO-style loss calculation instead.
    """


class Loss(TypedDict, total=False):
    """Loss function configuration"""

    type: Required[LossType]
    """Type of loss function to use"""

    cross_entropy_params: object
    """Cross-entropy loss parameters (currently empty)."""

    grpo_params: LossGrpoParams


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
