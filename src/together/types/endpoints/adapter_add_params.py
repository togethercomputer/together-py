# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AdapterAddParams"]


class AdapterAddParams(TypedDict, total=False):
    model_id: Required[str]
    """Combined identifier in format "endpoint_name:adapter_model_name"."""
