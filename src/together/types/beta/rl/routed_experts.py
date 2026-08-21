# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ...._models import BaseModel

__all__ = ["RoutedExperts"]


class RoutedExperts(BaseModel):
    """
    Mixture-of-experts routing decisions captured while generating, so training can reuse the same expert selection. Exactly one source is set—legacy inline `data`, or a backend-owned `object_uri` that the manager hydrates before training. The contiguous int32 buffer is reshaped by `shape`, which is always `[num_tokens, num_layers, width]`; packed buffers carry fp32-bitcast routing weights in the trailing top-k columns.
    """

    shape: List[Union[str, int]]
    """Buffer shape as `[num_tokens, num_layers, width]`."""

    data: Optional[str] = None
    """
    Legacy base64-encoded contiguous int32 routing buffer, row-major over (token,
    layer, width).
    """

    object_uri: Optional[str] = None
    """Backend-owned S3/R2 object URI containing the contiguous int32 routing buffer.

    Clients relay this URI unchanged; the manager validates and downloads it before
    training.
    """
