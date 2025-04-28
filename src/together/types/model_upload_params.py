# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelUploadParams"]


class ModelUploadParams(TypedDict, total=False):
    model_name: Required[str]
    """The name to give to your uploaded model"""

    model_source: Required[str]
    """The source location of the model (Hugging Face repo or S3 path)"""

    description: str
    """A description of your model"""

    hf_token: str
    """Hugging Face token (if uploading from Hugging Face)"""
