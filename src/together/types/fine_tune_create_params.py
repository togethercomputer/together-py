# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FineTuneCreateParams"]


class FineTuneCreateParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model to run fine-tune job on"""

    training_file: Required[str]
    """File-ID of a file uploaded to the Together API"""

    batch_size: int
    """Batch size for fine-tuning"""

    learning_rate: float
    """Learning rate multiplier to use for training"""

    n_checkpoints: int
    """Number of checkpoints to save during fine-tuning"""

    n_epochs: int
    """Number of epochs for fine-tuning"""

    suffix: str
    """Suffix that will be added to your fine-tuned model name"""

    wandb_api_key: str
    """API key for Weights & Biases integration"""
