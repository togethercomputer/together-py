# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = [
    "RlSupportedModel",
    "ComputeConfig",
    "ComputeConfigGeneratorConfig",
    "ComputeConfigGeneratorConfigSamplingDefaults",
    "ComputeConfigTrainerConfig",
    "ComputeConfigTrainerConfigFull",
    "ComputeConfigTrainerConfigLora",
]


class ComputeConfigGeneratorConfigSamplingDefaults(BaseModel):
    """Default sampling parameters used for sample requests."""

    logprobs: int
    """Number of logprobs to return per token"""

    max_tokens: int
    """Maximum tokens generated per completion"""

    n: int
    """Number of completions per prompt"""

    temperature: float
    """Sampling temperature"""


class ComputeConfigGeneratorConfig(BaseModel):
    """Inference config for this GPU type.

    Set when the model can be provisioned with generator replicas on this GPU type.
    """

    context_length: int
    """Maximum tokens in a single inference request (prompt + completion)"""

    sampling_defaults: ComputeConfigGeneratorConfigSamplingDefaults
    """Default sampling parameters used for sample requests."""


class ComputeConfigTrainerConfigFull(BaseModel):
    """Full-weight training config. Set when the model supports full-weight training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class ComputeConfigTrainerConfigLora(BaseModel):
    """LoRA training config. Set when the model supports LoRA training."""

    max_batch_size: int
    """Maximum global batch size accepted by a forward-backward step"""

    max_rank: int
    """Maximum LoRA rank"""

    max_seq_length: int
    """Maximum sequence length in tokens"""


class ComputeConfigTrainerConfig(BaseModel):
    """Training config for this GPU type.

    Set when the model supports at least one training mode on this GPU type.
    """

    full: Optional[ComputeConfigTrainerConfigFull] = None
    """Full-weight training config. Set when the model supports full-weight training."""

    lora: Optional[ComputeConfigTrainerConfigLora] = None
    """LoRA training config. Set when the model supports LoRA training."""


class ComputeConfig(BaseModel):
    """A validated hardware configuration available for an RL base model."""

    gpu_type: Literal["H100-80GB", "B200-SXM"]
    """GPU type this configuration provisions."""

    generator_config: Optional[ComputeConfigGeneratorConfig] = None
    """Inference config for this GPU type.

    Set when the model can be provisioned with generator replicas on this GPU type.
    """

    trainer_config: Optional[ComputeConfigTrainerConfig] = None
    """Training config for this GPU type.

    Set when the model supports at least one training mode on this GPU type.
    """


class RlSupportedModel(BaseModel):
    """A base model supported by the RL service.

    Per-mode configs are present only when the model supports that mode.
    """

    base_model: str
    """Base model identifier to pass as base_model when creating a model resource"""

    default_gpu_type: Literal["H100-80GB", "B200-SXM"]
    """GPU type used when model-resource creation omits gpu_type."""

    compute_configs: Optional[List[ComputeConfig]] = None
    """Validated GPU configurations available for this base model."""
