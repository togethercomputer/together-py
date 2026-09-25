# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["TrainingCheckpointResult"]


class TrainingCheckpointResult(BaseModel):
    """Result of a save training checkpoint operation"""

    checkpoint_id: str
    """ID of the saved training checkpoint (use for resume via Start)"""
