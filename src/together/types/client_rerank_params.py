# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["ClientRerankParams"]


class ClientRerankParams(TypedDict, total=False):
    documents: Required[Union[Iterable[Dict[str, object]], List[str]]]
    """List of documents, which can be either strings or objects."""

    model: Required[str]
    """The model to be used for the rerank request."""

    query: Required[str]
    """The search query to be used for ranking."""

    rank_fields: List[str]
    """List of keys in the JSON Object document to rank by.

    Defaults to use all supplied keys for ranking.
    """

    return_documents: bool
    """Whether to return supplied documents with the response."""

    top_n: int
    """The number of top results to return."""
