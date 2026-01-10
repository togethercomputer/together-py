from enum import Enum
from typing import Any, List, Union, Literal, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from pydantic import Field, StrictBool

from ..._models import BaseModel


class FinetuneJobStatus(str, Enum):
    """
    Possible fine-tune job status
    """

    STATUS_PENDING = "pending"
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_COMPRESSING = "compressing"
    STATUS_UPLOADING = "uploading"
    STATUS_CANCEL_REQUESTED = "cancel_requested"
    STATUS_CANCELLED = "cancelled"
    STATUS_ERROR = "error"
    STATUS_USER_ERROR = "user_error"
    STATUS_COMPLETED = "completed"


COMPLETED_STATUSES = [
    FinetuneJobStatus.STATUS_ERROR,
    FinetuneJobStatus.STATUS_USER_ERROR,
    FinetuneJobStatus.STATUS_COMPLETED,
    FinetuneJobStatus.STATUS_CANCELLED,
]


class FinetuneEventType(str, Enum):
    """
    Fine-tune job event types
    """

    JOB_PENDING = "JOB_PENDING"
    JOB_START = "JOB_START"
    JOB_STOPPED = "JOB_STOPPED"
    MODEL_DOWNLOADING = "MODEL_DOWNLOADING"
    MODEL_DOWNLOAD_COMPLETE = "MODEL_DOWNLOAD_COMPLETE"
    TRAINING_DATA_DOWNLOADING = "TRAINING_DATA_DOWNLOADING"
    TRAINING_DATA_DOWNLOAD_COMPLETE = "TRAINING_DATA_DOWNLOAD_COMPLETE"
    VALIDATION_DATA_DOWNLOADING = "VALIDATION_DATA_DOWNLOADING"
    VALIDATION_DATA_DOWNLOAD_COMPLETE = "VALIDATION_DATA_DOWNLOAD_COMPLETE"
    WANDB_INIT = "WANDB_INIT"
    TRAINING_START = "TRAINING_START"
    CHECKPOINT_SAVE = "CHECKPOINT_SAVE"
    BILLING_LIMIT = "BILLING_LIMIT"
    EPOCH_COMPLETE = "EPOCH_COMPLETE"
    EVAL_COMPLETE = "EVAL_COMPLETE"
    TRAINING_COMPLETE = "TRAINING_COMPLETE"
    MODEL_COMPRESSING = "COMPRESSING_MODEL"
    MODEL_COMPRESSION_COMPLETE = "MODEL_COMPRESSION_COMPLETE"
    MODEL_UPLOADING = "MODEL_UPLOADING"
    MODEL_UPLOAD_COMPLETE = "MODEL_UPLOAD_COMPLETE"
    MODEL_UPLOADING_TO_HF = "MODEL_UPLOADING_TO_HF"
    MODEL_UPLOAD_TO_HF_COMPLETE = "MODEL_UPLOAD_TO_HF_COMPLETE"
    JOB_COMPLETE = "JOB_COMPLETE"
    JOB_ERROR = "JOB_ERROR"
    JOB_USER_ERROR = "JOB_USER_ERROR"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    JOB_RESTARTED = "JOB_RESTARTED"
    REFUND = "REFUND"
    WARNING = "WARNING"


class FinetuneEventLevels(str, Enum):
    """
    Fine-tune job event status levels
    """

    NULL = ""
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"


class FinetuneEvent(BaseModel):
    """
    Fine-tune event type
    """

    # object type
    object: Literal["fine-tune-event"]
    # created at datetime stamp
    created_at: Union[str, None] = None
    # event log level
    level: Union[FinetuneEventLevels, str, None] = None
    # event message string
    message: Union[str, None] = None
    # event type
    type: Union[FinetuneEventType, None] = None
    # optional: model parameter count
    param_count: Union[int, None] = None
    # optional: dataset token count
    token_count: Union[int, None] = None
    # optional: weights & biases url
    wandb_url: Union[str, None] = None
    # event hash
    hash: Union[str, None] = None


class FullTrainingType(BaseModel):
    """
    Training type for full fine-tuning
    """

    type: Union[Literal["Full"], Literal[""]] = "Full"


class LoRATrainingType(BaseModel):
    """
    Training type for LoRA adapters training
    """

    lora_r: int
    lora_alpha: int
    lora_dropout: float = 0.0
    lora_trainable_modules: str = "all-linear"
    type: Literal["Lora"] = "Lora"


