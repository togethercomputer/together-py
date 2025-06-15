# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FineTuneEvent"]


class FineTuneEvent(BaseModel):
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
