# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .model_weights import ModelWeights

__all__ = ["Model"]


class Model(BaseModel):
    """
    Custom or derived model registered in a project and backed by versioned weight files.
    """

    id: str
    """Unique model identifier."""

    name: str
    """Project-qualified model name in the form `<project_slug>/<model_name>`.

    Create and update requests may use the bare or qualified form.
    """

    organization_id: str = FieldInfo(alias="organizationId")
    """ID of the organization that owns the model's project."""

    project_id: str = FieldInfo(alias="projectId")
    """ID of the project that owns the model."""

    visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"]
    """Who can discover the model.

    `VISIBILITY_PRIVATE` restricts it to the project; `VISIBILITY_INTERNAL` shares
    it with the organization.
    """

    weights: ModelWeights
    """
    Architecture, size, precision, and speculative-decoding metadata derived from
    the model files.
    """

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """
    Resource name of the base model, using
    `projects/{baseProject}/models/{baseModelId}`; empty when the model has no base.
    """

    base_model_id: Optional[str] = FieldInfo(alias="baseModelId", default=None)
    """ID of the supported or custom base model from which this model was derived."""

    description: Optional[str] = None
    """Human-readable description of the model and its intended use."""
