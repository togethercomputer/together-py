# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from .checkpoints import (
    CheckpointsResource,
    AsyncCheckpointsResource,
    CheckpointsResourceWithRawResponse,
    AsyncCheckpointsResourceWithRawResponse,
    CheckpointsResourceWithStreamingResponse,
    AsyncCheckpointsResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from .model_resources import (
    ModelResourcesResource,
    AsyncModelResourcesResource,
    ModelResourcesResourceWithRawResponse,
    AsyncModelResourcesResourceWithRawResponse,
    ModelResourcesResourceWithStreamingResponse,
    AsyncModelResourcesResourceWithStreamingResponse,
)
from .supported_models import (
    SupportedModelsResource,
    AsyncSupportedModelsResource,
    SupportedModelsResourceWithRawResponse,
    AsyncSupportedModelsResourceWithRawResponse,
    SupportedModelsResourceWithStreamingResponse,
    AsyncSupportedModelsResourceWithStreamingResponse,
)

__all__ = ["RlResource", "AsyncRlResource"]


class RlResource(SyncAPIResource):
    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def checkpoints(self) -> CheckpointsResource:
        return CheckpointsResource(self._client)

    @cached_property
    def model_resources(self) -> ModelResourcesResource:
        return ModelResourcesResource(self._client)

    @cached_property
    def supported_models(self) -> SupportedModelsResource:
        return SupportedModelsResource(self._client)

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
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def checkpoints(self) -> AsyncCheckpointsResource:
        return AsyncCheckpointsResource(self._client)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResource:
        return AsyncModelResourcesResource(self._client)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResource:
        return AsyncSupportedModelsResource(self._client)

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
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._rl.sessions)

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._rl.operations)

    @cached_property
    def checkpoints(self) -> CheckpointsResourceWithRawResponse:
        return CheckpointsResourceWithRawResponse(self._rl.checkpoints)

    @cached_property
    def model_resources(self) -> ModelResourcesResourceWithRawResponse:
        return ModelResourcesResourceWithRawResponse(self._rl.model_resources)

    @cached_property
    def supported_models(self) -> SupportedModelsResourceWithRawResponse:
        return SupportedModelsResourceWithRawResponse(self._rl.supported_models)


class AsyncRlResourceWithRawResponse:
    def __init__(self, rl: AsyncRlResource) -> None:
        self._rl = rl

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._rl.sessions)

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._rl.operations)

    @cached_property
    def checkpoints(self) -> AsyncCheckpointsResourceWithRawResponse:
        return AsyncCheckpointsResourceWithRawResponse(self._rl.checkpoints)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResourceWithRawResponse:
        return AsyncModelResourcesResourceWithRawResponse(self._rl.model_resources)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResourceWithRawResponse:
        return AsyncSupportedModelsResourceWithRawResponse(self._rl.supported_models)


class RlResourceWithStreamingResponse:
    def __init__(self, rl: RlResource) -> None:
        self._rl = rl

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._rl.sessions)

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._rl.operations)

    @cached_property
    def checkpoints(self) -> CheckpointsResourceWithStreamingResponse:
        return CheckpointsResourceWithStreamingResponse(self._rl.checkpoints)

    @cached_property
    def model_resources(self) -> ModelResourcesResourceWithStreamingResponse:
        return ModelResourcesResourceWithStreamingResponse(self._rl.model_resources)

    @cached_property
    def supported_models(self) -> SupportedModelsResourceWithStreamingResponse:
        return SupportedModelsResourceWithStreamingResponse(self._rl.supported_models)


class AsyncRlResourceWithStreamingResponse:
    def __init__(self, rl: AsyncRlResource) -> None:
        self._rl = rl

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._rl.sessions)

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._rl.operations)

    @cached_property
    def checkpoints(self) -> AsyncCheckpointsResourceWithStreamingResponse:
        return AsyncCheckpointsResourceWithStreamingResponse(self._rl.checkpoints)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResourceWithStreamingResponse:
        return AsyncModelResourcesResourceWithStreamingResponse(self._rl.model_resources)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResourceWithStreamingResponse:
        return AsyncSupportedModelsResourceWithStreamingResponse(self._rl.supported_models)
