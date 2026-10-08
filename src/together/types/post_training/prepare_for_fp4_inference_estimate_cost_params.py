# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PrepareForFp4InferenceEstimateCostParams", "Inputs"]


class PrepareForFp4InferenceEstimateCostParams(TypedDict, total=False):
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

    Upload it first with `POST /v1/files` using purpose `calibration` and file type
    `jsonl`. Each JSONL row must contain a `messages` array and may contain a
    `tools` array. When provided, the job draws half of the calibration corpus from
    this file and half from a general-text corpus. When omitted, the job calibrates
    on the general-text corpus only. The request is rejected unless the file exists
    in the request project, has finished uploading, has passed files API validation
    as a conversation dataset, is not empty, and is at most 64 MiB. A `fine-tune`
    purpose file is also accepted so a training file can be reused.
    """
