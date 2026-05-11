# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BatchCreateParams"]


class BatchCreateParams(TypedDict, total=False):
    endpoint: Required[Literal["/v1/chat/completions", "/v1/audio/transcriptions", "/v1/audio/translations"]]
    """The endpoint to use for batch processing.

    Each line of the uploaded input file is dispatched against this endpoint.

    - `/v1/chat/completions` — chat completion batches
    - `/v1/audio/transcriptions` — audio transcription batches (e.g.
      `openai/whisper-large-v3`)
    - `/v1/audio/translations` — audio translation batches
    """

    input_file_id: Required[str]
    """ID of the uploaded input file containing batch requests"""

    completion_window: str
    """Time window for batch completion (optional)"""

    model_id: str
    """Model to use for processing batch requests"""

    priority: int
    """Priority for batch processing (optional)"""
