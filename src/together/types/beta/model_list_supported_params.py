# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelListSupportedParams"]


class ModelListSupportedParams(TypedDict, total=False):
    adapter_mode: Annotated[
        Literal["ADAPTER_MODE_FIXED", "ADAPTER_MODE_DYNAMIC", "ADAPTER_MODE_DISABLED"],
        PropertyInfo(alias="adapterMode"),
    ]
    """
    Filter models to those with a deployment profile in the selected adapter serving
    mode.
    """

    after: str
    """Cursor from a previous supported-model list response."""

    limit: int
    """Maximum number of models to return."""

    modality: Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"]
    """Filter models by input modality."""

    product: Literal["PRODUCT_SERVERLESS", "PRODUCT_DEDICATED", "PRODUCT_FINE_TUNING"]
    """Filter models by product surface."""

    search: str
    """Case-insensitive search across model IDs, names, and descriptions."""
