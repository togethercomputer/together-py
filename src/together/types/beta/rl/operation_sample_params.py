# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .sampling_params import SamplingParams
from .model_input_param import ModelInput

__all__ = ["OperationSampleParams"]


class OperationSampleParams(TypedDict, total=False):
    model_inputs: Required[Iterable[ModelInput]]
    """Model inputs to sample from"""

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="Idempotency-Key")]]
    """
    Required key that makes retries return the original operation; use a new key for
    changed request bodies.
    """

    num_samples: int
    """Number of completions to generate per prompt"""

    prompt_logprobs: bool
    """
    When true, also compute teacher-forced log-probabilities for the model input
    tokens and return them in `SampleResult.prompt_logprobs`.
    """

    return_routed_experts: bool
    """
    When true, enable reuse of the expert selections from sampled sequences during
    training. Only supported for mixture-of-experts models; ignored for other
    models.
    """

    sampling_params: SamplingParams
    """Optional sampling parameters"""

    topk_prompt_logprobs: int
    """
    Number of most likely alternative tokens to return per model input token in
    `SampleResult.topk_prompt_logprobs`. 0 disables top-k prompt log-probabilities.
    Maximum 20.
    """
