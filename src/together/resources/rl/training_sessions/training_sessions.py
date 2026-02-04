# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from ....types.rl import (
    training_session_list_params,
    training_session_create_params,
    training_session_optim_step_params,
    training_session_forward_backward_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["TrainingSessionsResource", "AsyncTrainingSessionsResource"]


class TrainingSessionsResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TrainingSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return TrainingSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TrainingSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return TrainingSessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        body: training_session_create_params.Body,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Creates a training session and returns its details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/rl/training-sessions",
            body=maybe_transform({"body": body}, training_session_create_params.TrainingSessionCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Gets a training session by its ID and returns its details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/rl/training-sessions/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list(
        self,
        *,
        limit: str | Omit = omit,
        offset: str | Omit = omit,
        status: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Lists all training sessions.

        Args:
          limit: Maximum number of sessions to return (1-100)

          offset: Number of sessions to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/rl/training-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "status": status,
                    },
                    training_session_list_params.TrainingSessionListParams,
                ),
            ),
            cast_to=NoneType,
        )

    def forward_backward(
        self,
        session_id: str,
        *,
        body: training_session_forward_backward_params.Body,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits a forward-backward pass operation that will asynchronously compute
        gradients via backpropagation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/rl/training-sessions/{session_id}:forward-backward",
            body=maybe_transform(
                {"body": body}, training_session_forward_backward_params.TrainingSessionForwardBackwardParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def optim_step(
        self,
        session_id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits an optimizer step operation that will asynchronously apply accumulated
        gradients to update model parameters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/rl/training-sessions/{session_id}:optim-step",
            body=maybe_transform({"body": body}, training_session_optim_step_params.TrainingSessionOptimStepParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def stop(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stops a training session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/rl/training-sessions/{session_id}:stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncTrainingSessionsResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTrainingSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTrainingSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTrainingSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncTrainingSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        body: training_session_create_params.Body,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Creates a training session and returns its details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/rl/training-sessions",
            body=await async_maybe_transform(
                {"body": body}, training_session_create_params.TrainingSessionCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Gets a training session by its ID and returns its details.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/rl/training-sessions/{session_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list(
        self,
        *,
        limit: str | Omit = omit,
        offset: str | Omit = omit,
        status: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Lists all training sessions.

        Args:
          limit: Maximum number of sessions to return (1-100)

          offset: Number of sessions to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/rl/training-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "status": status,
                    },
                    training_session_list_params.TrainingSessionListParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def forward_backward(
        self,
        session_id: str,
        *,
        body: training_session_forward_backward_params.Body,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits a forward-backward pass operation that will asynchronously compute
        gradients via backpropagation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/rl/training-sessions/{session_id}:forward-backward",
            body=await async_maybe_transform(
                {"body": body}, training_session_forward_backward_params.TrainingSessionForwardBackwardParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def optim_step(
        self,
        session_id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits an optimizer step operation that will asynchronously apply accumulated
        gradients to update model parameters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/rl/training-sessions/{session_id}:optim-step",
            body=await async_maybe_transform(
                {"body": body}, training_session_optim_step_params.TrainingSessionOptimStepParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def stop(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stops a training session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/rl/training-sessions/{session_id}:stop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class TrainingSessionsResourceWithRawResponse:
    def __init__(self, training_sessions: TrainingSessionsResource) -> None:
        self._training_sessions = training_sessions

        self.create = to_raw_response_wrapper(
            training_sessions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            training_sessions.retrieve,
        )
        self.list = to_raw_response_wrapper(
            training_sessions.list,
        )
        self.forward_backward = to_raw_response_wrapper(
            training_sessions.forward_backward,
        )
        self.optim_step = to_raw_response_wrapper(
            training_sessions.optim_step,
        )
        self.stop = to_raw_response_wrapper(
            training_sessions.stop,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._training_sessions.operations)


class AsyncTrainingSessionsResourceWithRawResponse:
    def __init__(self, training_sessions: AsyncTrainingSessionsResource) -> None:
        self._training_sessions = training_sessions

        self.create = async_to_raw_response_wrapper(
            training_sessions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            training_sessions.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            training_sessions.list,
        )
        self.forward_backward = async_to_raw_response_wrapper(
            training_sessions.forward_backward,
        )
        self.optim_step = async_to_raw_response_wrapper(
            training_sessions.optim_step,
        )
        self.stop = async_to_raw_response_wrapper(
            training_sessions.stop,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._training_sessions.operations)


class TrainingSessionsResourceWithStreamingResponse:
    def __init__(self, training_sessions: TrainingSessionsResource) -> None:
        self._training_sessions = training_sessions

        self.create = to_streamed_response_wrapper(
            training_sessions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            training_sessions.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            training_sessions.list,
        )
        self.forward_backward = to_streamed_response_wrapper(
            training_sessions.forward_backward,
        )
        self.optim_step = to_streamed_response_wrapper(
            training_sessions.optim_step,
        )
        self.stop = to_streamed_response_wrapper(
            training_sessions.stop,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._training_sessions.operations)


class AsyncTrainingSessionsResourceWithStreamingResponse:
    def __init__(self, training_sessions: AsyncTrainingSessionsResource) -> None:
        self._training_sessions = training_sessions

        self.create = async_to_streamed_response_wrapper(
            training_sessions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            training_sessions.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            training_sessions.list,
        )
        self.forward_backward = async_to_streamed_response_wrapper(
            training_sessions.forward_backward,
        )
        self.optim_step = async_to_streamed_response_wrapper(
            training_sessions.optim_step,
        )
        self.stop = async_to_streamed_response_wrapper(
            training_sessions.stop,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._training_sessions.operations)
