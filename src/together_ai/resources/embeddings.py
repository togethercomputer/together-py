# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import httpx

from ..types import EmbeddingsResponse, embedding_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import (
    make_request_options,
)

__all__ = ["Embeddings", "AsyncEmbeddings"]


class Embeddings(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EmbeddingsWithRawResponse:
        return EmbeddingsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EmbeddingsWithStreamingResponse:
        return EmbeddingsWithStreamingResponse(self)

    def create(
        self,
        *,
        input: str,
        model: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmbeddingsResponse:
        """
        Creates an embedding vector representing the input text

        Args:
          input: A string providing the text for the model to embed.

          model: The name of the embedding model to use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/embeddings",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                },
                embedding_create_params.EmbeddingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EmbeddingsResponse,
        )


class AsyncEmbeddings(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEmbeddingsWithRawResponse:
        return AsyncEmbeddingsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEmbeddingsWithStreamingResponse:
        return AsyncEmbeddingsWithStreamingResponse(self)

    async def create(
        self,
        *,
        input: str,
        model: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EmbeddingsResponse:
        """
        Creates an embedding vector representing the input text

        Args:
          input: A string providing the text for the model to embed.

          model: The name of the embedding model to use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/embeddings",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                },
                embedding_create_params.EmbeddingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EmbeddingsResponse,
        )


class EmbeddingsWithRawResponse:
    def __init__(self, embeddings: Embeddings) -> None:
        self._embeddings = embeddings

        self.create = to_raw_response_wrapper(
            embeddings.create,
        )


class AsyncEmbeddingsWithRawResponse:
    def __init__(self, embeddings: AsyncEmbeddings) -> None:
        self._embeddings = embeddings

        self.create = async_to_raw_response_wrapper(
            embeddings.create,
        )


class EmbeddingsWithStreamingResponse:
    def __init__(self, embeddings: Embeddings) -> None:
        self._embeddings = embeddings

        self.create = to_streamed_response_wrapper(
            embeddings.create,
        )


class AsyncEmbeddingsWithStreamingResponse:
    def __init__(self, embeddings: AsyncEmbeddings) -> None:
        self._embeddings = embeddings

        self.create = async_to_streamed_response_wrapper(
            embeddings.create,
        )
