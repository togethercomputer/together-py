# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FineTuningModelLimitsParams"]


class FineTuningModelLimitsParams(TypedDict, total=False):
    model_name: Required[str]
    """The model name to get limits for."""
