# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .rollout_condition import RolloutCondition
from .rollout_step_status import RolloutStepStatus

__all__ = ["RolloutStatus"]


class RolloutStatus(BaseModel):
    """Derived runtime progress for a rollout."""

    steps: List[RolloutStepStatus]
    """Per-step rollout execution summaries."""

    total_steps: int = FieldInfo(alias="totalSteps")
    """Total number of steps in the rollout progression.

    Always serializes when status is present.
    """

    condition: Optional[RolloutCondition] = None
    """Structured reason a rollout stopped progressing."""

    conditions: Optional[List[RolloutCondition]] = None
    """Informational conditions that describe the rollout's current state.

    Omitted when empty; clients should treat an absent key as an empty list.
    """

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """Timestamp of the most recent progress update."""
