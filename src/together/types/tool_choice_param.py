# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ToolChoiceParam", "Function"]


class Function(TypedDict, total=False):
    arguments: Required[str]

    name: Required[str]


class ToolChoiceParam(TypedDict, total=False):
    id: Required[str]

    function: Required[Function]

    index: Required[float]

    type: Required[Literal["function"]]
