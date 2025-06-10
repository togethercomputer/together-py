# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TrainingMethodSftParam"]


class TrainingMethodSftParam(TypedDict, total=False):
    method: Required[Literal["sft"]]

    train_on_inputs: Required[Union[bool, Literal["auto"]]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """
