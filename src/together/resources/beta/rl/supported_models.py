# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.rl.rl_supported_models import RlSupportedModels

__all__ = ["SupportedModelsResource", "AsyncSupportedModelsResource"]


class SupportedModelsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SupportedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return SupportedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SupportedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return SupportedModelsResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RlSupportedModels:
        """
        Returns the models supported by the RL service and their limits for
        training/sampling operations.
        """
        return self._get(
            "/rl/supported-models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RlSupportedModels,
        )


class AsyncSupportedModelsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSupportedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncSupportedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSupportedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncSupportedModelsResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RlSupportedModels:
        """
        Returns the models supported by the RL service and their limits for
        training/sampling operations.
        """
        return await self._get(
            "/rl/supported-models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RlSupportedModels,
        )


class SupportedModelsResourceWithRawResponse:
    def __init__(self, supported_models: SupportedModelsResource) -> None:
        self._supported_models = supported_models

        self.get = to_raw_response_wrapper(
            supported_models.get,
        )


class AsyncSupportedModelsResourceWithRawResponse:
    def __init__(self, supported_models: AsyncSupportedModelsResource) -> None:
        self._supported_models = supported_models

        self.get = async_to_raw_response_wrapper(
            supported_models.get,
        )


class SupportedModelsResourceWithStreamingResponse:
    def __init__(self, supported_models: SupportedModelsResource) -> None:
        self._supported_models = supported_models

        self.get = to_streamed_response_wrapper(
            supported_models.get,
        )


class AsyncSupportedModelsResourceWithStreamingResponse:
    def __init__(self, supported_models: AsyncSupportedModelsResource) -> None:
        self._supported_models = supported_models

        self.get = async_to_streamed_response_wrapper(
            supported_models.get,
        )
