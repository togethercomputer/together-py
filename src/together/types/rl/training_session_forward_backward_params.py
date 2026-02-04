# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "TrainingSessionForwardBackwardParams",
    "Body",
    "BodySample",
    "BodySampleLossFnInputs",
    "BodySampleLossFnInputsTargetTokens",
    "BodySampleLossFnInputsWeights",
    "BodySampleModelInput",
    "BodySampleModelInputChunk",
    "BodySampleModelInputChunkEncodedText",
]


class TrainingSessionForwardBackwardParams(TypedDict, total=False):
    body: Required[Body]


class BodySampleLossFnInputsTargetTokens(TypedDict, total=False):
    """Target tokens for loss computation"""

    data: Required[Iterable[float]]
    """Integer array of target tokens"""

    dtype: Literal["D_TYPE_UNSPECIFIED", "D_TYPE_INT64", "D_TYPE_FLOAT32", "D_TYPE_BFLOAT16"]
    """Data type of the integer array"""


class BodySampleLossFnInputsWeights(TypedDict, total=False):
    """Per-token weights"""

    data: Required[Iterable[float]]
    """Float array of per-token weights"""

    dtype: Literal["D_TYPE_UNSPECIFIED", "D_TYPE_INT64", "D_TYPE_FLOAT32", "D_TYPE_BFLOAT16"]
    """Data type of the float array"""


class BodySampleLossFnInputs(TypedDict, total=False):
    """Loss function inputs"""

    target_tokens: Required[BodySampleLossFnInputsTargetTokens]
    """Target tokens for loss computation"""

    weights: Required[BodySampleLossFnInputsWeights]
    """Per-token weights"""


class BodySampleModelInputChunkEncodedText(TypedDict, total=False):
    tokens: Iterable[int]
    """Pre-tokenized text input"""


class BodySampleModelInputChunk(TypedDict, total=False):
    encoded_text: BodySampleModelInputChunkEncodedText


class BodySampleModelInput(TypedDict, total=False):
    """Model input"""

    chunks: Required[Iterable[BodySampleModelInputChunk]]
    """Input chunks for the model"""


class BodySample(TypedDict, total=False):
    loss_fn_inputs: Required[BodySampleLossFnInputs]
    """Loss function inputs"""

    model_input: Required[BodySampleModelInput]
    """Model input"""


class Body(TypedDict, total=False):
    loss_fn: Required[Literal["LOSS_FN_UNSPECIFIED", "LOSS_FN_GRPO"]]
    """Loss function to use for gradient computation"""

    samples: Required[Iterable[BodySample]]
    """Batch of training samples to process"""
