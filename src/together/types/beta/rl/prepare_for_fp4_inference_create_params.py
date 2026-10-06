# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PrepareForFp4InferenceCreateParams", "Inputs"]


class PrepareForFp4InferenceCreateParams(TypedDict, total=False):
    inputs: Required[Inputs]
    """Adapter inputs to prepare."""


class Inputs(TypedDict, total=False):
    """Adapter inputs to prepare."""

    adapter_object_id: Required[str]
    """Model object ID of the adapter to prepare."""

    adapter_revision_id: str
    """Adapter revision ID to prepare. Omit to use the adapter's current revision."""

    calibration_file_id: str
    """Conversation dataset file ID to use for calibration.

    This field is accepted and stored but not yet validated or used.
    """
