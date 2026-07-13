# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = [
    "SupportedModels",
    "Data",
    "DataGeneratorConfig",
    "DataGeneratorConfigSamplingDefaults",
    "DataTrainerConfig",
    "DataTrainerConfigFull",
    "DataTrainerConfigLora",
]


class DataGeneratorConfigSamplingDefaults(BaseModel):
    """Default sampling parameters used for sample requests."""

    logprobs: int
    """Number of logprobs to return per token"""

    max_tokens: int
    """Maximum tokens generated per completion"""

    n: int
    """Number of completions per prompt"""

    temperature: float
    """Sampling temperature"""


class DataGeneratorConfig(BaseModel):
    """Inference config.

    Set when the model can be provisioned with generator replicas.
    """

    context_length: int
    """Maximum tokens in a single inference request (prompt + completion)"""

    sampling_defaults: DataGeneratorConfigSamplingDefaults
    """Default sampling parameters used for sample requests."""


class DataTrainerConfigFull(BaseModel):
    """Full-weight training config. Set when the model supports full-weight training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class DataTrainerConfigLora(BaseModel):
    """LoRA training config. Set when the model supports LoRA training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_rank: int
    """Maximum LoRA rank"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class DataTrainerConfig(BaseModel):
    """Training config. Set when the model supports at least one training mode."""

    full: Optional[DataTrainerConfigFull] = None
    """Full-weight training config. Set when the model supports full-weight training."""

    lora: Optional[DataTrainerConfigLora] = None
    """LoRA training config. Set when the model supports LoRA training."""


class Data(BaseModel):
    """A base model supported by the RL service.

    Per-mode configs are present only when the model supports that mode.
    """

    base_model: str
    """Base model identifier to pass as base_model when creating a model resource"""

    generator_config: Optional[DataGeneratorConfig] = None
    """Inference config.

    Set when the model can be provisioned with generator replicas.
    """

    trainer_config: Optional[DataTrainerConfig] = None
    """Training config. Set when the model supports at least one training mode."""


class SupportedModels(BaseModel):
    """List of base models supported by the RL service"""

    data: List[Data]
    """Supported base models for RL"""
