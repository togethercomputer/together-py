# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Model", "Weights", "WeightsParameters", "WeightsParametersByDtype"]


class WeightsParametersByDtype(BaseModel):
    """Number of model parameters stored in one numerical data type."""

    count: str
    """Number of model parameters stored with this data type."""

    dtype: str
    """Numerical data type, such as `float16`, `bfloat16`, or `int8`."""


class WeightsParameters(BaseModel):
    """Total parameter count and breakdown by numerical data type."""

    by_dtype: List[WeightsParametersByDtype] = FieldInfo(alias="byDtype")
    """Parameter counts grouped by numerical data type."""

    total: str
    """Total number of parameters in the model weights."""


class Weights(BaseModel):
    """
    Architecture, size, precision, and speculative-decoding metadata derived from the model files.
    """

    architecture: Optional[str] = None
    """Model architecture detected from the weight metadata."""

    context_length: Optional[str] = FieldInfo(alias="contextLength", default=None)
    """Maximum context length reported by the model metadata."""

    draft_speculator_type: Optional[Literal["DRAFT_SPECULATOR_TYPE_EAGLE", "DRAFT_SPECULATOR_TYPE_PHOENIX"]] = (
        FieldInfo(alias="draftSpeculatorType", default=None)
    )
    """Draft-model speculator family for draft speculative decoding."""

    parameters: Optional[WeightsParameters] = None
    """Total parameter count and breakdown by numerical data type."""

    speculator_mechanism: Optional[
        Literal["SPECULATOR_MECHANISM_DRAFT", "SPECULATOR_MECHANISM_LOOKAHEAD", "SPECULATOR_MECHANISM_MTP"]
    ] = FieldInfo(alias="speculatorMechanism", default=None)
    """Speculative decoding mechanism for speculator weights."""

    type: Optional[Literal["WEIGHTS_TYPE_DEFAULT", "WEIGHTS_TYPE_SPECULATOR", "WEIGHTS_TYPE_ADAPTER"]] = None
    """Role of the weights: full model, speculative draft model, or LoRA adapter."""


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

    weights: Weights
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
