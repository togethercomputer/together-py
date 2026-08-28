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
    Mixture-of-experts routing decisions captured while generating, so training can reuse the same expert selection. Exactly one source is set—legacy inline `data`, or a backend-owned `object_uri` that the manager hydrates before training. The contiguous int32 buffer is reshaped by `shape`, which is always `[num_tokens, num_layers, width]`; packed buffers carry fp32-bitcast routing weights in the trailing top-k columns.
    """

    shape: Required[SequenceNotStr[Union[str, int]]]
    """Buffer shape as `[num_tokens, num_layers, width]`."""

    data: Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]
    """
    Legacy base64-encoded contiguous int32 routing buffer, row-major over (token,
    layer, width).
    """

    object_uri: str
    """Backend-owned S3/R2 object URI containing the contiguous int32 routing buffer.

    Clients relay this URI unchanged; the manager validates and downloads it before
    training.
    """


set_pydantic_config(RoutedExpertsParam, {"arbitrary_types_allowed": True})
