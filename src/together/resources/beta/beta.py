# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING

from .jig.jig import (
    JigResource,
    AsyncJigResource,
    JigResourceWithRawResponse,
    AsyncJigResourceWithRawResponse,
    JigResourceWithStreamingResponse,
    AsyncJigResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .models.models import (
    ModelsResource,
    AsyncModelsResource,
    ModelsResourceWithRawResponse,
    AsyncModelsResourceWithRawResponse,
    ModelsResourceWithStreamingResponse,
    AsyncModelsResourceWithStreamingResponse,
)
from .clusters.clusters import (
    ClustersResource,
    AsyncClustersResource,
    ClustersResourceWithRawResponse,
    AsyncClustersResourceWithRawResponse,
    ClustersResourceWithStreamingResponse,
    AsyncClustersResourceWithStreamingResponse,
)
from .endpoints.endpoints import (
    EndpointsResource,
    AsyncEndpointsResource,
    EndpointsResourceWithRawResponse,
    AsyncEndpointsResourceWithRawResponse,
    EndpointsResourceWithStreamingResponse,
    AsyncEndpointsResourceWithStreamingResponse,
)

if TYPE_CHECKING:
    from ..realtime import RealtimeResource, AsyncRealtimeResource

__all__ = ["BetaResource", "AsyncBetaResource"]


class BetaResource(SyncAPIResource):
    @cached_property
    def endpoints(self) -> EndpointsResource:
        return EndpointsResource(self._client)

    @cached_property
    def models(self) -> ModelsResource:
        return ModelsResource(self._client)

    @cached_property
    def jig(self) -> JigResource:
        return JigResource(self._client)

    # Handwritten (not generated): realtime transcription over WebSocket.
    # Guarded by tests/unit/test_realtime_wiring.py against regen drops.
    @cached_property
    def realtime(self) -> RealtimeResource:
        from ..realtime import RealtimeResource

        return RealtimeResource(self._client)

    @cached_property
    def clusters(self) -> ClustersResource:
        return ClustersResource(self._client)

    @cached_property
    def with_raw_response(self) -> BetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return BetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return BetaResourceWithStreamingResponse(self)


class AsyncBetaResource(AsyncAPIResource):
    @cached_property
    def endpoints(self) -> AsyncEndpointsResource:
        return AsyncEndpointsResource(self._client)

    @cached_property
    def models(self) -> AsyncModelsResource:
        return AsyncModelsResource(self._client)

    @cached_property
    def jig(self) -> AsyncJigResource:
        return AsyncJigResource(self._client)

    # Handwritten (not generated): realtime transcription over WebSocket.
    # Guarded by tests/unit/test_realtime_wiring.py against regen drops.
    @cached_property
    def realtime(self) -> AsyncRealtimeResource:
        from ..realtime import AsyncRealtimeResource

        return AsyncRealtimeResource(self._client)

    @cached_property
    def clusters(self) -> AsyncClustersResource:
        return AsyncClustersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncBetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncBetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncBetaResourceWithStreamingResponse(self)


class BetaResourceWithRawResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def endpoints(self) -> EndpointsResourceWithRawResponse:
        return EndpointsResourceWithRawResponse(self._beta.endpoints)

    @cached_property
    def models(self) -> ModelsResourceWithRawResponse:
        return ModelsResourceWithRawResponse(self._beta.models)

    @cached_property
    def jig(self) -> JigResourceWithRawResponse:
        return JigResourceWithRawResponse(self._beta.jig)

    @cached_property
    def clusters(self) -> ClustersResourceWithRawResponse:
        return ClustersResourceWithRawResponse(self._beta.clusters)


class AsyncBetaResourceWithRawResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def endpoints(self) -> AsyncEndpointsResourceWithRawResponse:
        return AsyncEndpointsResourceWithRawResponse(self._beta.endpoints)

    @cached_property
    def models(self) -> AsyncModelsResourceWithRawResponse:
        return AsyncModelsResourceWithRawResponse(self._beta.models)

    @cached_property
    def jig(self) -> AsyncJigResourceWithRawResponse:
        return AsyncJigResourceWithRawResponse(self._beta.jig)

    @cached_property
    def clusters(self) -> AsyncClustersResourceWithRawResponse:
        return AsyncClustersResourceWithRawResponse(self._beta.clusters)


class BetaResourceWithStreamingResponse:
    def __init__(self, beta: BetaResource) -> None:
        self._beta = beta

    @cached_property
    def endpoints(self) -> EndpointsResourceWithStreamingResponse:
        return EndpointsResourceWithStreamingResponse(self._beta.endpoints)

    @cached_property
    def models(self) -> ModelsResourceWithStreamingResponse:
        return ModelsResourceWithStreamingResponse(self._beta.models)

    @cached_property
    def jig(self) -> JigResourceWithStreamingResponse:
        return JigResourceWithStreamingResponse(self._beta.jig)

    @cached_property
    def clusters(self) -> ClustersResourceWithStreamingResponse:
        return ClustersResourceWithStreamingResponse(self._beta.clusters)


class AsyncBetaResourceWithStreamingResponse:
    def __init__(self, beta: AsyncBetaResource) -> None:
        self._beta = beta

    @cached_property
    def endpoints(self) -> AsyncEndpointsResourceWithStreamingResponse:
        return AsyncEndpointsResourceWithStreamingResponse(self._beta.endpoints)

    @cached_property
    def models(self) -> AsyncModelsResourceWithStreamingResponse:
        return AsyncModelsResourceWithStreamingResponse(self._beta.models)

    @cached_property
    def jig(self) -> AsyncJigResourceWithStreamingResponse:
        return AsyncJigResourceWithStreamingResponse(self._beta.jig)

    @cached_property
    def clusters(self) -> AsyncClustersResourceWithStreamingResponse:
        return AsyncClustersResourceWithStreamingResponse(self._beta.clusters)
