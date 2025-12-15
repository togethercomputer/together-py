# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "FineTuningEstimatePriceParams",
    "TrainingMethod",
    "TrainingMethodTrainingMethodSft",
    "TrainingMethodTrainingMethodDpo",
    "TrainingType",
    "TrainingTypeFullTrainingType",
    "TrainingTypeLoRaTrainingType",
]


class FineTuningEstimatePriceParams(TypedDict, total=False):
    training_file: Required[str]
    """File-ID of a training file uploaded to the Together API"""

    from_checkpoint: str
    """The checkpoint identifier to continue training from a previous fine-tuning job.

    Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
    `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
    final checkpoint will be used.
    """

    model: str
    """Name of the base model to run fine-tune job on"""

    n_epochs: int
    """
    Number of complete passes through the training dataset (higher values may
    improve results but increase cost and risk of overfitting)
    """

    n_evals: int
    """Number of evaluations to be run on a given validation set during training"""

    training_method: TrainingMethod
    """The training method to use.

    'sft' for Supervised Fine-Tuning or 'dpo' for Direct Preference Optimization.
    """

    training_type: TrainingType

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""


class TrainingMethodTrainingMethodSft(TypedDict, total=False):
    method: Required[Literal["sft"]]

    train_on_inputs: Required[Union[bool, Literal["auto"]]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """


class TrainingMethodTrainingMethodDpo(TypedDict, total=False):
    method: Required[Literal["dpo"]]

    dpo_beta: float

    dpo_normalize_logratios_by_length: bool

    dpo_reference_free: bool

    rpo_alpha: float

    simpo_gamma: float


TrainingMethod: TypeAlias = Union[TrainingMethodTrainingMethodSft, TrainingMethodTrainingMethodDpo]


class TrainingTypeFullTrainingType(TypedDict, total=False):
    type: Required[Literal["Full"]]


class TrainingTypeLoRaTrainingType(TypedDict, total=False):
    lora_alpha: Required[int]

    lora_r: Required[int]

    type: Required[Literal["Lora"]]

    lora_dropout: float

    lora_trainable_modules: str


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]
