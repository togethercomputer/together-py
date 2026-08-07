# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr, Base64FileInput
from ...._utils import PropertyInfo
from ...._models import set_pydantic_config

__all__ = ["RoutedExpertsParam"]


class RoutedExpertsParam(TypedDict, total=False):
    """
    Mixture-of-experts routing decisions captured while generating, so training can reuse the same expert selection. A contiguous uint16 buffer of selected expert indices, reshaped by `shape`, which is always `[num_tokens, num_layers, topk]`.
    """

    data: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]
    """
    Base64-encoded contiguous uint16 buffer of selected expert indices, row-major
    over (token, layer, k).
    """

    shape: Required[SequenceNotStr[Union[str, int]]]
    """Buffer shape as `[num_tokens, num_layers, topk]`."""


set_pydantic_config(RoutedExpertsParam, {"arbitrary_types_allowed": True})
