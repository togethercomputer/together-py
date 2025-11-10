# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import hardware_list_params
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
from ..types.hardware_list_response import HardwareListResponse

__all__ = ["HardwareResource", "AsyncHardwareResource"]


class HardwareResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HardwareResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return HardwareResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HardwareResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return HardwareResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> HardwareListResponse:
        """Returns a list of available hardware configurations for deploying models.

        When a
        model parameter is provided, it returns only hardware configurations compatible
        with that model, including their current availability status.

        Args:
          model: Filter hardware configurations by model compatibility. When provided, the
              response includes availability status for each compatible configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/hardware",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"model": model}, hardware_list_params.HardwareListParams),
            ),
            cast_to=HardwareListResponse,
        )


class AsyncHardwareResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHardwareResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncHardwareResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHardwareResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncHardwareResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> HardwareListResponse:
        """Returns a list of available hardware configurations for deploying models.

        When a
        model parameter is provided, it returns only hardware configurations compatible
        with that model, including their current availability status.

        Args:
          model: Filter hardware configurations by model compatibility. When provided, the
              response includes availability status for each compatible configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/hardware",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"model": model}, hardware_list_params.HardwareListParams),
            ),
            cast_to=HardwareListResponse,
        )


class HardwareResourceWithRawResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.list = to_raw_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithRawResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.list = async_to_raw_response_wrapper(
            hardware.list,
        )


class HardwareResourceWithStreamingResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.list = to_streamed_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithStreamingResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.list = async_to_streamed_response_wrapper(
            hardware.list,
        )
