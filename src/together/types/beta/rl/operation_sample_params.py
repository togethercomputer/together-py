# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .sampling_params import SamplingParams
from .model_input_param import ModelInputParam

__all__ = ["OperationSampleParams"]


class OperationSampleParams(TypedDict, total=False):
    model_inputs: Required[Iterable[ModelInputParam]]
    """Model inputs to sample from"""

    num_samples: int
    """Number of completions to generate per prompt"""

    prompt_logprobs: bool
    """
    When true, also compute teacher-forced log-probabilities for the model input
    tokens and return them in `SampleResult.prompt_logprobs`.
    """

    sampling_params: SamplingParams
    """Optional sampling parameters"""

    topk_prompt_logprobs: int
    """
    Number of most likely alternative tokens to return per model input token in
    `SampleResult.topk_prompt_logprobs`. 0 disables top-k prompt log-probabilities.
    Maximum 20.
    """
