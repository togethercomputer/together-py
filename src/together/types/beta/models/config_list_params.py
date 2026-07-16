# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ConfigListParams"]


class ConfigListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous list response."""

    limit: int
    """Maximum number of results to return."""

    reference_model: Annotated[str, PropertyInfo(alias="referenceModel")]
    """
    Model resource-name filter using `projects/{projectId}/models/{modelId}`;
    alternative to `referenceModelId`. If both are set, they must agree.
    """

    reference_model_id: Annotated[str, PropertyInfo(alias="referenceModelId")]
    """Deprecated.

    Use `referenceModel`. Reference model identifier filter; if both are set, they
    must agree.
    """
