# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["ToolsParam", "Function"]


class Function(TypedDict, total=False):
    description: str

    name: str

    parameters: Dict[str, object]
    """A map of parameter names to their values."""


class ToolsParam(TypedDict, total=False):
    function: Function

    type: str
