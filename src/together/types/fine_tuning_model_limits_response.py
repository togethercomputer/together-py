# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FineTuningModelLimitsResponse", "LoraTraining", "FullTraining"]


class LoraTraining(BaseModel):
    """Limits for LoRA training."""

    max_batch_size: int
    """Maximum batch size for SFT LoRA training."""

    max_batch_size_dpo: int
    """Maximum batch size for DPO LoRA training."""

    max_rank: int
    """Maximum LoRA rank."""

    min_batch_size: int
    """Minimum batch size for LoRA training."""

    target_modules: List[str]
    """Available target modules for LoRA."""


class FullTraining(BaseModel):
    """Limits for full training."""

    max_batch_size: int
    """Maximum batch size for SFT full training."""

    max_batch_size_dpo: int
    """Maximum batch size for DPO full training."""

    min_batch_size: int
    """Minimum batch size for full training."""


class FineTuningModelLimitsResponse(BaseModel):
    """Model limits for fine-tuning."""

    default_gradient_accumulation_steps: int
    """
    Default gradient accumulation steps used when a fine-tune request omits the
    value or sets it to 0.
    """

    lora_training: LoraTraining
    """Limits for LoRA training."""

    max_learning_rate: float
    """Maximum learning rate."""

    max_num_checkpoints: int
    """Maximum number of checkpoints that can be saved during a fine-tuning job."""

    max_num_epochs: int
    """Maximum number of training epochs."""

    max_num_evals: int
    """Maximum number of evaluations."""

    max_seq_length_dpo: int
    """Maximum sequence length supported for DPO training."""

    max_seq_length_sft: int
    """Maximum sequence length supported for SFT training."""

    merge_output_lora: bool
    """
    Whether a merged checkpoint (the base model with the trained LoRA adapter fused
    in) is produced for LoRA fine-tunes of this model, in addition to the standalone
    adapter.
    """

    min_learning_rate: float
    """Minimum learning rate."""

    min_max_seq_length: int
    """Minimum value allowed for the max_seq_length hyperparameter."""

    api_model_name: str = FieldInfo(alias="model_name")
    """The name of the model."""

    supports_full_training: bool
    """Whether the model supports full (non-LoRA) fine-tuning.

    When false, only LoRA fine-tuning is available and the full_training limits are
    reported as zero.
    """

    supports_reasoning: bool
    """Whether the model supports reasoning."""

    supports_tools: bool
    """Whether the model supports tool/function calling."""

    supports_vision: bool
    """Whether the model supports vision/multimodal inputs."""

    full_training: Optional[FullTraining] = None
    """Limits for full training."""
