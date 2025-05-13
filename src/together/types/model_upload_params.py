# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ModelUploadParams"]


class ModelUploadParams(TypedDict, total=False):
    model_name: Required[str]
    """The name to give to your uploaded model"""

    model_source: Required[str]
    """The source location of the model (Hugging Face repo or S3 path)"""

    base_model: str
    """
    The base model to use for an adapter if setting it to run against a serverless
    pool. Only used for model_type `adapter`.
    """

    description: str
    """A description of your model"""

    hf_token: str
    """Hugging Face token (if uploading from Hugging Face)"""

    lora_model: str
    """
    The lora pool to use for an adapter if setting it to run against, say, a
    dedicated pool. Only used for model_type `adapter`.
    """

    model_type: Literal["model", "adapter"]
    """Whether the model is a full model or an adapter"""
