# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel
from .fine_tune_preview_row import FineTunePreviewRow

__all__ = ["FineTunePreviewResponse"]


class FineTunePreviewResponse(BaseModel):
    """Tokenized preview for sampled rows from a fine-tuning training file."""

    dataset_format: Literal["general", "conversation", "instruction"]
    """Detected SFT dataset format for the sampled rows."""

    max_seq_length: int
    """Maximum sequence length configured for the requested model."""

    model: str
    """Name of the base model used to tokenize the sampled rows."""

    rows: List[FineTunePreviewRow]
    """Tokenized preview rows, in the same order as the sampled training file rows."""

    train_on_inputs: bool
    """Whether prompt or user-message tokens contribute to training loss."""
