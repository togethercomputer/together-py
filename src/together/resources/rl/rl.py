# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .training_sessions.training_sessions import (
    TrainingSessionsResource,
    AsyncTrainingSessionsResource,
    TrainingSessionsResourceWithRawResponse,
    AsyncTrainingSessionsResourceWithRawResponse,
    TrainingSessionsResourceWithStreamingResponse,
    AsyncTrainingSessionsResourceWithStreamingResponse,
)

__all__ = ["RlResource", "AsyncRlResource"]


class RlResource(SyncAPIResource):
    @cached_property
    def training_sessions(self) -> TrainingSessionsResource:
        return TrainingSessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> RlResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RlResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RlResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RlResourceWithStreamingResponse(self)


class AsyncRlResource(AsyncAPIResource):
    @cached_property
    def training_sessions(self) -> AsyncTrainingSessionsResource:
        return AsyncTrainingSessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRlResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRlResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRlResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRlResourceWithStreamingResponse(self)


class RlResourceWithRawResponse:
    def __init__(self, rl: RlResource) -> None:
        self._rl = rl

    @cached_property
    def training_sessions(self) -> TrainingSessionsResourceWithRawResponse:
        return TrainingSessionsResourceWithRawResponse(self._rl.training_sessions)


class AsyncRlResourceWithRawResponse:
    def __init__(self, rl: AsyncRlResource) -> None:
        self._rl = rl

    @cached_property
    def training_sessions(self) -> AsyncTrainingSessionsResourceWithRawResponse:
        return AsyncTrainingSessionsResourceWithRawResponse(self._rl.training_sessions)


class RlResourceWithStreamingResponse:
    def __init__(self, rl: RlResource) -> None:
        self._rl = rl

    @cached_property
    def training_sessions(self) -> TrainingSessionsResourceWithStreamingResponse:
        return TrainingSessionsResourceWithStreamingResponse(self._rl.training_sessions)


class AsyncRlResourceWithStreamingResponse:
    def __init__(self, rl: AsyncRlResource) -> None:
        self._rl = rl

    @cached_property
    def training_sessions(self) -> AsyncTrainingSessionsResourceWithStreamingResponse:
        return AsyncTrainingSessionsResourceWithStreamingResponse(self._rl.training_sessions)
