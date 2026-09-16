# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RegressionCheckParam"]


class RegressionCheckParam(TypedDict, total=False):
    """
    Regression criteria that fail when the target regresses against the source beyond a limit.
    """

    direction: Required[Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]]
    """
    Required direction that indicates whether higher or lower metric values are
    worse.
    """

    max_regression_percent: Annotated[float, PropertyInfo(alias="maxRegressionPercent")]
    """Finite maximum allowed regression percentage, greater than or equal to 0.

    Omitting this value is read as 0. A value of 0 is the strictest budget; any
    regression fails, and exactly-at-budget passes.
    """
