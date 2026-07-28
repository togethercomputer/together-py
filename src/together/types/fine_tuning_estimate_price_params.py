# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
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
    `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, uses the
    final checkpoint.
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

    training_type: Optional[TrainingType]
    """The training type to use. Defaults to LoRA if not provided."""

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""


class TrainingMethodTrainingMethodSft(TypedDict, total=False):
    method: Required[Literal["sft"]]

    train_on_inputs: Required[Union[bool, Literal["auto"]]]
    """
    Whether to mask user messages in conversational data or prompts in instruction
    data.
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
    """LoRA training configuration for a fine-tuning job."""

    lora_alpha: Required[int]
    """Scaling factor applied to the LoRA adapter weights."""

    lora_r: Required[int]
    """Rank of the LoRA adapter matrices."""

    type: Required[Literal["Lora"]]
    """Identifies this request as a LoRA fine-tune."""

    lora_dropout: float
    """Dropout probability applied to LoRA adapter inputs."""

    lora_trainable_modules: str
    """Comma-separated LoRA target modules.

    Use `all-linear` for model defaults; MoE expert modules (`w_up`, `w_gate`,
    `w_down`) can be combined with attention modules on compatible models.
    Fine-tunes that target any expert module produce adapter-only output.
    """


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]
