# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .encoded_text_chunk_param import EncodedTextChunk

__all__ = ["ModelInputChunk"]


class ModelInputChunk(TypedDict, total=False):
    """A single chunk of model input content."""

    encoded_text: Required[EncodedTextChunk]
    """Pre-tokenized text content for this input chunk."""
