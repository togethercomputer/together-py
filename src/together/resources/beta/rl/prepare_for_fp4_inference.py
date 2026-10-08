# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.rl import prepare_for_fp4_inference_create_params, prepare_for_fp4_inference_estimate_cost_params
from ....types.post_training.quantization_job import QuantizationJob
from ....types.post_training.quantization_estimate import QuantizationEstimate
from ....types.beta.rl.prepare_for_fp4_inference_list_response import PrepareForFp4InferenceListResponse
from ....types.beta.rl.prepare_for_fp4_inference_list_events_response import PrepareForFp4InferenceListEventsResponse

__all__ = ["PrepareForFp4InferenceResource", "AsyncPrepareForFp4InferenceResource"]


class PrepareForFp4InferenceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PrepareForFp4InferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return PrepareForFp4InferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PrepareForFp4InferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return PrepareForFp4InferenceResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        inputs: prepare_for_fp4_inference_create_params.Inputs,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QuantizationJob:
        """
        Merges a fine-tuned adapter into its base model and prepares the result for FP4
        inference. The adapter is resolved when the request is made, so a request naming
        a model that does not exist in the project, is not an adapter, was not produced
        by fine-tuning, has no base model to merge into, or uses an unsupported base
        model is rejected with 400 rather than accepted and failed later. The run is
        priced before it is created, and a project that cannot cover it is answered 402.

        Args:
          inputs: Adapter inputs to prepare.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/shaping/prepare-for-fp4-inference",
            body=maybe_transform(
                {"inputs": inputs}, prepare_for_fp4_inference_create_params.PrepareForFp4InferenceCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
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
    ) -> QuantizationJob:
        """
        Retrieve a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/shaping/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
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
    ) -> PrepareForFp4InferenceListResponse:
        """List shaping jobs owned by the caller's project."""
        return self._get(
            "/shaping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareForFp4InferenceListResponse,
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
    ) -> QuantizationJob:
        """
        Request cancellation of a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            path_template("/shaping/{id}/cancel", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
        )

    def estimate_cost(
        self,
        *,
        inputs: prepare_for_fp4_inference_estimate_cost_params.Inputs,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QuantizationEstimate:
        """
        Reports the price and expected wall-clock time for preparing the named adapter
        without creating a job. The request body is the same as POST
        /shaping/prepare-for-fp4-inference, so a caller can price exactly the job it is
        about to submit.

        Args:
          inputs: Adapter inputs to prepare.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/shaping/prepare-for-fp4-inference/estimate",
            body=maybe_transform(
                {"inputs": inputs},
                prepare_for_fp4_inference_estimate_cost_params.PrepareForFp4InferenceEstimateCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationEstimate,
        )

    def list_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PrepareForFp4InferenceListEventsResponse:
        """
        List events for a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/shaping/{id}/events", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareForFp4InferenceListEventsResponse,
        )


class AsyncPrepareForFp4InferenceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPrepareForFp4InferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncPrepareForFp4InferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPrepareForFp4InferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncPrepareForFp4InferenceResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        inputs: prepare_for_fp4_inference_create_params.Inputs,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QuantizationJob:
        """
        Merges a fine-tuned adapter into its base model and prepares the result for FP4
        inference. The adapter is resolved when the request is made, so a request naming
        a model that does not exist in the project, is not an adapter, was not produced
        by fine-tuning, has no base model to merge into, or uses an unsupported base
        model is rejected with 400 rather than accepted and failed later. The run is
        priced before it is created, and a project that cannot cover it is answered 402.

        Args:
          inputs: Adapter inputs to prepare.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/shaping/prepare-for-fp4-inference",
            body=await async_maybe_transform(
                {"inputs": inputs}, prepare_for_fp4_inference_create_params.PrepareForFp4InferenceCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
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
    ) -> QuantizationJob:
        """
        Retrieve a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/shaping/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
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
    ) -> PrepareForFp4InferenceListResponse:
        """List shaping jobs owned by the caller's project."""
        return await self._get(
            "/shaping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareForFp4InferenceListResponse,
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
    ) -> QuantizationJob:
        """
        Request cancellation of a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            path_template("/shaping/{id}/cancel", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationJob,
        )

    async def estimate_cost(
        self,
        *,
        inputs: prepare_for_fp4_inference_estimate_cost_params.Inputs,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> QuantizationEstimate:
        """
        Reports the price and expected wall-clock time for preparing the named adapter
        without creating a job. The request body is the same as POST
        /shaping/prepare-for-fp4-inference, so a caller can price exactly the job it is
        about to submit.

        Args:
          inputs: Adapter inputs to prepare.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/shaping/prepare-for-fp4-inference/estimate",
            body=await async_maybe_transform(
                {"inputs": inputs},
                prepare_for_fp4_inference_estimate_cost_params.PrepareForFp4InferenceEstimateCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuantizationEstimate,
        )

    async def list_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PrepareForFp4InferenceListEventsResponse:
        """
        List events for a shaping job owned by the caller's project.

        Args:
          id: Shaping job ID beginning with `shp-quant-`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/shaping/{id}/events", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PrepareForFp4InferenceListEventsResponse,
        )


class PrepareForFp4InferenceResourceWithRawResponse:
    def __init__(self, prepare_for_fp4_inference: PrepareForFp4InferenceResource) -> None:
        self._prepare_for_fp4_inference = prepare_for_fp4_inference

        self.create = to_raw_response_wrapper(
            prepare_for_fp4_inference.create,
        )
        self.retrieve = to_raw_response_wrapper(
            prepare_for_fp4_inference.retrieve,
        )
        self.list = to_raw_response_wrapper(
            prepare_for_fp4_inference.list,
        )
        self.cancel = to_raw_response_wrapper(
            prepare_for_fp4_inference.cancel,
        )
        self.estimate_cost = to_raw_response_wrapper(
            prepare_for_fp4_inference.estimate_cost,
        )
        self.list_events = to_raw_response_wrapper(
            prepare_for_fp4_inference.list_events,
        )


class AsyncPrepareForFp4InferenceResourceWithRawResponse:
    def __init__(self, prepare_for_fp4_inference: AsyncPrepareForFp4InferenceResource) -> None:
        self._prepare_for_fp4_inference = prepare_for_fp4_inference

        self.create = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.cancel,
        )
        self.estimate_cost = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.estimate_cost,
        )
        self.list_events = async_to_raw_response_wrapper(
            prepare_for_fp4_inference.list_events,
        )


class PrepareForFp4InferenceResourceWithStreamingResponse:
    def __init__(self, prepare_for_fp4_inference: PrepareForFp4InferenceResource) -> None:
        self._prepare_for_fp4_inference = prepare_for_fp4_inference

        self.create = to_streamed_response_wrapper(
            prepare_for_fp4_inference.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            prepare_for_fp4_inference.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            prepare_for_fp4_inference.list,
        )
        self.cancel = to_streamed_response_wrapper(
            prepare_for_fp4_inference.cancel,
        )
        self.estimate_cost = to_streamed_response_wrapper(
            prepare_for_fp4_inference.estimate_cost,
        )
        self.list_events = to_streamed_response_wrapper(
            prepare_for_fp4_inference.list_events,
        )


class AsyncPrepareForFp4InferenceResourceWithStreamingResponse:
    def __init__(self, prepare_for_fp4_inference: AsyncPrepareForFp4InferenceResource) -> None:
        self._prepare_for_fp4_inference = prepare_for_fp4_inference

        self.create = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.cancel,
        )
        self.estimate_cost = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.estimate_cost,
        )
        self.list_events = async_to_streamed_response_wrapper(
            prepare_for_fp4_inference.list_events,
        )
