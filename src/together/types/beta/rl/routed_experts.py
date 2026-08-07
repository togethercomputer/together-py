# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union

from ...._models import BaseModel

__all__ = ["RoutedExperts"]


class RoutedExperts(BaseModel):
    """
    Mixture-of-experts routing decisions captured while generating, so training can reuse the same expert selection. A contiguous uint16 buffer of selected expert indices, reshaped by `shape`, which is always `[num_tokens, num_layers, topk]`.
    """

    data: str
    """
    Base64-encoded contiguous uint16 buffer of selected expert indices, row-major
    over (token, layer, k).
    """

    shape: List[Union[str, int]]
    """Buffer shape as `[num_tokens, num_layers, topk]`."""
