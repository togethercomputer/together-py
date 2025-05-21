# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "FineTuneCancelResponse",
    "Event",
    "LrScheduler",
    "LrSchedulerLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs",
    "TrainingMethod",
    "TrainingMethodTrainingMethodSft",
    "TrainingMethodTrainingMethodDpo",
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


class TrainingMethodTrainingMethodSft(BaseModel):
    method: Literal["sft"]

    train_on_inputs: Union[bool, Literal["auto"]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """


class TrainingMethodTrainingMethodDpo(BaseModel):
    method: Literal["dpo"]

    dpo_beta: Optional[float] = None


TrainingMethod: TypeAlias = Union[TrainingMethodTrainingMethodSft, TrainingMethodTrainingMethodDpo]


class TrainingTypeFullTrainingType(BaseModel):
    type: Literal["Full"]


class TrainingTypeLoRaTrainingType(BaseModel):
    lora_alpha: int

    lora_r: int

    type: Literal["Lora"]

    lora_dropout: Optional[float] = None

    lora_trainable_modules: Optional[str] = None


TrainingType: TypeAlias = Union[TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType]


class FineTuneCancelResponse(BaseModel):
    id: str
    """Unique identifier for the fine-tune job"""

    created_at: datetime
    """Creation timestamp of the fine-tune job"""

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

    updated_at: datetime
    """Last update timestamp of the fine-tune job"""

    batch_size: Optional[int] = None
    """Batch size used for training"""

    events: Optional[List[Event]] = None
    """Events related to this fine-tune job"""

    from_checkpoint: Optional[str] = None
    """Checkpoint used to continue training"""

    learning_rate: Optional[float] = None
    """Learning rate used for training"""

    lr_scheduler: Optional[LrScheduler] = None
    """Learning rate scheduler configuration"""

    max_grad_norm: Optional[float] = None
    """Maximum gradient norm for clipping"""

    model: Optional[str] = None
    """Base model used for fine-tuning"""

    n_checkpoints: Optional[int] = None
    """Number of checkpoints saved during training"""

    n_epochs: Optional[int] = None
    """Number of training epochs"""

    n_evals: Optional[int] = None
    """Number of evaluations during training"""

    owner_address: Optional[str] = None
    """Owner address information"""

    suffix: Optional[str] = None
    """Suffix added to the fine-tuned model name"""

    token_count: Optional[int] = None
    """Count of tokens processed"""

    total_price: Optional[int] = None
    """Total price for the fine-tuning job"""

    training_file: Optional[str] = None
    """File-ID of the training file"""

    training_method: Optional[TrainingMethod] = None
    """Method of training used"""

    training_type: Optional[TrainingType] = None
    """Type of training used (full or LoRA)"""

    user_id: Optional[str] = None
    """Identifier for the user who created the job"""

    validation_file: Optional[str] = None
    """File-ID of the validation file"""

    wandb_name: Optional[str] = None
    """Weights & Biases run name"""

    wandb_project_name: Optional[str] = None
    """Weights & Biases project name"""

    warmup_ratio: Optional[float] = None
    """Ratio of warmup steps"""

    weight_decay: Optional[float] = None
    """Weight decay value used"""
