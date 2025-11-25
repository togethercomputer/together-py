# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
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

    batch_size: Union[int, Literal["max"], None] = None

    created_at: Optional[str] = None

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

    training_method: Optional[TrainingMethod] = None

    training_type: Optional[TrainingType] = None

    trainingfile_numlines: Optional[int] = None

    trainingfile_size: Optional[int] = None

    updated_at: Optional[str] = None

    validation_file: Optional[str] = None

    wandb_project_name: Optional[str] = None

    wandb_url: Optional[str] = None

    warmup_ratio: Optional[float] = None

    weight_decay: Optional[float] = None
