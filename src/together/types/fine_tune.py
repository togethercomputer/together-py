# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "FineTune",
    "Event",
    "LrScheduler",
    "LrSchedulerLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs",
    "TrainingType",
    "TrainingTypeFullTrainingType",
    "TrainingTypeLoRaTrainingType",
]


class Event(BaseModel):
    checkpoint_path: str

    created_at: str

    hash: str

    message: str

    x_model_path: str = FieldInfo(alias="model_path")

    object: Literal["fine-tune-event"]

    param_count: int

    step: int

    token_count: int

    total_steps: int

    training_offset: int

    type: Literal[
        "job_pending",
        "job_start",
        "job_stopped",
        "model_downloading",
        "model_download_complete",
        "training_data_downloading",
        "training_data_download_complete",
        "validation_data_downloading",
        "validation_data_download_complete",
        "wandb_init",
        "training_start",
        "checkpoint_save",
        "billing_limit",
        "epoch_complete",
        "training_complete",
        "model_compressing",
        "model_compression_complete",
        "model_uploading",
        "model_upload_complete",
        "job_complete",
        "job_error",
        "cancel_requested",
        "job_restarted",
        "refund",
        "warning",
    ]

    wandb_url: str

    level: Optional[Literal["info", "warning", "error", "legacy_info", "legacy_iwarning", "legacy_ierror"]] = None


class LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs(BaseModel):
    min_lr_ratio: Optional[float] = None
    """The ratio of the final learning rate to the peak learning rate"""


class LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs(BaseModel):
    min_lr_ratio: Optional[float] = None
    """The ratio of the final learning rate to the peak learning rate"""

    num_cycles: Optional[float] = None
    """Number or fraction of cycles for the cosine learning rate scheduler"""


LrSchedulerLrSchedulerArgs: TypeAlias = Union[
    LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs, LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs
]


class LrScheduler(BaseModel):
    lr_scheduler_type: Literal["linear", "cosine"]

    lr_scheduler_args: Optional[LrSchedulerLrSchedulerArgs] = None


class TrainingTypeFullTrainingType(BaseModel):
    type: Literal["Full"]


class TrainingTypeLoRaTrainingType(BaseModel):
    lora_alpha: int

    lora_r: int

    type: Literal["Lora"]

    lora_dropout: Optional[float] = None

    lora_trainable_modules: Optional[str] = None


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]


class FineTune(BaseModel):
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

    batch_size: Optional[int] = None

    created_at: Optional[str] = None

    dpo_beta: Optional[float] = None

    epochs_completed: Optional[int] = None

    eval_steps: Optional[int] = None

    events: Optional[List[Event]] = None

    from_checkpoint: Optional[str] = None

    job_id: Optional[str] = None

    learning_rate: Optional[float] = None

    lr_scheduler: Optional[LrScheduler] = None

    max_grad_norm: Optional[float] = None

    model: Optional[str] = None

    x_model_output_name: Optional[str] = FieldInfo(alias="model_output_name", default=None)

    x_model_output_path: Optional[str] = FieldInfo(alias="model_output_path", default=None)

    n_checkpoints: Optional[int] = None

    n_epochs: Optional[int] = None

    n_evals: Optional[int] = None

    param_count: Optional[int] = None

    queue_depth: Optional[int] = None

    token_count: Optional[int] = None

    total_price: Optional[int] = None

    train_on_inputs: Union[bool, Literal["auto"], None] = None

    training_file: Optional[str] = None

    training_method: Optional[Literal["sft", "dpo"]] = None

    training_type: Optional[TrainingType] = None

    trainingfile_numlines: Optional[int] = None

    trainingfile_size: Optional[int] = None

    updated_at: Optional[str] = None

    validation_file: Optional[str] = None

    wandb_project_name: Optional[str] = None

    wandb_url: Optional[str] = None

    warmup_ratio: Optional[float] = None

    weight_decay: Optional[float] = None
