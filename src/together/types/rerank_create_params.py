# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["RerankCreateParams"]


class RerankCreateParams(TypedDict, total=False):
    documents: Required[Union[Iterable[Dict[str, object]], SequenceNotStr[str]]]
    """List of documents, which can be either strings or objects."""

    model: Required[Union[Literal["Salesforce/Llama-Rank-v1"], str]]
    """The model to be used for the rerank request.

    [See all of Together AI's rerank models](https://docs.together.ai/docs/serverless-models#rerank-models)
    """

    query: Required[str]
    """The search query to be used for ranking."""

    rank_fields: SequenceNotStr[str]
    """List of keys in the JSON Object document to rank by.

    Defaults to use all supplied keys for ranking.
    """

    return_documents: bool
    """Whether to return supplied documents with the response."""

    top_n: int
    """The number of top results to return."""
