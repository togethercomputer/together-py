# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from ..._models import BaseModel

__all__ = ["EstimateRolloutResponse"]


class EstimateRolloutResponse(BaseModel):
    """Estimated rollout elapsed time, tokens, throughput, GPU-hours, and price"""

    allocated_gpu_hours: float
    """Generator GPUs across all replicas times wall time, in GPU-hours."""

    billed_gpu_hours: float
    """
    GPUs of the whole model resource, trainer and generator, times wall time, in
    GPU-hours. A model resource is billed for all of its GPUs while the rollouts
    run. An approximation measured on single-wave rollouts (concurrency equal to
    episodes) of up to four turns on one generator replica: actual usage can be up
    to about 45% higher when episodes share a prompt, and about 20% higher or lower
    otherwise. Longer multi-turn rollouts with distinct prompts can take longer than
    estimated.
    """

    currency: str
    """Currency of estimated_price."""

    effective_decode_tokens_per_second: float
    """generated_tokens divided by wall_seconds."""

    effective_distinct_prompts_per_replica: int
    """
    Effective distinct_prompts_per_replica (Q) for the largest concurrent batch of
    one replica.
    """

    effective_episodes_per_prompt: int
    """
    Effective episodes_per_prompt (G) for the largest concurrent batch of one
    replica.
    """

    effective_prefill_tokens_per_second: float
    """
    submitted_prompt_tokens divided by wall_seconds, counting prompt tokens served
    from the prompt cache.
    """

    effective_shared_prefix_tokens: int
    """Effective shared_prefix_tokens (H)."""

    estimated_price: float
    """
    Estimated on-demand price of the rollouts: billed_gpu_hours times the GPU type's
    list price per GPU-hour, the rate the model resource cost estimate uses. An
    approximation that inherits the uncertainty of billed_gpu_hours; it is not a
    quote.
    """

    generated_tokens: Union[str, int]
    """Generated output tokens across all turns.

    JSON encodes this count as a decimal string.
    """

    lora_enabled: bool
    """
    Whether the estimate is for a LoRA resource (true) or a full-weight resource
    (false).
    """

    submitted_prompt_tokens: Union[str, int]
    """Prompt tokens submitted across all turns.

    JSON encodes this count as a decimal string.
    """

    wall_seconds: float
    """Estimated time until all rollout episodes finish, in seconds."""
