# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelCreateParams"]


class ModelCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    base_model_id: Required[Annotated[str, PropertyInfo(alias="baseModelId")]]
    """ID of the supported base model from which this model was derived."""

    name: Required[str]
    """Name for the custom model.

    May be bare or qualified as `<project_slug>/<model_name>`; a supplied project
    slug must match the project in the request path.
    """

    type: Required[str]
    """Volume type to create.

    Use `model` or `adapter`; plural `models` and `adapters` are also accepted.
    """

    description: str
    """Human-readable description of the model and its intended use."""
