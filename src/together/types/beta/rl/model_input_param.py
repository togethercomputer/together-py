# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["ModelInput", "Chunk", "ChunkEncodedText"]


class ChunkEncodedText(TypedDict, total=False):
    """Pre-tokenized text content for this input chunk."""

    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""


class Chunk(TypedDict, total=False):
    """A single chunk of model input content."""

    encoded_text: Required[ChunkEncodedText]
    """Pre-tokenized text content for this input chunk."""


class ModelInput(TypedDict, total=False):
    chunks: Required[Iterable[Chunk]]
    """Input chunks for the model"""
