# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ToolChoiceParam", "Function"]


class Function(TypedDict, total=False):
    name: str


class ToolChoiceParam(TypedDict, total=False):
    function: Function

    type: str
