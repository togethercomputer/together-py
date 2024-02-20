# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EmbeddingCreateParams"]


class EmbeddingCreateParams(TypedDict, total=False):
    input: Required[str]
    """A string providing the text for the model to embed."""

    model: Required[str]
    """The name of the embedding model to use."""
