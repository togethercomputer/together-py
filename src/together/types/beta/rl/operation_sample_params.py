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

    sampling_params: SamplingParams
    """Optional sampling parameters"""
