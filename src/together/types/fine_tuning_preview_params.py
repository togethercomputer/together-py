# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FineTuningPreviewParams"]


class FineTuningPreviewParams(TypedDict, total=False):
    model: Required[str]
    """Name of the base model whose tokenizer and chat template will be used."""

    training_file: Required[str]
    """File-ID of the uploaded JSONL training file to sample for preview."""

    top_k: int
    """Maximum number of rows from the start of the training file to tokenize."""

    train_on_inputs: bool
    """
    Whether prompt or user-message tokens should contribute to training loss in the
    preview.
    """

    training_method: Literal["sft"]
    """Fine-tuning method to preview.

    Only supervised fine-tuning is currently supported.
    """
