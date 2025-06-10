# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .lr_scheduler import LrScheduler
from .fine_tune_event import FineTuneEvent
from .full_training_type import FullTrainingType
from .lo_ra_training_type import LoRaTrainingType
from .training_method_dpo import TrainingMethodDpo
from .training_method_sft import TrainingMethodSft

__all__ = ["FineTuneListResponse", "Data", "DataTrainingMethod", "DataTrainingType"]

DataTrainingMethod: TypeAlias = Union[TrainingMethodSft, TrainingMethodDpo]

DataTrainingType: TypeAlias = Union[FullTrainingType, LoRaTrainingType]


class Data(BaseModel):
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

    events: Optional[List[FineTuneEvent]] = None
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

    x_model_output_name: Optional[str] = FieldInfo(alias="model_output_name", default=None)

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

    training_method: Optional[DataTrainingMethod] = None
    """Method of training used"""

    training_type: Optional[DataTrainingType] = None
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


class FineTuneListResponse(BaseModel):
    data: List[Data]
