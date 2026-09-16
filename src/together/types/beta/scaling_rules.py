# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .scaling_policy import ScalingPolicy

__all__ = ["ScalingRules"]


class ScalingRules(BaseModel):
    """Rate limits applied after stabilization and before replica bounds."""

    policies: Optional[List[ScalingPolicy]] = None
    """Non-empty lists replace the existing policies.

    To clear policies, include `autoscaling.scaleDown.policies` or
    `autoscaling.scaleUp.policies` in the update mask and supply an empty scaling
    rules object or `policies: []`.
    """

    select_policy: Optional[
        Literal["SCALING_POLICY_SELECT_MAX", "SCALING_POLICY_SELECT_MIN", "SCALING_POLICY_SELECT_DISABLED"]
    ] = FieldInfo(alias="selectPolicy", default=None)
    """
    `SCALING_POLICY_SELECT_MIN` chooses the policy allowing the smallest replica
    change; `SCALING_POLICY_SELECT_MAX` chooses the largest. These are caps, not
    guaranteed changes. `SCALING_POLICY_SELECT_DISABLED` holds this direction steady
    while replica bounds still apply. Omitted preserves the existing selector on
    update. When no selector is configured, authored policies use MAX; with no
    policies configured, the platform defaults apply. To reset the selector, include
    `autoscaling.scaleDown.selectPolicy` or `autoscaling.scaleUp.selectPolicy` in
    the update mask and omit `selectPolicy`. Clear both policies and `selectPolicy`
    to restore inherited defaults.
    """
