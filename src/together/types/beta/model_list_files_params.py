# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelListFilesParams"]


class ModelListFilesParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    revision_id: Annotated[str, PropertyInfo(alias="revisionId")]
    """Revision identifier to read from."""
