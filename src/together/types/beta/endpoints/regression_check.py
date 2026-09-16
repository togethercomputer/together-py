# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RegressionCheck"]


class RegressionCheck(BaseModel):
    """
    Regression criteria that fail when the target regresses against the source beyond a limit.
    """

    direction: Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]
    """
    Required direction that indicates whether higher or lower metric values are
    worse.
    """

    max_regression_percent: Optional[float] = FieldInfo(alias="maxRegressionPercent", default=None)
    """Finite maximum allowed regression percentage, greater than or equal to 0.

    Omitting this value is read as 0. A value of 0 is the strictest budget; any
    regression fails, and exactly-at-budget passes.
    """
