# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ModelResourceStopParams"]


class ModelResourceStopParams(TypedDict, total=False):
    force: bool
    """Stop the resource even if active training sessions are attached"""
