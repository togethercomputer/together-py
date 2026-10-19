# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .shaping_job_type import ShapingJobType
from .quantization_event import QuantizationEvent
from .shaping_job_status import ShapingJobStatus
from .quantization_results import QuantizationResults

__all__ = ["QuantizationJob", "Params", "ParamsConfiguration", "ParamsInputs"]


class ParamsConfiguration(BaseModel):
    """Server-resolved configuration for the run."""

    base_model_name: str
    """Qualified name of the base model."""

    base_object_id: str
    """Model object ID of the base model the prepared model was fine-tuned from."""

    base_revision_id: str
    """Revision ID of that base model."""

    api_model_name: str = FieldInfo(alias="model_name")
    """Qualified name of the model, which the produced model is named after."""

    api_model_project_id: str = FieldInfo(alias="model_project_id")
    """Project the model belongs to."""

    api_model_revision_id: str = FieldInfo(alias="model_revision_id")
    """Revision of the model selected for preparation."""

    user_id: str
    """User whose scope is used to fetch the model weights."""


class ParamsInputs(BaseModel):
    """Inputs requested by the caller."""

    calibration_file_id: Optional[str] = None
    """Conversation dataset file ID to use for calibration.

    Upload it first with `POST /v1/files` using purpose `calibration` and file type
    `jsonl`. Each JSONL row must contain a `messages` array and may contain a
    `tools` array. When provided, the job draws half of the calibration corpus from
    this file and half from a general-text corpus. When omitted, the job calibrates
    on the general-text corpus only. The request is rejected unless the file exists
    in the request project, has finished uploading, has passed files API validation
    as a conversation dataset, is not empty, and is at most 64 MiB. A `fine-tune`
    purpose file is also accepted so a training file can be reused.
    """

    api_model_object_id: Optional[str] = FieldInfo(alias="model_object_id", default=None)
    """Model object ID of the model to prepare.

    It names the input model; it is not the `results.model_object_id` of a job,
    which names the model the job produced.
    """

    api_model_revision_id: Optional[str] = FieldInfo(alias="model_revision_id", default=None)
    """Revision ID of the model to prepare.

    Omit to use the model's current revision. Only valid with `model_object_id`.
    """


class Params(BaseModel):
    """Job specification."""

    configuration: ParamsConfiguration
    """Server-resolved configuration for the run."""

    inputs: ParamsInputs
    """Inputs requested by the caller."""


class QuantizationJob(BaseModel):
    """Quantization job that prepares a fine-tuned model for FP4 inference."""

    id: str
    """Unique shaping job ID."""

    created_at: datetime
    """Time when the job was created."""

    events: List[QuantizationEvent]
    """Events emitted by the job."""

    job_type: ShapingJobType
    """Type of shaping job."""

    params: Params
    """Job specification."""

    status: ShapingJobStatus
    """Current job status."""

    updated_at: datetime
    """Time when the job was last updated."""

    user_id: str
    """User that created the job."""

    results: Optional[QuantizationResults] = None
    """Model artifacts produced by the job."""