class UnknownTrainingType(BaseModel):
    """
    Catch-all for unknown training types (forward compatibility).
    Accepts any training type not explicitly defined.
    """

    type: str


TrainingType: TypeAlias = Union[
    FullTrainingType,
    LoRATrainingType,
    UnknownTrainingType,
]


class FinetuneFullTrainingLimits(BaseModel):
    max_batch_size: int
    max_batch_size_dpo: int = -1
    min_batch_size: int

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.max_batch_size_dpo == -1:
            half_max = self.max_batch_size // 2
            rounded_half_max = (half_max // 8) * 8
            self.max_batch_size_dpo = max(self.min_batch_size, rounded_half_max)


class FinetuneLoraTrainingLimits(FinetuneFullTrainingLimits):
    max_rank: int
    target_modules: List[str]


class TrainingMethodSFT(BaseModel):
    """
    Training method type for SFT training
    """

    method: Literal["sft"] = "sft"
    train_on_inputs: Union[StrictBool, Literal["auto"]] = "auto"


class TrainingMethodDPO(BaseModel):
    """
    Training method type for DPO training
    """

    method: Literal["dpo"] = "dpo"
    dpo_beta: Union[float, None] = None
    dpo_normalize_logratios_by_length: bool = False
    dpo_reference_free: bool = False
    rpo_alpha: Union[float, None] = None
    simpo_gamma: Union[float, None] = None


class TrainingMethodUnknown(BaseModel):
    """
    Catch-all for unknown training methods (forward compatibility).
    Accepts any training method not explicitly defined.
    """

    method: str


TrainingMethod: TypeAlias = Union[
    TrainingMethodSFT,
    TrainingMethodDPO,
    TrainingMethodUnknown,
]


class FinetuneTrainingLimits(BaseModel):
    max_num_epochs: int
    max_learning_rate: float
    min_learning_rate: float
    full_training: Optional[FinetuneFullTrainingLimits] = None
    lora_training: Optional[FinetuneLoraTrainingLimits] = None
    supports_vision: bool = False


class LinearLRSchedulerArgs(BaseModel):
    """
    Linear learning rate scheduler arguments
    """

    min_lr_ratio: Union[float, None] = 0.0


class CosineLRSchedulerArgs(BaseModel):
    """
    Cosine learning rate scheduler arguments
    """

    min_lr_ratio: Union[float, None] = 0.0
    num_cycles: Union[float, None] = 0.5


class LinearLRScheduler(BaseModel):
    """
    Linear learning rate scheduler
    """

    lr_scheduler_type: Literal["linear"] = "linear"
    lr_scheduler_args: Union[LinearLRSchedulerArgs, None] = None


class CosineLRScheduler(BaseModel):
    """
    Cosine learning rate scheduler
    """

    lr_scheduler_type: Literal["cosine"] = "cosine"
    lr_scheduler_args: Union[CosineLRSchedulerArgs, None] = None


class EmptyLRScheduler(BaseModel):
    """
    Empty learning rate scheduler

    Placeholder for old fine-tuning jobs with no lr_scheduler_type specified
    """

    lr_scheduler_type: Literal[""]
    lr_scheduler_args: None = None


class UnknownLRScheduler(BaseModel):
    """
    Unknown learning rate scheduler

    Catch-all for unknown LR scheduler types (forward compatibility)
    """

    lr_scheduler_type: str
    lr_scheduler_args: Optional[Any] = None


FinetuneLRScheduler: TypeAlias = Union[
    LinearLRScheduler,
    CosineLRScheduler,
    EmptyLRScheduler,
    UnknownLRScheduler,
]


class FinetuneMultimodalParams(BaseModel):
    """
    Multimodal parameters
    """

    train_vision: bool = False


class FinetuneProgress(BaseModel):
    """
    Fine-tune job progress
    """

    estimate_available: bool = False
    seconds_remaining: float = 0


class FinetuneResponse(BaseModel):
    """
    Fine-tune API response type
    """

    id: str
    """Unique identifier for the fine-tune job"""

    created_at: datetime
    """Creation timestamp of the fine-tune job"""

    status: Optional[Union[FinetuneJobStatus, str]] = None
    """Status of the fine-tune job (accepts known enum values or string for forward compatibility)"""

    updated_at: datetime
    """Last update timestamp of the fine-tune job"""

    started_at: Optional[datetime] = None
    """Start timestamp of a current stage of the fine-tune job"""

    batch_size: Optional[int] = None
    """Batch size used for training"""

    events: Optional[List[Union[FinetuneEvent, str]]] = None
    """Events related to this fine-tune job (accepts known enum values or string for forward compatibility)"""

    from_checkpoint: Optional[str] = None
    """Checkpoint used to continue training"""

    multimodal_params: Optional[FinetuneMultimodalParams] = None
    """Multimodal parameters"""

    from_hf_model: Optional[str] = None
    """Hugging Face Hub repo to start training from"""

    hf_model_revision: Optional[str] = None
    """The revision of the Hugging Face Hub model to continue training from"""

    learning_rate: Optional[float] = None
    """Learning rate used for training"""

    lr_scheduler: Optional[FinetuneLRScheduler] = None
    """Learning rate scheduler configuration"""

    max_grad_norm: Optional[float] = None
    """Maximum gradient norm for clipping"""

    model: Optional[str] = None
    """Base model used for fine-tuning"""

    output_name: Optional[str] = Field(alias="model_output_name")
    """Output model name"""

    adapter_output_name: Optional[str]
    """Adapter output name"""

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

    wandb_base_url: Union[str, None] = None
    """Weights & Biases base URL"""

    wandb_url: Union[str, None] = None
    """Weights & Biases job URL"""

    warmup_ratio: Optional[float] = None
    """Ratio of warmup steps"""

    weight_decay: Optional[float] = None
    """Weight decay value used"""

    eval_steps: Union[int, None] = None
    """number of steps between evals"""

    job_id: Optional[str] = None
    """Job ID"""

    param_count: Optional[int] = None
    """Model parameter count"""

    total_steps: Optional[int] = None
    """Total number of training steps"""

    steps_completed: Union[int, None] = None
    """Number of steps completed (incrementing counter)"""

    epochs_completed: Union[int, None] = None
    """Number of epochs completed (incrementing counter)"""

    evals_completed: Union[int, None] = None
    """Number of evaluation loops completed (incrementing counter)"""

    queue_depth: Union[int, None] = None
    """Place in job queue (decrementing counter)"""

    # # training file metadata
    training_file_num_lines: Optional[int] = Field(None, alias="TrainingFileNumLines")
    training_file_size: Optional[int] = Field(None, alias="TrainingFileSize")
    train_on_inputs: Union[StrictBool, Literal["auto"], None] = "auto"

    progress: Union[FinetuneProgress, None] = None

    @classmethod
    def validate_training_type(cls, v: TrainingType) -> TrainingType:
        if v.type == "Full" or v.type == "":
            return FullTrainingType(**v.model_dump())
        elif v.type == "Lora":
            return LoRATrainingType(**v.model_dump())
        else:
            raise ValueError("Unknown training type")


class FinetuneRequest(BaseModel):
    """
    Fine-tune request type
    """

    # training file ID
    training_file: str
    # validation file id
    validation_file: Union[str, None] = None
    # base model string
    model: Union[str, None] = None
    # number of epochs to train for
    n_epochs: int
    # training learning rate
    learning_rate: float
    # learning rate scheduler type and args
    lr_scheduler: Union[FinetuneLRScheduler, None] = None
    # learning rate warmup ratio
    warmup_ratio: float
    # max gradient norm
    max_grad_norm: float
    # weight decay
    weight_decay: float
    # number of checkpoints to save
    n_checkpoints: Union[int, None] = None
    # number of evaluation loops to run
    n_evals: Union[int, None] = None
    # training batch size
    batch_size: Union[int, Literal["max"], None] = None
    # up to 40 character suffix for output model name
    suffix: Union[str, None] = None
    # weights & biases api key
    wandb_key: Union[str, None] = None
    # weights & biases base url
    wandb_base_url: Union[str, None] = None
    # wandb project name
    wandb_project_name: Union[str, None] = None
    # wandb run name
    wandb_name: Union[str, None] = None
    # training type
    training_type: Union[TrainingType, None] = None
    # training method
    training_method: TrainingMethod = Field(default_factory=TrainingMethodSFT)
    # from step
    from_checkpoint: Union[str, None] = None
    # multimodal parameters
    multimodal_params: Union[FinetuneMultimodalParams, None] = None
    # hugging face related fields
    from_hf_model: Union[str, None] = None
    hf_model_revision: Union[str, None] = None
    # hf related fields
    hf_api_token: Union[str, None] = None
    hf_output_repo_name: Union[str, None] = None
