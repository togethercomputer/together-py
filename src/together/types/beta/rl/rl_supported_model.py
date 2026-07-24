# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = [
    "RlSupportedModel",
    "GeneratorConfig",
    "GeneratorConfigSamplingDefaults",
    "TrainerConfig",
    "TrainerConfigFull",
    "TrainerConfigLora",
]


class GeneratorConfigSamplingDefaults(BaseModel):
    """Default sampling parameters used for sample requests."""

    logprobs: int
    """Number of logprobs to return per token"""

    max_tokens: int
    """Maximum tokens generated per completion"""

    n: int
    """Number of completions per prompt"""

    temperature: float
    """Sampling temperature"""


class GeneratorConfig(BaseModel):
    """Inference config.

    Set when the model can be provisioned with generator replicas.
    """

    context_length: int
    """Maximum tokens in a single inference request (prompt + completion)"""

    sampling_defaults: GeneratorConfigSamplingDefaults
    """Default sampling parameters used for sample requests."""


class TrainerConfigFull(BaseModel):
    """Full-weight training config. Set when the model supports full-weight training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class TrainerConfigLora(BaseModel):
    """LoRA training config. Set when the model supports LoRA training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_rank: int
    """Maximum LoRA rank"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class TrainerConfig(BaseModel):
    """Training config. Set when the model supports at least one training mode."""

    full: Optional[TrainerConfigFull] = None
    """Full-weight training config. Set when the model supports full-weight training."""

    lora: Optional[TrainerConfigLora] = None
    """LoRA training config. Set when the model supports LoRA training."""


class RlSupportedModel(BaseModel):
    """A base model supported by the RL service.

    Per-mode configs are present only when the model supports that mode.
    """

    base_model: str
    """Base model identifier to pass as base_model when creating a model resource"""

    generator_config: Optional[GeneratorConfig] = None
    """Inference config.

    Set when the model can be provisioned with generator replicas.
    """

    trainer_config: Optional[TrainerConfig] = None
    """Training config. Set when the model supports at least one training mode."""
