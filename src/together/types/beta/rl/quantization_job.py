# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel
from .shaping_job_type import ShapingJobType
from .quantization_event import QuantizationEvent
from .shaping_job_status import ShapingJobStatus
from .quantization_results import QuantizationResults

__all__ = ["QuantizationJob", "Params", "ParamsConfiguration", "ParamsInputs"]


class ParamsConfiguration(BaseModel):
    """Server-resolved configuration for the run."""

    adapter_model_name: str
    """Qualified adapter model name."""

    adapter_project_id: str
    """Project that owns the adapter."""

    adapter_revision_id: str
    """Adapter revision selected for preparation."""

    base_model_name: str
    """Qualified name of the base model."""

    base_object_id: str
    """Model object ID of the adapter's base model."""

    base_revision_id: str
    """Revision ID of the adapter's base model."""

    user_id: str
    """User whose scope is used to fetch the adapter weights."""


class ParamsInputs(BaseModel):
    """Adapter inputs requested by the caller."""

    adapter_object_id: str
    """Model object ID of the adapter to prepare."""

    adapter_revision_id: Optional[str] = None
    """Adapter revision ID to prepare. Omit to use the adapter's current revision."""

    calibration_file_id: Optional[str] = None
    """Conversation dataset file ID to use for calibration.

    This field is accepted and stored but not yet validated or used.
    """


class Params(BaseModel):
    """Job specification."""

    configuration: ParamsConfiguration
    """Server-resolved configuration for the run."""

    inputs: ParamsInputs
    """Adapter inputs requested by the caller."""


class QuantizationJob(BaseModel):
    """Quantization job that prepares an adapter for FP4 inference."""

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
