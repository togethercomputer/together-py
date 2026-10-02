# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RemediationCreateParams"]


class RemediationCreateParams(TypedDict, total=False):
    cluster_id: Required[str]

    mode: Required[
        Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
            "REMEDIATION_MODE_HOST_POWER_CYCLE",
        ]
    ]
    """Remediation mode specifies how the remediation should be performed.

    - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
      available host.
    - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
      provisions a new one on a different host.
    - `REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT`: Evicts the VM without
      provisioning a replacement.
    - `REMEDIATION_MODE_REBOOT_VM`: Reboots the VM in place.
    - `REMEDIATION_MODE_HOST_POWER_CYCLE`: Cordons and power-cycles the bare-metal
      host while preserving host and node identity.
    """

    remediation_id: str
    """Client-specified ID for idempotency."""

    reason: str
    """User-provided reason for the remediation."""
