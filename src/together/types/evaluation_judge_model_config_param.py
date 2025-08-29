# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EvaluationJudgeModelConfigParam"]


class EvaluationJudgeModelConfigParam(TypedDict, total=False):
    model_name: Required[str]
    """Name of the judge model"""

    system_template: Required[str]
    """System prompt template for the judge"""
