# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .sampled_sequence import SampledSequence
from .prompt_top_logprobs import PromptTopLogprobs
from .policy_version_segment import PolicyVersionSegment

__all__ = ["SampleResult"]


class SampleResult(BaseModel):
    """Completions generated for a single model input"""

    policy_segments: List[PolicyVersionSegment]
    """Policy versions that produced these completions"""

    sequences: List[SampledSequence]
    """Generated completions"""

    prompt_logprobs: Optional[List[float]] = None
    """Teacher-forced log-probability of each model input token.

    Full prompt length; entry i corresponds to prompt token i. Entry 0 is always 0
    as a placeholder: the first prompt token has no conditioning context, so it has
    no log-probability. Present only when prompt_logprobs was set on the request.
    """

    topk_prompt_logprobs: Optional[List[PromptTopLogprobs]] = None
    """
    The most likely alternative tokens at each model input token, up to
    `topk_prompt_logprobs` per position. Full prompt length; entry i corresponds to
    prompt token i, and entry 0 is empty. Present only when topk_prompt_logprobs was
    set on the request.
    """
