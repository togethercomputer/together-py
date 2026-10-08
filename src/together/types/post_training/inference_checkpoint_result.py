# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .inference_checkpoint import InferenceCheckpoint

__all__ = ["InferenceCheckpointResult"]


class InferenceCheckpointResult(BaseModel):
    """Result of an inference checkpoint operation"""

    checkpoint: InferenceCheckpoint
    """The checkpoint this operation created.

    The training session lists the same checkpoint in `inference_checkpoints`.
    """
