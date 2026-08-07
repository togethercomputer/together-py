# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .sampling_params import SamplingParams
from .model_input_param import ModelInput

__all__ = ["OperationSampleParams"]


class OperationSampleParams(TypedDict, total=False):
    model_inputs: Required[Iterable[ModelInput]]
    """Model inputs to sample from"""

    num_samples: int
    """Number of completions to generate per prompt"""

    prompt_logprobs: bool
    """
    When true, also compute teacher-forced log-probabilities for the model input
    tokens and return them in `SampleResult.prompt_logprobs`.
    """

    return_routed_experts: bool
    """
    When true, capture the mixture-of-experts routing decisions made while
    generating and return them in `SampledSequence.routed_experts`, so training can
    reuse the same expert selection. Only available on mixture-of-experts models;
    ignored otherwise. The captured buffer scales with sequence length, so leave it
    off unless you replay routing during training.
    """

    sampling_params: SamplingParams
    """Optional sampling parameters"""

    topk_prompt_logprobs: int
    """
    Number of most likely alternative tokens to return per model input token in
    `SampleResult.topk_prompt_logprobs`. 0 disables top-k prompt log-probabilities.
    Maximum 20.
    """
