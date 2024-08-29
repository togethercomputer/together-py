# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FineTuneCreateParams"]


class FineTuneCreateParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model to run fine-tune job on"""

    training_file: Required[str]
    """File-ID of a training file uploaded to the Together API"""

    batch_size: int
    """Batch size for fine-tuning"""

    learning_rate: float
    """Learning rate multiplier to use for training"""

    lora: bool
    """Whether to enable LoRA training.

    If not provided, full fine-tuning will be applied.
    """

    lora_alpha: int
    """The alpha value for LoRA adapter training."""

    lora_dropout: float
    """The dropout probability for Lora layers."""

    lora_r: int
    """Rank for LoRA adapter weights"""

    lora_trainable_modules: str
    """A list of LoRA trainable modules, separated by a comma"""

    n_checkpoints: int
    """Number of checkpoints to save during fine-tuning"""

    n_epochs: int
    """Number of epochs for fine-tuning"""

    n_evals: int
    """Number of evaluations to be run on a given validation set during training"""

    suffix: str
    """Suffix that will be added to your fine-tuned model name"""

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""

    wandb_api_key: str
    """API key for Weights & Biases integration"""
