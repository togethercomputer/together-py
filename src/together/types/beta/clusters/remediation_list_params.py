# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RemediationListParams"]


class RemediationListParams(TypedDict, total=False):
    cluster_id: Required[str]

    mode: List[
        Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ]
    ]
    """Filter by remediation mode(s).

    Returns remediations matching any of the specified modes.
    """

    order_by: str
    """Order by expression."""

    page_size: int
    """Maximum results to return."""

    page_token: str
    """Pagination token from previous request."""

    state: List[Literal["PENDING_APPROVAL", "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "AUTO_RESOLVED"]]
    """Filter by state(s). Returns remediations matching any of the specified states.

    - `PENDING_APPROVAL`: Awaiting approval before processing can begin.
    - `PENDING`: Approved and queued for processing.
    - `RUNNING`: Actively being processed.
    - `SUCCEEDED`: Successfully completed.
    - `FAILED`: Failed with an error.
    - `CANCELLED`: Cancelled by user or system.
    - `AUTO_RESOLVED`: The underlying issue was automatically resolved before
      processing.
    """

    trigger: List[Literal["REMEDIATION_TRIGGER_MANUAL", "REMEDIATION_TRIGGER_AUTOMATED"]]
    """Filter by trigger type(s).

    Returns remediations matching any of the specified triggers.
    """
