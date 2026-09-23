# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .pause_info import PauseInfo
from .rollout_status import RolloutStatus

__all__ = ["Rollout"]


class Rollout(BaseModel):
    """
    Public view of a rollout resource, including runtime progress and any pause or abort reason.
    """

    id: str
    """Output only. Unique rollout identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Output only. Timestamp when the rollout was created."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. Endpoint this rollout belongs to."""

    source_deployment_id: str = FieldInfo(alias="sourceDeploymentId")
    """Output only. Deployment that traffic is shifting away from."""

    state: Literal[
        "ROLLOUT_STATE_RUNNING",
        "ROLLOUT_STATE_PAUSED",
        "ROLLOUT_STATE_STABILIZING",
        "ROLLOUT_STATE_COMPLETED",
        "ROLLOUT_STATE_PENDING",
        "ROLLOUT_STATE_SYSTEM_PAUSED",
        "ROLLOUT_STATE_CANCELLING",
        "ROLLOUT_STATE_CANCELED",
        "ROLLOUT_STATE_PAUSING",
    ]
    """Output only. High-level rollout lifecycle state."""

    status: RolloutStatus
    """Derived runtime progress for a rollout."""

    strategy: Literal[
        "ROLLOUT_STRATEGY_TYPE_ROLLING", "ROLLOUT_STRATEGY_TYPE_CANARY", "ROLLOUT_STRATEGY_TYPE_BLUE_GREEN"
    ]
    """Output only. Rollout strategy selected at creation."""

    target_deployment_id: str = FieldInfo(alias="targetDeploymentId")
    """Output only. Deployment that traffic is shifting toward."""

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
    """Output only. Timestamp when the rollout reached a terminal state."""

    current_step: Optional[int] = FieldInfo(alias="currentStep", default=None)
    """Output only.

    Zero-based index of the current step. Unset while PENDING; step 0 is reported
    explicitly after start.
    """

    current_traffic_percent: Optional[int] = FieldInfo(alias="currentTrafficPercent", default=None)
    """Output only. Applied percentage of traffic on the target deployment."""

    etag: Optional[str] = None
    """Output only. Opaque version tag for optimistic concurrency control."""

    pause_info: Optional[PauseInfo] = FieldInfo(alias="pauseInfo", default=None)
    """Pause metadata returned while a rollout is paused."""

    started_at: Optional[datetime] = FieldInfo(alias="startedAt", default=None)
    """Output only. Timestamp when the rollout started running."""
