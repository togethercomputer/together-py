# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .finetune_event import FinetuneEvent

__all__ = [
    "FineTuningCancelResponse",
    "LrScheduler",
    "LrSchedulerLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsLinearLrSchedulerArgs",
    "LrSchedulerLrSchedulerArgsCosineLrSchedulerArgs",
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
    """Learning rate scheduler configuration"""

    lr_scheduler_type: Literal["linear", "cosine"]

    lr_scheduler_args: Optional[LrSchedulerLrSchedulerArgs] = None


class Progress(BaseModel):
    """Progress information for the fine-tuning job"""

    estimate_available: bool
    """Whether time estimate is available"""

    seconds_remaining: int
    """Estimated time remaining in seconds for the fine-tuning job to next state"""


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

    dpo_normalize_logratios_by_length: Optional[bool] = None

    dpo_reference_free: Optional[bool] = None

    rpo_alpha: Optional[float] = None

    simpo_gamma: Optional[float] = None


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


class FineTuningCancelResponse(BaseModel):
    """
    A truncated version of the fine-tune response, used for POST /fine-tunes, GET /fine-tunes and POST /fine-tunes/{id}/cancel endpoints
    """

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

    events: Optional[List[FinetuneEvent]] = None
    """Events related to this fine-tune job"""

    from_checkpoint: Optional[str] = None
    """Checkpoint used to continue training"""

    from_hf_model: Optional[str] = None
    """Hugging Face Hub repo to start training from"""

    hf_model_revision: Optional[str] = None
    """The revision of the Hugging Face Hub model to continue training from"""

    learning_rate: Optional[float] = None
    """Learning rate used for training"""

    lr_scheduler: Optional[LrScheduler] = None
    """Learning rate scheduler configuration"""

    max_grad_norm: Optional[float] = None
    """Maximum gradient norm for clipping"""

    model: Optional[str] = None
    """Base model used for fine-tuning"""

    x_model_output_name: Optional[str] = FieldInfo(alias="model_output_name", default=None)

    n_checkpoints: Optional[int] = None
    """Number of checkpoints saved during training"""

    n_epochs: Optional[int] = None
    """Number of training epochs"""

    n_evals: Optional[int] = None
    """Number of evaluations during training"""

    owner_address: Optional[str] = None
    """Owner address information"""

    progress: Optional[Progress] = None
    """Progress information for the fine-tuning job"""

    started_at: Optional[datetime] = None
    """Start timestamp of the current stage of the fine-tune job"""

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
