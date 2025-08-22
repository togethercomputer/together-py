# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .lr_scheduler import LrScheduler
from .fine_tune_event import FineTuneEvent
from .full_training_type import FullTrainingType
from .lo_ra_training_type import LoRaTrainingType
from .training_method_dpo import TrainingMethodDpo
from .training_method_sft import TrainingMethodSft

__all__ = ["FineTune", "TrainingMethod", "TrainingType"]

TrainingMethod: TypeAlias = Union[TrainingMethodSft, TrainingMethodDpo]

TrainingType: TypeAlias = Union[FullTrainingType, LoRaTrainingType]


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

    batch_size: Union[int, Literal["max"], None] = None

    created_at: Optional[str] = None

    epochs_completed: Optional[int] = None

    eval_steps: Optional[int] = None

    events: Optional[List[FineTuneEvent]] = None

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
