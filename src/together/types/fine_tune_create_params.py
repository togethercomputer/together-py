# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "FineTuneCreateParams",
    "LrScheduler",
    "LrSchedulerLrSchedulerArgs",
    "TrainingType",
    "TrainingTypeFullTrainingType",
    "TrainingTypeLoRaTrainingType",
]


class FineTuneCreateParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model to run fine-tune job on"""

    training_file: Required[str]
    """File-ID of a training file uploaded to the Together API"""

    batch_size: int
    """Batch size for fine-tuning"""

    learning_rate: float
    """Learning rate multiplier to use for training"""

    lr_scheduler: LrScheduler

    max_grad_norm: float
    """Max gradient norm to be used for gradient clipping. Set to 0 to disable."""

    n_checkpoints: int
    """Number of checkpoints to save during fine-tuning"""

    n_epochs: int
    """Number of epochs for fine-tuning"""

    n_evals: int
    """Number of evaluations to be run on a given validation set during training"""

    suffix: str
    """Suffix that will be added to your fine-tuned model name"""

    train_on_inputs: Union[bool, Literal["auto"]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """

    training_type: TrainingType

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""

    wandb_api_key: str
    """API key for Weights & Biases integration"""

    wandb_base_url: str
    """The base URL of a dedicated Weights & Biases instance."""

    wandb_name: str
    """The Weights & Biases name for your run."""

    wandb_project_name: str
    """The Weights & Biases project for your run.

    If not specified, will use `together` as the project name.
    """

    warmup_ratio: float
    """
    The percent of steps at the start of training to linearly increase the learning
    rate.
    """

    weight_decay: float
    """Weight decay"""


class LrSchedulerLrSchedulerArgs(TypedDict, total=False):
    min_lr_ratio: float
    """The ratio of the final learning rate to the peak learning rate"""


class LrScheduler(TypedDict, total=False):
    lr_scheduler_type: Required[str]

    lr_scheduler_args: LrSchedulerLrSchedulerArgs


class TrainingTypeFullTrainingType(TypedDict, total=False):
    type: Required[Literal["Full"]]


class TrainingTypeLoRaTrainingType(TypedDict, total=False):
    lora_alpha: Required[int]

    lora_r: Required[int]

    type: Required[Literal["Lora"]]

    lora_dropout: float

    lora_trainable_modules: str


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]
