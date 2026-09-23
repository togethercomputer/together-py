# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..shadow_source_response import ShadowSourceResponse
from .shadow_experiments.shadow_experiment_target import ShadowExperimentTarget

__all__ = ["ShadowExperiment"]


class ShadowExperiment(BaseModel):
    """
    Experiment that mirrors sampled endpoint requests to target deployments without changing client responses.
    """

    id: str
    """Output only. Unique shadow experiment identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the experiment was created."""

    created_by: str = FieldInfo(alias="createdBy")
    """Identifier of the principal that created the experiment."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. Endpoint whose traffic this experiment samples."""

    etag: str
    """Opaque version tag for optimistic concurrency control.

    Returned on read; set it on update or delete requests for consistent
    read-modify-write.
    """

    name: str
    """Human-readable shadow experiment name, unique within the endpoint.

    At most 256 characters.
    """

    project_id: str = FieldInfo(alias="projectId")
    """Output only. Project that owns the parent endpoint."""

    source: ShadowSourceResponse
    """Endpoint traffic source returned for a shadow experiment."""

    state: Literal["SHADOW_EXPERIMENT_STATE_ACTIVE", "SHADOW_EXPERIMENT_STATE_INACTIVE"]
    """Derived serving state, active when the experiment has at least one target."""

    targets: List[ShadowExperimentTarget]
    """Target deployments that receive mirrored traffic."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Timestamp when the experiment was last updated."""

    description: Optional[str] = None
    """User defined description."""
