# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RemediationRejectParams"]


class RemediationRejectParams(TypedDict, total=False):
    cluster_id: Required[str]

    instance_id: Required[str]

    comment: str
    """Comment explaining the action."""
