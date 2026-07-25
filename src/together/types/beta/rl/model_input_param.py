# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["ModelInput", "Chunk", "ChunkEncodedText"]


class ChunkEncodedText(TypedDict, total=False):
    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""


class Chunk(TypedDict, total=False):
    encoded_text: ChunkEncodedText


class ModelInput(TypedDict, total=False):
    chunks: Required[Iterable[Chunk]]
    """Input chunks for the model"""
