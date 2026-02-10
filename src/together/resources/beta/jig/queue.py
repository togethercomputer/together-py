# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.jig import queue_cancel_params, queue_submit_params, queue_metrics_params, queue_retrieve_params
from ....types.beta.jig.queue_cancel_response import QueueCancelResponse
from ....types.beta.jig.queue_submit_response import QueueSubmitResponse
from ....types.beta.jig.queue_metrics_response import QueueMetricsResponse
from ....types.beta.jig.queue_retrieve_response import QueueRetrieveResponse

__all__ = ["QueueResource", "AsyncQueueResource"]


class QueueResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QueueResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return QueueResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QueueResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return QueueResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        model: str,
        request_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueRetrieveResponse:
        """Poll the current status of a previously submitted job.

        Provide the request_id
        and model as query parameters.

        Args:
          model: Model name the job was submitted to

          request_id: Request ID returned from the submit endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/queue/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "model": model,
                        "request_id": request_id,
                    },
                    queue_retrieve_params.QueueRetrieveParams,
                ),
            ),
            cast_to=QueueRetrieveResponse,
        )

    def cancel(
        self,
        *,
        model: str,
        request_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueCancelResponse:
        """Cancel a pending job.

        Only jobs in pending status can be canceled. Running jobs
        cannot be stopped. Returns the job status after the attempt. If the job is not
        pending, returns 409 with the current status unchanged.

        Args:
          model: Model identifier the job was submitted to

          request_id: The request ID returned from the submit endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/queue/cancel",
            body=maybe_transform(
                {
                    "model": model,
                    "request_id": request_id,
                },
                queue_cancel_params.QueueCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueueCancelResponse,
        )

    def metrics(
        self,
        *,
        model: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueMetricsResponse:
        """
        Get the current queue statistics for a model, including pending and running job
        counts.

        Args:
          model: Model name to get metrics for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/queue/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"model": model}, queue_metrics_params.QueueMetricsParams),
            ),
            cast_to=QueueMetricsResponse,
        )

    def submit(
        self,
        *,
        model: str,
        payload: Dict[str, object],
        info: Dict[str, object] | Omit = omit,
        priority: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueSubmitResponse:
        """Submit a new job to the queue for asynchronous processing.

        Jobs are processed in
        strict priority order (higher priority first, FIFO within the same priority).
        Returns a request ID that can be used to poll status or cancel the job.

        Args:
          model: Required model identifier

          payload: Freeform model input. Passed unchanged to the model. Contents are
              model-specific.

          info: Arbitrary JSON metadata stored with the job and returned in status responses.
              The model and system may add or update keys during processing.

          priority: Job priority. Higher values are processed first (strict priority ordering). Jobs
              with equal priority are processed in submission order (FIFO).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/queue/submit",
            body=maybe_transform(
                {
                    "model": model,
                    "payload": payload,
                    "info": info,
                    "priority": priority,
                },
                queue_submit_params.QueueSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueueSubmitResponse,
        )


class AsyncQueueResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQueueResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncQueueResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQueueResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncQueueResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        model: str,
        request_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueRetrieveResponse:
        """Poll the current status of a previously submitted job.

        Provide the request_id
        and model as query parameters.

        Args:
          model: Model name the job was submitted to

          request_id: Request ID returned from the submit endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/queue/status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "model": model,
                        "request_id": request_id,
                    },
                    queue_retrieve_params.QueueRetrieveParams,
                ),
            ),
            cast_to=QueueRetrieveResponse,
        )

    async def cancel(
        self,
        *,
        model: str,
        request_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueCancelResponse:
        """Cancel a pending job.

        Only jobs in pending status can be canceled. Running jobs
        cannot be stopped. Returns the job status after the attempt. If the job is not
        pending, returns 409 with the current status unchanged.

        Args:
          model: Model identifier the job was submitted to

          request_id: The request ID returned from the submit endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/queue/cancel",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "request_id": request_id,
                },
                queue_cancel_params.QueueCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueueCancelResponse,
        )

    async def metrics(
        self,
        *,
        model: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueMetricsResponse:
        """
        Get the current queue statistics for a model, including pending and running job
        counts.

        Args:
          model: Model name to get metrics for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/queue/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"model": model}, queue_metrics_params.QueueMetricsParams),
            ),
            cast_to=QueueMetricsResponse,
        )

    async def submit(
        self,
        *,
        model: str,
        payload: Dict[str, object],
        info: Dict[str, object] | Omit = omit,
        priority: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QueueSubmitResponse:
        """Submit a new job to the queue for asynchronous processing.

        Jobs are processed in
        strict priority order (higher priority first, FIFO within the same priority).
        Returns a request ID that can be used to poll status or cancel the job.

        Args:
          model: Required model identifier

          payload: Freeform model input. Passed unchanged to the model. Contents are
              model-specific.

          info: Arbitrary JSON metadata stored with the job and returned in status responses.
              The model and system may add or update keys during processing.

          priority: Job priority. Higher values are processed first (strict priority ordering). Jobs
              with equal priority are processed in submission order (FIFO).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/queue/submit",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "payload": payload,
                    "info": info,
                    "priority": priority,
                },
                queue_submit_params.QueueSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueueSubmitResponse,
        )


class QueueResourceWithRawResponse:
    def __init__(self, queue: QueueResource) -> None:
        self._queue = queue

        self.retrieve = to_raw_response_wrapper(
            queue.retrieve,
        )
        self.cancel = to_raw_response_wrapper(
            queue.cancel,
        )
        self.metrics = to_raw_response_wrapper(
            queue.metrics,
        )
        self.submit = to_raw_response_wrapper(
            queue.submit,
        )


class AsyncQueueResourceWithRawResponse:
    def __init__(self, queue: AsyncQueueResource) -> None:
        self._queue = queue

        self.retrieve = async_to_raw_response_wrapper(
            queue.retrieve,
        )
        self.cancel = async_to_raw_response_wrapper(
            queue.cancel,
        )
        self.metrics = async_to_raw_response_wrapper(
            queue.metrics,
        )
        self.submit = async_to_raw_response_wrapper(
            queue.submit,
        )


class QueueResourceWithStreamingResponse:
    def __init__(self, queue: QueueResource) -> None:
        self._queue = queue

        self.retrieve = to_streamed_response_wrapper(
            queue.retrieve,
        )
        self.cancel = to_streamed_response_wrapper(
            queue.cancel,
        )
        self.metrics = to_streamed_response_wrapper(
            queue.metrics,
        )
        self.submit = to_streamed_response_wrapper(
            queue.submit,
        )


class AsyncQueueResourceWithStreamingResponse:
    def __init__(self, queue: AsyncQueueResource) -> None:
        self._queue = queue

        self.retrieve = async_to_streamed_response_wrapper(
            queue.retrieve,
        )
        self.cancel = async_to_streamed_response_wrapper(
            queue.cancel,
        )
        self.metrics = async_to_streamed_response_wrapper(
            queue.metrics,
        )
        self.submit = async_to_streamed_response_wrapper(
            queue.submit,
        )
