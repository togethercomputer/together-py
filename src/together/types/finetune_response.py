# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .finetune_event import FinetuneEvent

__all__ = [
    "FinetuneResponse",
    "LrScheduler",
    "LrSchedulerLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs",
    "MultimodalParams",
    "Progress",
    "TrainingMethod",
    "TrainingMethodTrainingMethodSft",
    "TrainingMethodTrainingMethodDpo",
    "TrainingType",
    "TrainingTypeFullTrainingType",
    "TrainingTypeLoRaTrainingType",
]


class LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs(BaseModel):
    min_lr_ratio: Optional[float] = None
    """The ratio of the final learning rate to the peak learning rate"""


class LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs(BaseModel):
    min_lr_ratio: float
    """The ratio of the final learning rate to the peak learning rate"""

    num_cycles: float
    """Number or fraction of cycles for the cosine learning rate scheduler"""


LrSchedulerLrSchedulerArgs: TypeAlias = Union[
    LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs, LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs
]


class LrScheduler(BaseModel):
    lr_scheduler_type: Literal["linear", "cosine"]

    lr_scheduler_args: Optional[LrSchedulerLrSchedulerArgs] = None


class MultimodalParams(BaseModel):
    train_vision: Optional[bool] = None
    """Whether to train the vision encoder of the model.

    Only available for multimodal models.
    """


class Progress(BaseModel):
    """Progress information for a fine-tuning job"""

    estimate_available: bool
    """Whether time estimate is available"""

    seconds_remaining: int
    """Estimated time remaining in seconds for the fine-tuning job to next state"""


class TrainingMethodTrainingMethodSft(BaseModel):
    method: Literal["sft"]

    train_on_inputs: Union[bool, Literal["auto"]]
    """
    Whether to mask user messages in conversational data or prompts in instruction
    data.
    """


class TrainingMethodTrainingMethodDpo(BaseModel):
    method: Literal["dpo"]

    dpo_beta: Optional[float] = None

    dpo_normalize_logratios_by_length: Optional[bool] = None

    dpo_reference_free: Optional[bool] = None

    rpo_alpha: Optional[float] = None

    simpo_gamma: Optional[float] = None


TrainingMethod: TypeAlias = Union[TrainingMethodTrainingMethodSft, TrainingMethodTrainingMethodDpo]


class TrainingTypeFullTrainingType(BaseModel):
    type: Literal["Full"]


class TrainingTypeLoRaTrainingType(BaseModel):
    """LoRA training configuration for a fine-tuning job."""

    lora_alpha: int
    """Scaling factor applied to the LoRA adapter weights."""

    lora_r: int
    """Rank of the LoRA adapter matrices."""

    type: Literal["Lora"]
    """Identifies this request as a LoRA fine-tune."""

    lora_dropout: Optional[float] = None
    """Dropout probability applied to LoRA adapter inputs."""

    lora_trainable_modules: Optional[str] = None
    """Comma-separated LoRA target modules.

    Use `all-linear` for model defaults; MoE expert modules (`w_up`, `w_gate`,
    `w_down`) can be combined with attention modules on compatible models.
    Fine-tunes that target any expert module produce adapter-only output.
    """


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]


class FinetuneResponse(BaseModel):
    id: str

    status: Literal[
        "pending",
        "queued",
        "running",
        "compressing",
        "uploading",
        "cancel_requested",
        "cancelled",
        "error",
        "completed",
    ]

    user_id: str
    """ID of the user who created the fine-tune job."""

    adapter_object_id: Optional[str] = None
    """Together model registry object ID for the final adapter weights on LoRA jobs."""

    adapter_object_name: Optional[str] = None
    """
    Together model registry name for the final adapter weights on LoRA jobs,
    formatted as `<project_slug>/<model_name>-adapter`.
    """

    adapter_object_revision_id: Optional[str] = None
    """Together model registry revision ID for the final adapter weights on LoRA jobs."""

    batch_size: Union[int, Literal["max"], None] = None

    created_at: Optional[datetime] = None

    early_stopped: Optional[bool] = None
    """Whether the early-stopping criterion triggered."""

    early_stopping_best_metric: Optional[float] = None
    """Best validation loss observed, corresponding to early_stopping_best_step.

    Null if no improving evaluation was recorded (for example, a non-finite first
    evaluation).
    """

    early_stopping_best_step: Optional[int] = None
    """Step associated with the selected early-stopping artifact.

    When early_stopping_best_metric is null, no finite best metric was recorded;
    this is the halt step, not a best-checkpoint step.
    """

    epochs_completed: Optional[int] = None

    eval_steps: Optional[int] = None

    events: Optional[List[FinetuneEvent]] = None

    from_checkpoint: Optional[str] = None

    from_hf_model: Optional[str] = None

    hf_model_revision: Optional[str] = None

    job_id: Optional[str] = None

    learning_rate: Optional[float] = None

    lr_scheduler: Optional[LrScheduler] = None

    max_grad_norm: Optional[float] = None

    model: Optional[str] = None

    api_model_object_id: Optional[str] = FieldInfo(alias="model_object_id", default=None)
    """Together model registry object ID for the final model weights (e.g. `ml_...`)."""

    api_model_object_name: Optional[str] = FieldInfo(alias="model_object_name", default=None)
    """
    Together model registry name for the final model weights, formatted as
    `<project_slug>/<model_name>`.
    """

    api_model_object_revision_id: Optional[str] = FieldInfo(alias="model_object_revision_id", default=None)
    """Together model registry revision ID for the final model weights (e.g.

    `rv_...`).
    """

    x_model_output_name: Optional[str] = FieldInfo(alias="model_output_name", default=None)

    x_model_output_path: Optional[str] = FieldInfo(alias="model_output_path", default=None)

    multimodal_params: Optional[MultimodalParams] = None

    n_checkpoints: Optional[int] = None

    n_epochs: Optional[int] = None

    n_evals: Optional[int] = None

    param_count: Optional[int] = None

    progress: Optional[Progress] = None
    """Progress information for a fine-tuning job"""

    queue_depth: Optional[int] = None

    started_at: Optional[datetime] = None

    token_count: Optional[int] = None

    tokenized_dataset_path: Optional[str] = None
    """
    Storage path for the tokenized dataset archive generated for this fine-tune job.
    """

    tokenized_dataset_uploaded_at: Optional[datetime] = None
    """Timestamp when the tokenized dataset archive was uploaded."""

    total_price: Optional[int] = None

    train_on_inputs: Union[bool, Literal["auto"], None] = None

    training_file: Optional[str] = None

    training_method: Optional[TrainingMethod] = None

    training_type: Optional[TrainingType] = None
    """LoRA training configuration for a fine-tuning job."""

    trainingfile_numlines: Optional[int] = None

    trainingfile_size: Optional[int] = None

    updated_at: Optional[datetime] = None

    validation_file: Optional[str] = None

    wandb_project_name: Optional[str] = None

    wandb_url: Optional[str] = None

    warmup_ratio: Optional[float] = None

    weight_decay: Optional[float] = None
