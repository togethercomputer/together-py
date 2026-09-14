# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EndpointDeleteParams"]


class EndpointDeleteParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    etag: str
    """Etag for optimistic concurrency.

    If set, the delete is rejected if the current etag does not match.
    """
