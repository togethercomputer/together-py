# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PolicyVersionSegmentParam"]


class PolicyVersionSegmentParam(TypedDict, total=False):
    """A (policy version, starting token) span within a rollout.

    Version 0 is the initial model; each optim_step call increments the version by 1.
    """

    start_token: Required[int]
    """Index of the first token of this segment within the rollout's token sequence.

    Always 0 for the first segment.
    """

    version: Required[int]
    """Model version under which this segment of tokens was generated"""
