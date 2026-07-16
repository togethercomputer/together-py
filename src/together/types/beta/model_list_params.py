# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelListParams"]


class ModelListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous model list response."""

    limit: int
    """Maximum number of models to return."""

    organization_id: Annotated[str, PropertyInfo(alias="organizationId")]
    """Organization whose shared models should be included.

    Defaults to the authenticated project's organization.
    """

    visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"]
    """Model visibility.

    Private means it is scoped to the project. Internal means it is scoped to the
    organization.
    """
