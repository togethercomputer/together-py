# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["EncodedTextChunk"]


class EncodedTextChunk(TypedDict, total=False):
    """Pre-tokenized text content for a model input chunk."""

    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""
