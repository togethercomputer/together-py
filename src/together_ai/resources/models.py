# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import ModelListResponse
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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

__all__ = ["Models", "AsyncModels"]


class Models(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelsWithRawResponse:
        return ModelsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsWithStreamingResponse:
        return ModelsWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelListResponse:
        """Lists all the available models"""
        return self._get(
            "/models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelListResponse,
        )


class AsyncModels(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelsWithRawResponse:
        return AsyncModelsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsWithStreamingResponse:
        return AsyncModelsWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelListResponse:
        """Lists all the available models"""
        return await self._get(
            "/models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelListResponse,
        )


class ModelsWithRawResponse:
    def __init__(self, models: Models) -> None:
        self._models = models

        self.list = to_raw_response_wrapper(
            models.list,
        )


class AsyncModelsWithRawResponse:
    def __init__(self, models: AsyncModels) -> None:
        self._models = models

        self.list = async_to_raw_response_wrapper(
            models.list,
        )


class ModelsWithStreamingResponse:
    def __init__(self, models: Models) -> None:
        self._models = models

        self.list = to_streamed_response_wrapper(
            models.list,
        )


class AsyncModelsWithStreamingResponse:
    def __init__(self, models: AsyncModels) -> None:
        self._models = models

        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
