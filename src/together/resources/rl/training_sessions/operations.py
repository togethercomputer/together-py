# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NoneType, NotGiven, not_given
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

    def retrieve_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves the current status and result of a forward-backward operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/rl/training-sessions/{session_id}/operations/forward-backward/{operation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_optim_step(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves the current status and result of an optim-step operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/rl/training-sessions/{session_id}/operations/optim-step/{operation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

    async def retrieve_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves the current status and result of a forward-backward operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/rl/training-sessions/{session_id}/operations/forward-backward/{operation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_optim_step(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Retrieves the current status and result of an optim-step operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/rl/training-sessions/{session_id}/operations/optim-step/{operation_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.retrieve_forward_backward = to_raw_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_optim_step = to_raw_response_wrapper(
            operations.retrieve_optim_step,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.retrieve_forward_backward = async_to_raw_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_optim_step = async_to_raw_response_wrapper(
            operations.retrieve_optim_step,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.retrieve_forward_backward = to_streamed_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_optim_step = to_streamed_response_wrapper(
            operations.retrieve_optim_step,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.retrieve_forward_backward = async_to_streamed_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_optim_step = async_to_streamed_response_wrapper(
            operations.retrieve_optim_step,
        )
