# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import path_template
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.endpoints.hardware_list_response import HardwareListResponse
from ....types.beta.endpoints.inference_instance_type import InferenceInstanceType

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
    ) -> InferenceInstanceType:
        """
        Retrieves the GPU resources, pricing, regional availability, and best-effort
        capacity headroom for one inference instance type.

        Args:
          id: Resource identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/public/inference-instance-types/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceInstanceType,
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
    ) -> HardwareListResponse:
        """
        Lists hardware instance types currently available to inference deployments,
        including GPU resources, pricing, regions, and best-effort capacity headroom.
        """
        return self._get(
            "/public/inference-instance-types"
            if self._client._base_url_overridden
            else "https://api.together.ai/v2/public/inference-instance-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
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
    ) -> InferenceInstanceType:
        """
        Retrieves the GPU resources, pricing, regional availability, and best-effort
        capacity headroom for one inference instance type.

        Args:
          id: Resource identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/public/inference-instance-types/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceInstanceType,
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
    ) -> HardwareListResponse:
        """
        Lists hardware instance types currently available to inference deployments,
        including GPU resources, pricing, regions, and best-effort capacity headroom.
        """
        return await self._get(
            "/public/inference-instance-types"
            if self._client._base_url_overridden
            else "https://api.together.ai/v2/public/inference-instance-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HardwareListResponse,
        )


class HardwareResourceWithRawResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.retrieve = to_raw_response_wrapper(
            hardware.retrieve,
        )
        self.list = to_raw_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithRawResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.retrieve = async_to_raw_response_wrapper(
            hardware.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            hardware.list,
        )


class HardwareResourceWithStreamingResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.retrieve = to_streamed_response_wrapper(
            hardware.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithStreamingResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.retrieve = async_to_streamed_response_wrapper(
            hardware.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            hardware.list,
        )
