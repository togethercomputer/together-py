# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from ...._models import BaseModel
from .tensor_data import TensorData

__all__ = ["LossFnOutput"]


class LossFnOutput(BaseModel):
    """Output tensors produced by the loss function for one sample."""

    tensors: Dict[str, TensorData]
    """Output tensors keyed by name.

    Built-in losses return `logprobs`: the model's float32 per-token
    log-probabilities under the current policy, one value per token of the sample's
    input. Positions excluded from the loss, such as zero-weight positions, are
    masked to zero rather than true log-probabilities.
    """
