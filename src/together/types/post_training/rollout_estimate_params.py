# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RolloutEstimateParams", "ComputeConfig"]


class RolloutEstimateParams(TypedDict, total=False):
    added_tokens_per_turn: Required[int]
    """
    Tokens added before each later turn (K), including the prior generated tokens
    followed by environment tokens. Must be at least generated_tokens_per_turn.
    """

    base_model: Required[str]
    """Base model to estimate.

    The model, GPU type, and training mode must support rollout estimates.
    """

    concurrency: Required[int]
    """Maximum concurrent episodes across all generator replicas (B).

    Must be positive.
    """

    episodes: Required[int]
    """Total number of episodes (N). Must be between 1 and 10000000."""

    generated_tokens_per_turn: Required[int]
    """Tokens generated on each turn (O). Must be positive."""

    prompt_tokens: Required[int]
    """Initial prompt tokens per episode (P). Must be positive."""

    turns: Required[int]
    """Assistant turns per episode (T). Must be between 1 and 1024."""

    compute_config: ComputeConfig
    """Compute layout to estimate, as for a model resource.

    Omitted fields use the model's default GPU type and one generator replica (D);
    num_generator_replicas must be positive.
    """

    distinct_prompts_per_replica: int
    """
    Number of distinct initial prompts among the concurrent episodes of one replica
    (Q). When episodes_per_prompt is given, defaults to ceil(concurrent episodes /
    G). Otherwise defaults to 1 when shared_prefix_tokens equals prompt_tokens, and
    to the concurrent episodes per replica when it does not. Must be 1 when
    shared_prefix_tokens equals prompt_tokens.
    """

    episodes_per_prompt: int
    """Maximum sibling episodes per initial prompt (G).

    When distinct_prompts_per_replica is given, defaults to ceil(concurrent episodes
    / Q). Otherwise defaults to the concurrent episodes per replica when
    shared_prefix_tokens equals prompt_tokens, and to 1 when it does not. When
    shared_prefix_tokens equals prompt_tokens, must be at least the concurrent
    episodes per replica.
    """

    lora_enabled: bool
    """
    Whether to estimate a resource that hosts LoRA sessions (true, default) or a
    single full-weight session (false), as in a model resource. The model and GPU
    type must support rollout estimates in this mode.
    """

    shared_prefix_tokens: int
    """Leading tokens shared by all distinct initial prompts (H).

    Defaults to 0; cannot exceed prompt_tokens.
    """


class ComputeConfig(TypedDict, total=False):
    """Compute layout to estimate, as for a model resource.

    Omitted fields use the model's default GPU type and one generator replica (D); num_generator_replicas must be positive.
    """

    gpu_type: Literal["B200-SXM"]
    """GPU type to provision. Omit to use the model's default GPU type."""

    num_generator_replicas: int
    """Number of generator replicas. 0 runs the trainer only, with no generator."""

    num_trainer_replicas: int
    """Number of trainers: 0 or 1.

    Omit to use 1. Each trainer can use multiple GPUs. With 0, at least one
    generator replica is required, optimizer_config is not allowed, and sessions
    must resume from an inference checkpoint for sampling only.
    """
