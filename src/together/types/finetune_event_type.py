# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["FinetuneEventType"]

FinetuneEventType: TypeAlias = Literal[
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
