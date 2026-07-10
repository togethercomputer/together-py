# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Remediation", "LinkedAlert"]


class LinkedAlert(BaseModel):
    """Passive health check alert returned by the health check API."""

    alert_name: str
    """Alertmanager alert name."""

    annotations: Dict[str, str]
    """Alertmanager annotations as key-value strings."""

    cluster_id: str
    """Cluster UUID the alert was raised against."""

    passive_health_check_alert_id: str
    """Primary key UUID for the passive health check alert."""

    severity: Literal["PHC_SEVERITY_INFO", "PHC_SEVERITY_WARNING", "PHC_SEVERITY_CRITICAL"]
    """Canonical severity tier for the alert."""

    started_at: datetime
    """Time when the underlying alert first fired."""

    target_vm: str
    """VM name extracted from the Alertmanager labels."""

    instance_id: Optional[str] = None
    """Resolved instance UUID. Empty until the alert is joined to an instance."""

    node_remediation_intent_id: Optional[str] = None
    """Remediation intent UUID attached to this alert, if any."""

    resolved_at: Optional[datetime] = None
    """Time when the underlying alert resolved. Empty while the alert is firing."""


class Remediation(BaseModel):
    """
    Remediation represents a node remediation request for an instance.
    An instance can have multiple remediations over time (e.g., failed attempts followed by retries).
    """

    id: str

    cluster_id: str

    instance_id: str

    mode: Literal[
        "REMEDIATION_MODE_VM_ONLY",
        "REMEDIATION_MODE_HOST_AWARE",
        "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
        "REMEDIATION_MODE_REBOOT_VM",
        "REMEDIATION_MODE_HOST_POWER_CYCLE",
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

    state: Literal[
        "PENDING_APPROVAL",
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "CANCELLED",
        "AUTO_RESOLVED",
        "QUARANTINING",
        "QUARANTINED",
    ]
    """RemediationState represents the lifecycle state of a remediation.

    - `PENDING_APPROVAL`: Awaiting approval before processing can begin.
    - `PENDING`: Approved and queued for processing.
    - `RUNNING`: Actively being processed.
    - `SUCCEEDED`: Successfully completed.
    - `FAILED`: Failed with an error.
    - `CANCELLED`: Cancelled by user or system.
    - `AUTO_RESOLVED`: The underlying issue was automatically resolved before
      processing.
    - `QUARANTINING`: Cordoning or preparing the host before remediation.
    - `QUARANTINED`: Host has been cordoned or isolated for remediation.
    """

    trigger: Literal["REMEDIATION_TRIGGER_MANUAL", "REMEDIATION_TRIGGER_AUTOMATED"]
    """RemediationTrigger specifies how the remediation was triggered.

    - `REMEDIATION_TRIGGER_MANUAL`: A user-initiated remediation (either via web UI
      or API call).
    - `REMEDIATION_TRIGGER_AUTOMATED`: A system-initiated remediation that requires
      approval.
    """

    active_health_check_run_id: Optional[str] = None
    """Active health check run ID (UUID) that triggered this remediation."""

    create_time: Optional[datetime] = None
    """When the remediation was created."""

    end_time: Optional[datetime] = None
    """When the remediation completed."""

    error_message: Optional[str] = None
    """Error message if the remediation failed."""

    instance_name: Optional[str] = None
    """Display name of the targeted instance."""

    linked_alerts: Optional[List[LinkedAlert]] = None
    """
    Passive health check alerts linked to this remediation, including resolved
    alerts.
    """

    passive_health_check_event_id: Optional[str] = None
    """Passive health check event ID that triggered this remediation."""

    reason: Optional[str] = None
    """User-provided reason for the remediation."""

    requested_by: Optional[str] = None
    """Who requested the remediation."""

    review_comment: Optional[str] = None
    """Review comment."""

    review_time: Optional[datetime] = None
    """When the remediation was reviewed."""

    reviewed_by: Optional[str] = None
    """Who reviewed the remediation."""

    start_time: Optional[datetime] = None
    """When processing started."""

    update_time: Optional[datetime] = None
    """When the remediation was last updated."""
