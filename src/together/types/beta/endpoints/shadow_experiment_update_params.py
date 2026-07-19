# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..shadow_source_param import ShadowSourceParam

__all__ = ["ShadowExperimentUpdateParams"]


class ShadowExperimentUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Required fields to update, such as description or source."""

    description: str
    """Updated free-form description."""

    etag: str
    """Opaque version tag from a prior read for optimistic concurrency."""

    source: ShadowSourceParam
    """Traffic source for a shadow experiment.

    The public API supports endpoint sources only.
    """
