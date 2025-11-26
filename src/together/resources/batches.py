# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import batch_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ..types.batch_job import BatchJob
from ..types.batch_list_response import BatchListResponse
from ..types.batch_create_response import BatchCreateResponse

__all__ = ["BatchesResource", "AsyncBatchesResource"]


class BatchesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return BatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return BatchesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        endpoint: str,
        input_file_id: str,
        completion_window: str | Omit = omit,
        model_id: str | Omit = omit,
        priority: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCreateResponse:
        """
        Create a new batch job with the given input file and endpoint

        Args:
          endpoint: The endpoint to use for batch processing

          input_file_id: ID of the uploaded input file containing batch requests

          completion_window: Time window for batch completion (optional)

          model_id: Model to use for processing batch requests

          priority: Priority for batch processing (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/batches",
            body=maybe_transform(
                {
                    "endpoint": endpoint,
                    "input_file_id": input_file_id,
                    "completion_window": completion_window,
                    "model_id": model_id,
                    "priority": priority,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJob:
        """
        Get details of a batch job by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/batches/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchJob,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchListResponse:
        """List all batch jobs for the authenticated user"""
        return self._get(
            "/batches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchListResponse,
        )

    def cancel(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJob:
        """
        Cancel a batch job by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/batches/{id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchJob,
        )


class AsyncBatchesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncBatchesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        endpoint: str,
        input_file_id: str,
        completion_window: str | Omit = omit,
        model_id: str | Omit = omit,
        priority: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchCreateResponse:
        """
        Create a new batch job with the given input file and endpoint

        Args:
          endpoint: The endpoint to use for batch processing

          input_file_id: ID of the uploaded input file containing batch requests

          completion_window: Time window for batch completion (optional)

          model_id: Model to use for processing batch requests

          priority: Priority for batch processing (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/batches",
            body=await async_maybe_transform(
                {
                    "endpoint": endpoint,
                    "input_file_id": input_file_id,
                    "completion_window": completion_window,
                    "model_id": model_id,
                    "priority": priority,
                },
                batch_create_params.BatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJob:
        """
        Get details of a batch job by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/batches/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchJob,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchListResponse:
        """List all batch jobs for the authenticated user"""
        return await self._get(
            "/batches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchListResponse,
        )

    async def cancel(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJob:
        """
        Cancel a batch job by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/batches/{id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BatchJob,
        )


class BatchesResourceWithRawResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.create = to_raw_response_wrapper(
            batches.create,
        )
        self.retrieve = to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = to_raw_response_wrapper(
            batches.list,
        )
        self.cancel = to_raw_response_wrapper(
            batches.cancel,
        )


class AsyncBatchesResourceWithRawResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.create = async_to_raw_response_wrapper(
            batches.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            batches.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            batches.cancel,
        )


class BatchesResourceWithStreamingResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.create = to_streamed_response_wrapper(
            batches.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            batches.list,
        )
        self.cancel = to_streamed_response_wrapper(
            batches.cancel,
        )


class AsyncBatchesResourceWithStreamingResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.create = async_to_streamed_response_wrapper(
            batches.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            batches.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            batches.cancel,
        )
