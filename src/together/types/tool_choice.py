# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ToolChoice", "Function"]


class Function(BaseModel):
    arguments: str

    name: str


class ToolChoice(BaseModel):
    id: str

    function: Function

    index: float

    type: Literal["function"]
