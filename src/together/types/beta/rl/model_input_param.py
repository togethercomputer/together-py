# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .model_input_chunk_param import ModelInputChunk

__all__ = ["ModelInput"]


class ModelInput(TypedDict, total=False):
    chunks: Required[Iterable[ModelInputChunk]]
    """Input chunks for the model"""
