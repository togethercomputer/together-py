# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PrepareForFp4InferenceCreateParams", "Inputs"]


class PrepareForFp4InferenceCreateParams(TypedDict, total=False):
    inputs: Required[Inputs]
    """Inputs naming the fine-tuned model to prepare."""


class Inputs(TypedDict, total=False):
    """Inputs naming the fine-tuned model to prepare."""

    adapter_object_id: str
    """The former name of `model_object_id`."""

    adapter_revision_id: str
    """The former name of `model_revision_id`. Only valid with `adapter_object_id`."""

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

    model_object_id: str
    """Model object ID of the model to prepare.

    It names the input model; it is not the `results.model_object_id` of a job,
    which names the model the job produced.
    """

    model_revision_id: str
    """Revision ID of the model to prepare.

    Omit to use the model's current revision. Only valid with `model_object_id`.
    """
