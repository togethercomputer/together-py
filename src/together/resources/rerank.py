# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal

import httpx

from ..types import rerank_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.rerank_create_response import RerankCreateResponse

__all__ = ["RerankResource", "AsyncRerankResource"]


class RerankResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RerankResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RerankResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RerankResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RerankResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        documents: Union[Iterable[Dict[str, object]], SequenceNotStr[str]],
        model: Union[Literal["Salesforce/Llama-Rank-v1"], str],
        query: str,
        rank_fields: SequenceNotStr[str] | Omit = omit,
        return_documents: bool | Omit = omit,
        top_n: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RerankCreateResponse:
        """
        Query a reranker model

        Args:
          documents: List of documents, which can be either strings or objects.

          model: The model to be used for the rerank request.

              [See all of Together AI's rerank models](https://docs.together.ai/docs/serverless-models#rerank-models)

          query: The search query to be used for ranking.

          rank_fields: List of keys in the JSON Object document to rank by. Defaults to use all
              supplied keys for ranking.

          return_documents: Whether to return supplied documents with the response.

          top_n: The number of top results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/rerank",
            body=maybe_transform(
                {
                    "documents": documents,
                    "model": model,
                    "query": query,
                    "rank_fields": rank_fields,
                    "return_documents": return_documents,
                    "top_n": top_n,
                },
                rerank_create_params.RerankCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankCreateResponse,
        )


class AsyncRerankResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRerankResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRerankResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRerankResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRerankResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        documents: Union[Iterable[Dict[str, object]], SequenceNotStr[str]],
        model: Union[Literal["Salesforce/Llama-Rank-v1"], str],
        query: str,
        rank_fields: SequenceNotStr[str] | Omit = omit,
        return_documents: bool | Omit = omit,
        top_n: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RerankCreateResponse:
        """
        Query a reranker model

        Args:
          documents: List of documents, which can be either strings or objects.

          model: The model to be used for the rerank request.

              [See all of Together AI's rerank models](https://docs.together.ai/docs/serverless-models#rerank-models)

          query: The search query to be used for ranking.

          rank_fields: List of keys in the JSON Object document to rank by. Defaults to use all
              supplied keys for ranking.

          return_documents: Whether to return supplied documents with the response.

          top_n: The number of top results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/rerank",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "model": model,
                    "query": query,
                    "rank_fields": rank_fields,
                    "return_documents": return_documents,
                    "top_n": top_n,
                },
                rerank_create_params.RerankCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankCreateResponse,
        )


class RerankResourceWithRawResponse:
    def __init__(self, rerank: RerankResource) -> None:
        self._rerank = rerank

        self.create = to_raw_response_wrapper(
            rerank.create,
        )


class AsyncRerankResourceWithRawResponse:
    def __init__(self, rerank: AsyncRerankResource) -> None:
        self._rerank = rerank

        self.create = async_to_raw_response_wrapper(
            rerank.create,
        )


class RerankResourceWithStreamingResponse:
    def __init__(self, rerank: RerankResource) -> None:
        self._rerank = rerank

        self.create = to_streamed_response_wrapper(
            rerank.create,
        )


class AsyncRerankResourceWithStreamingResponse:
    def __init__(self, rerank: AsyncRerankResource) -> None:
        self._rerank = rerank

        self.create = async_to_streamed_response_wrapper(
            rerank.create,
        )
