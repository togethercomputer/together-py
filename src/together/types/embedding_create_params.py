# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["EmbeddingCreateParams"]


class EmbeddingCreateParams(TypedDict, total=False):
    input: Required[Union[str, SequenceNotStr[str]]]
    """A string providing the text for the model to embed."""

    model: Required[
        Union[
            Literal[
                "WhereIsAI/UAE-Large-V1",
                "BAAI/bge-large-en-v1.5",
                "BAAI/bge-base-en-v1.5",
                "togethercomputer/m2-bert-80M-8k-retrieval",
            ],
            str,
        ]
    ]
    """The name of the embedding model to use.

    [See all of Together AI's embedding models](https://docs.together.ai/docs/serverless-models#embedding-models)
    """
