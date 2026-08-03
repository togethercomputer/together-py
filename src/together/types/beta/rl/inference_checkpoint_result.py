# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["InferenceCheckpointResult"]


class InferenceCheckpointResult(BaseModel):
    """Result of an inference checkpoint operation"""

    registered_model_name: str = FieldInfo(alias="model_name")
    """Registered model name for downloading the checkpoint"""
