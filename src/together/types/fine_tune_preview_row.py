# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["FineTunePreviewRow"]


class FineTunePreviewRow(BaseModel):
    """Tokenized representation of one sampled fine-tuning row."""

    input_ids: List[int]
    """Token IDs produced for the sampled row."""

    labels: List[int]
    """Training labels for each token; masked tokens use -100."""

    num_tokens: int
    """Total number of tokens in the preview row after truncation."""

    num_trained_tokens: int
    """Number of tokens in the row that contribute to training loss."""

    tokens: List[str]
    """Raw token strings produced for the sampled row."""

    trained_spans: List[List[int]]
    """Half-open token index ranges that contribute to training loss."""

    truncated: bool
    """Whether the row was truncated to the model maximum sequence length."""
