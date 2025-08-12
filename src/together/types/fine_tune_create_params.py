# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .lr_scheduler_param import LrSchedulerParam
from .full_training_type_param import FullTrainingTypeParam
from .lo_ra_training_type_param import LoRaTrainingTypeParam
from .training_method_dpo_param import TrainingMethodDpoParam
from .training_method_sft_param import TrainingMethodSftParam

__all__ = ["FineTuneCreateParams", "TrainingMethod", "TrainingType"]


class FineTuneCreateParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model to run fine-tune job on"""

    training_file: Required[str]
    """File-ID of a training file uploaded to the Together API"""

    batch_size: Union[int, Literal["max"]]
    """
    Number of training examples processed together (larger batches use more memory
    but may train faster). Defaults to "max". We use training optimizations like
    packing, so the effective batch size may be different than the value you set.
    """

    from_checkpoint: str
    """The checkpoint identifier to continue training from a previous fine-tuning job.

    Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
    `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
    final checkpoint will be used.
    """

    from_hf_model: str
    """The Hugging Face Hub repo to start training from.

    Should be as close as possible to the base model (specified by the `model` argument)
    in terms of architecture and size.
    """

    hf_model_revision: str
    """
    The revision of the Hugging Face Hub model to continue training from.

    Example: hf_model_revision=None (defaults to the latest revision in `main`) or
    hf_model_revision="607a30d783dfa663caf39e06633721c8d4cfcd7e" (specific commit).
    """

    hf_api_token: str
    """The API token for the Hugging Face Hub."""

    hf_output_repo_name: str
    """The name of the Hugging Face repository to upload the fine-tuned model to."""

    learning_rate: float
    """
    Controls how quickly the model adapts to new information (too high may cause
    instability, too low may slow convergence)
    """

    lr_scheduler: LrSchedulerParam
    """The learning rate scheduler to use.

    It specifies how the learning rate is adjusted during training.
    """

    max_grad_norm: float
    """Max gradient norm to be used for gradient clipping. Set to 0 to disable."""

    n_checkpoints: int
    """Number of intermediate model versions saved during training for evaluation"""

    n_epochs: int
    """
    Number of complete passes through the training dataset (higher values may
    improve results but increase cost and risk of overfitting)
    """

    n_evals: int
    """Number of evaluations to be run on a given validation set during training"""

    suffix: str
    """Suffix that will be added to your fine-tuned model name"""

    train_on_inputs: Union[bool, Literal["auto"]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """

    training_method: TrainingMethod
    """The training method to use.

    'sft' for Supervised Fine-Tuning or 'dpo' for Direct Preference Optimization.
    """

    training_type: TrainingType

    validation_file: str
    """File-ID of a validation file uploaded to the Together API"""

    wandb_api_key: str
    """Integration key for tracking experiments and model metrics on W&B platform"""

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
    """Weight decay. Regularization parameter for the optimizer."""


TrainingMethod: TypeAlias = Union[TrainingMethodSftParam, TrainingMethodDpoParam]

TrainingType: TypeAlias = Union[FullTrainingTypeParam, LoRaTrainingTypeParam]
