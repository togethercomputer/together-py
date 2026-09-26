# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .adam_params import AdamParams
from .muon_params import MuonParams

__all__ = ["OperationOptimStepParams"]


class OperationOptimStepParams(TypedDict, total=False):
    idempotency_key: Required[Annotated[str, PropertyInfo(alias="Idempotency-Key")]]
    """
    Required key that makes retries return the original operation; use a new key for
    changed request bodies.
    """

    adam_params: AdamParams
    """Adam optimizer overrides for this step."""

    muon_params: MuonParams
    """Muon optimizer overrides for this step."""
