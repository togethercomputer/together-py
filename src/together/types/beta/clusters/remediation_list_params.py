# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RemediationListParams"]


class RemediationListParams(TypedDict, total=False):
    cluster_id: Required[str]
    """The cluster ID."""

    mode: Literal[
        "REMEDIATION_MODE_VM_ONLY",
        "REMEDIATION_MODE_HOST_AWARE",
        "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
        "REMEDIATION_MODE_REBOOT_VM",
    ]
    """Optional.

    Filter by remediation mode. Returns only remediations matching the specified
    mode.
    """

    order_by: str
    """Optional. Order by expression."""

    page_size: int
    """Optional. Maximum results to return."""

    page_token: str
    """Optional. Pagination token from previous request."""

    state: List[Literal["PENDING_APPROVAL", "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "AUTO_RESOLVED"]]
    """Optional.

    Filter by state(s). Returns remediations matching any of the specified states.
    """

    trigger: Literal["REMEDIATION_TRIGGER_MANUAL", "REMEDIATION_TRIGGER_AUTOMATED"]
    """Optional.

    Filter by trigger type. Returns only remediations matching the specified
    trigger.
    """
