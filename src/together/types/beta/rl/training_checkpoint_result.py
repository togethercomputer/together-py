# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel
from .training_checkpoint import TrainingCheckpoint

__all__ = ["TrainingCheckpointResult"]


class TrainingCheckpointResult(BaseModel):
    """Result of a training checkpoint operation"""

    checkpoint: TrainingCheckpoint
    """The checkpoint this operation created.

    The training session lists the same checkpoint in `training_checkpoints`.
    """
