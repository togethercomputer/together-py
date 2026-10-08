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
from ..._compat import cached_property
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .checkpoints import (
    CheckpointsResource,
    AsyncCheckpointsResource,
    CheckpointsResourceWithRawResponse,
    AsyncCheckpointsResourceWithRawResponse,
    CheckpointsResourceWithStreamingResponse,
    AsyncCheckpointsResourceWithStreamingResponse,
)
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
from .prepare_for_fp4_inference import (
    PrepareForFp4InferenceResource,
    AsyncPrepareForFp4InferenceResource,
    PrepareForFp4InferenceResourceWithRawResponse,
    AsyncPrepareForFp4InferenceResourceWithRawResponse,
    PrepareForFp4InferenceResourceWithStreamingResponse,
    AsyncPrepareForFp4InferenceResourceWithStreamingResponse,
)

__all__ = ["PostTrainingResource", "AsyncPostTrainingResource"]


class PostTrainingResource(SyncAPIResource):
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
    def prepare_for_fp4_inference(self) -> PrepareForFp4InferenceResource:
        return PrepareForFp4InferenceResource(self._client)

    @cached_property
    def model_resources(self) -> ModelResourcesResource:
        return ModelResourcesResource(self._client)

    @cached_property
    def supported_models(self) -> SupportedModelsResource:
        return SupportedModelsResource(self._client)

    @cached_property
    def with_raw_response(self) -> PostTrainingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return PostTrainingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PostTrainingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return PostTrainingResourceWithStreamingResponse(self)


class AsyncPostTrainingResource(AsyncAPIResource):
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
    def prepare_for_fp4_inference(self) -> AsyncPrepareForFp4InferenceResource:
        return AsyncPrepareForFp4InferenceResource(self._client)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResource:
        return AsyncModelResourcesResource(self._client)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResource:
        return AsyncSupportedModelsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPostTrainingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncPostTrainingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPostTrainingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncPostTrainingResourceWithStreamingResponse(self)


class PostTrainingResourceWithRawResponse:
    def __init__(self, post_training: PostTrainingResource) -> None:
        self._post_training = post_training

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._post_training.sessions)

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._post_training.operations)

    @cached_property
    def checkpoints(self) -> CheckpointsResourceWithRawResponse:
        return CheckpointsResourceWithRawResponse(self._post_training.checkpoints)

    @cached_property
    def prepare_for_fp4_inference(self) -> PrepareForFp4InferenceResourceWithRawResponse:
        return PrepareForFp4InferenceResourceWithRawResponse(self._post_training.prepare_for_fp4_inference)

    @cached_property
    def model_resources(self) -> ModelResourcesResourceWithRawResponse:
        return ModelResourcesResourceWithRawResponse(self._post_training.model_resources)

    @cached_property
    def supported_models(self) -> SupportedModelsResourceWithRawResponse:
        return SupportedModelsResourceWithRawResponse(self._post_training.supported_models)


class AsyncPostTrainingResourceWithRawResponse:
    def __init__(self, post_training: AsyncPostTrainingResource) -> None:
        self._post_training = post_training

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._post_training.sessions)

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._post_training.operations)

    @cached_property
    def checkpoints(self) -> AsyncCheckpointsResourceWithRawResponse:
        return AsyncCheckpointsResourceWithRawResponse(self._post_training.checkpoints)

    @cached_property
    def prepare_for_fp4_inference(self) -> AsyncPrepareForFp4InferenceResourceWithRawResponse:
        return AsyncPrepareForFp4InferenceResourceWithRawResponse(self._post_training.prepare_for_fp4_inference)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResourceWithRawResponse:
        return AsyncModelResourcesResourceWithRawResponse(self._post_training.model_resources)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResourceWithRawResponse:
        return AsyncSupportedModelsResourceWithRawResponse(self._post_training.supported_models)


class PostTrainingResourceWithStreamingResponse:
    def __init__(self, post_training: PostTrainingResource) -> None:
        self._post_training = post_training

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._post_training.sessions)

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._post_training.operations)

    @cached_property
    def checkpoints(self) -> CheckpointsResourceWithStreamingResponse:
        return CheckpointsResourceWithStreamingResponse(self._post_training.checkpoints)

    @cached_property
    def prepare_for_fp4_inference(self) -> PrepareForFp4InferenceResourceWithStreamingResponse:
        return PrepareForFp4InferenceResourceWithStreamingResponse(self._post_training.prepare_for_fp4_inference)

    @cached_property
    def model_resources(self) -> ModelResourcesResourceWithStreamingResponse:
        return ModelResourcesResourceWithStreamingResponse(self._post_training.model_resources)

    @cached_property
    def supported_models(self) -> SupportedModelsResourceWithStreamingResponse:
        return SupportedModelsResourceWithStreamingResponse(self._post_training.supported_models)


class AsyncPostTrainingResourceWithStreamingResponse:
    def __init__(self, post_training: AsyncPostTrainingResource) -> None:
        self._post_training = post_training

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._post_training.sessions)

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._post_training.operations)

    @cached_property
    def checkpoints(self) -> AsyncCheckpointsResourceWithStreamingResponse:
        return AsyncCheckpointsResourceWithStreamingResponse(self._post_training.checkpoints)

    @cached_property
    def prepare_for_fp4_inference(self) -> AsyncPrepareForFp4InferenceResourceWithStreamingResponse:
        return AsyncPrepareForFp4InferenceResourceWithStreamingResponse(self._post_training.prepare_for_fp4_inference)

    @cached_property
    def model_resources(self) -> AsyncModelResourcesResourceWithStreamingResponse:
        return AsyncModelResourcesResourceWithStreamingResponse(self._post_training.model_resources)

    @cached_property
    def supported_models(self) -> AsyncSupportedModelsResourceWithStreamingResponse:
        return AsyncSupportedModelsResourceWithStreamingResponse(self._post_training.supported_models)
