# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RolloutCancelParams"]


class RolloutCancelParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    reason: Required[str]
    """Required human-readable reason recorded in the rollout audit trail."""

    disposition: Literal["CANCEL_DISPOSITION_FREEZE", "CANCEL_DISPOSITION_REVERT"]
    """Optional cancel behavior.

    Absent defaults to freeze, which preserves the current traffic split. Revert is
    removed and rejected with FAILED_PRECONDITION; cancel with freeze, then run a
    reverse rollout back to the source.
    """

    etag: str
    """Optional etag for optimistic concurrency."""
