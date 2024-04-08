# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FineTuneListResponse", "FineTuneListResponseItem", "FineTuneListResponseItemEvent"]


class FineTuneListResponseItemEvent(BaseModel):
    created_at: Optional[str] = None

    hash: Optional[str] = None

    level: Optional[Literal["info", "warning", "error", "legacy_info", "legacy_iwarning", "legacy_ierror"]] = None

    message: Optional[str] = None

    object: Optional[Literal["FinetuneEvent"]] = None

    param_count: Optional[int] = None

    token_count: Optional[int] = None

    type: Optional[
        Literal[
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
    ] = None

    wandb_url: Optional[str] = None


class FineTuneListResponseItem(BaseModel):
    id: Optional[str] = None

    batch_size: Optional[int] = None

    created_at: Optional[str] = None

    epochs_completed: Optional[int] = None

    eval_steps: Optional[int] = None

    events: Optional[List[FineTuneListResponseItemEvent]] = None

    job_id: Optional[str] = None

    learning_rate: Optional[float] = None

    lora: Optional[bool] = None

    lora_alpha: Optional[int] = None

    lora_dropout: Optional[int] = None

    lora_r: Optional[int] = None

    model: Optional[str] = None

    n_checkpoints: Optional[int] = None

    n_epochs: Optional[int] = None

    output_name: Optional[str] = None

    param_count: Optional[int] = None

    queue_depth: Optional[int] = None

    status: Optional[
        Literal[
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
    ] = None

    token_count: Optional[int] = None

    total_price: Optional[int] = None

    training_file: Optional[str] = None

    training_file_num_lines: Optional[int] = None

    training_file_size: Optional[int] = None

    updated_at: Optional[str] = None

    validation_file: Optional[str] = None

    wandb_project_name: Optional[str] = None

    wandb_url: Optional[str] = None


FineTuneListResponse = List[FineTuneListResponseItem]
