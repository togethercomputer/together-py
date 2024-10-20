# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["FineTuneCreateParams", "TrainingType", "TrainingTypeFullTrainingType", "TrainingTypeLoRaTrainingType"]


class FineTuneCreateParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model to run fine-tune job on"""

    training_file: Required[str]
    """File-ID of a training file uploaded to the Together API"""

    batch_size: int
    """Batch size for fine-tuning"""

    learning_rate: float
    """Learning rate multiplier to use for training"""

    n_checkpoints: int
    """Number of checkpoints to save during fine-tuning"""

    n_epochs: int
    """Number of epochs for fine-tuning"""

    n_evals: int
    """Number of evaluations to be run on a given validation set during training"""

    suffix: str
    """Suffix that will be added to your fine-tuned model name"""

    training_type: TrainingType

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""

    wandb_api_key: str
    """API key for Weights & Biases integration"""

    warmup_ratio: float
    """
    The percent of steps at the start of training to linearly increase the
    learning-rate.
    """


class TrainingTypeFullTrainingType(TypedDict, total=False):
    type: Required[Literal["Full"]]


class TrainingTypeLoRaTrainingType(TypedDict, total=False):
    lora_alpha: Required[int]

    lora_r: Required[int]

    type: Required[Literal["Lora"]]

    lora_dropout: float

    lora_trainable_modules: str


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]
