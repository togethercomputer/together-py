# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .costs import (
    CostsResource,
    AsyncCostsResource,
    CostsResourceWithRawResponse,
    AsyncCostsResourceWithRawResponse,
    CostsResourceWithStreamingResponse,
    AsyncCostsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["UsageResource", "AsyncUsageResource"]


class UsageResource(SyncAPIResource):
    @cached_property
    def costs(self) -> CostsResource:
        return CostsResource(self._client)

    @cached_property
    def with_raw_response(self) -> UsageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return UsageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return UsageResourceWithStreamingResponse(self)


class AsyncUsageResource(AsyncAPIResource):
    @cached_property
    def costs(self) -> AsyncCostsResource:
        return AsyncCostsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUsageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncUsageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncUsageResourceWithStreamingResponse(self)


class UsageResourceWithRawResponse:
    def __init__(self, usage: UsageResource) -> None:
        self._usage = usage

    @cached_property
    def costs(self) -> CostsResourceWithRawResponse:
        return CostsResourceWithRawResponse(self._usage.costs)


class AsyncUsageResourceWithRawResponse:
    def __init__(self, usage: AsyncUsageResource) -> None:
        self._usage = usage

    @cached_property
    def costs(self) -> AsyncCostsResourceWithRawResponse:
        return AsyncCostsResourceWithRawResponse(self._usage.costs)


class UsageResourceWithStreamingResponse:
    def __init__(self, usage: UsageResource) -> None:
        self._usage = usage

    @cached_property
    def costs(self) -> CostsResourceWithStreamingResponse:
        return CostsResourceWithStreamingResponse(self._usage.costs)


class AsyncUsageResourceWithStreamingResponse:
    def __init__(self, usage: AsyncUsageResource) -> None:
        self._usage = usage

    @cached_property
    def costs(self) -> AsyncCostsResourceWithStreamingResponse:
        return AsyncCostsResourceWithStreamingResponse(self._usage.costs)
