# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel
from .optimizer_config import OptimizerConfig
from .model_resources_error import ModelResourcesError
from .model_resources_status import ModelResourcesStatus

__all__ = ["ModelResources", "ComputeConfig"]


class ComputeConfig(BaseModel):
    """Compute layout provisioned for the resource."""

    num_generator_replicas: int
    """Number of generator replicas.

    0 means the resource runs the trainer only, with no generator.
    """

    gpu_type: Optional[Literal["H100-80GB", "B200-SXM"]] = None
    """GPU type selected for this resource."""


class ModelResources(BaseModel):
    """Allocated GPU resources that training sessions attach to"""

    id: str
    """Unique identifier for the model resource"""

    base_model: str
    """Base model the resource is provisioned for"""

    compute_config: ComputeConfig
    """Compute layout provisioned for the resource."""

    created_at: datetime
    """Timestamp when the model resource was created"""

    created_by: str
    """ID of the user who created the model resource"""

    lora_enabled: bool
    """Whether the resource hosts LoRA sessions or a full-weight session"""

    optimizer_config: OptimizerConfig
    """Optimizer configuration for this resource."""

    status: ModelResourcesStatus
    """Lifecycle status of the model resource"""

    updated_at: datetime
    """Timestamp when the model resource was last updated"""

    error: Optional[ModelResourcesError] = None
    """Structured detail for the model resource's current error.

    Set when the resource is in an error state.
    """
