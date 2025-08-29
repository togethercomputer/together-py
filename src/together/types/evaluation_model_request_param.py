# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EvaluationModelRequestParam"]


class EvaluationModelRequestParam(TypedDict, total=False):
    input_template: Required[str]
    """Input prompt template"""

    max_tokens: Required[int]
    """Maximum number of tokens to generate"""

    model_name: Required[str]
    """Name of the model to evaluate"""

    system_template: Required[str]
    """System prompt template"""

    temperature: Required[float]
    """Sampling temperature"""
