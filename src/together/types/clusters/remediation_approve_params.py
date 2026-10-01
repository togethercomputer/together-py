# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RemediationApproveParams"]


class RemediationApproveParams(TypedDict, total=False):
    cluster_id: Required[str]

    instance_id: Required[str]

    comment: str
    """Approval comment explaining the decision."""

    mode: Literal[
        "REMEDIATION_MODE_VM_ONLY",
        "REMEDIATION_MODE_HOST_AWARE",
        "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
        "REMEDIATION_MODE_REBOOT_VM",
        "REMEDIATION_MODE_HOST_POWER_CYCLE",
    ]
    """Remediation mode to use after approval.

    When omitted, the remediation keeps its existing mode.

    - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
      available host.
    - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
      provisions a new one on a different host.
    - `REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT`: Evicts the VM without
      provisioning a replacement.
    - `REMEDIATION_MODE_REBOOT_VM`: Reboots the VM in place.
    - `REMEDIATION_MODE_HOST_POWER_CYCLE`: Power-cycles the bare-metal host after
      cordoning it. This mode cannot be set as an approval override; create a host
      power-cycle remediation directly.
    """
