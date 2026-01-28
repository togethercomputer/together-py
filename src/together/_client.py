# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

import httpx

from together.lib._google_colab import get_google_colab_secret

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import TogetherError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        beta,
        chat,
        audio,
        evals,
        files,
        images,
        models,
        rerank,
        videos,
        batches,
        hardware,
        endpoints,
        embeddings,
        completions,
        fine_tuning,
        code_interpreter,
    )
    from .resources.evals import EvalsResource, AsyncEvalsResource
    from .resources.files import FilesResource, AsyncFilesResource
    from .resources.images import ImagesResource, AsyncImagesResource
    from .resources.rerank import RerankResource, AsyncRerankResource
    from .resources.videos import VideosResource, AsyncVideosResource
    from .resources.batches import BatchesResource, AsyncBatchesResource
    from .resources.hardware import HardwareResource, AsyncHardwareResource
    from .resources.beta.beta import BetaResource, AsyncBetaResource
    from .resources.chat.chat import ChatResource, AsyncChatResource
    from .resources.endpoints import EndpointsResource, AsyncEndpointsResource
    from .resources.embeddings import EmbeddingsResource, AsyncEmbeddingsResource
    from .resources.audio.audio import AudioResource, AsyncAudioResource
    from .resources.completions import CompletionsResource, AsyncCompletionsResource
    from .resources.fine_tuning import FineTuningResource, AsyncFineTuningResource
    from .resources.models.models import ModelsResource, AsyncModelsResource
    from .resources.code_interpreter.code_interpreter import CodeInterpreterResource, AsyncCodeInterpreterResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Together",
    "AsyncTogether",
    "Client",
    "AsyncClient",
]


class Together(SyncAPIClient):
    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Together client instance.

        This automatically infers the `api_key` argument from the `TOGETHER_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("TOGETHER_API_KEY")
        if api_key is None and "google.colab" in sys.modules:
            api_key = get_google_colab_secret("TOGETHER_API_KEY")
        if api_key is None:
            raise TogetherError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TOGETHER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("TOGETHER_BASE_URL")
        self._base_url_overridden = base_url is not None
        if base_url is None:
            base_url = f"https://api.together.xyz/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = Stream

    @cached_property
    def beta(self) -> BetaResource:
        from .resources.beta import BetaResource

        return BetaResource(self)

    @cached_property
    def chat(self) -> ChatResource:
        from .resources.chat import ChatResource

        return ChatResource(self)

    @cached_property
    def completions(self) -> CompletionsResource:
        from .resources.completions import CompletionsResource

        return CompletionsResource(self)

    @cached_property
    def embeddings(self) -> EmbeddingsResource:
        from .resources.embeddings import EmbeddingsResource

        return EmbeddingsResource(self)

    @cached_property
    def files(self) -> FilesResource:
        from .resources.files import FilesResource

        return FilesResource(self)

    @cached_property
    def fine_tuning(self) -> FineTuningResource:
        from .resources.fine_tuning import FineTuningResource

        return FineTuningResource(self)

    @cached_property
    def code_interpreter(self) -> CodeInterpreterResource:
        from .resources.code_interpreter import CodeInterpreterResource

        return CodeInterpreterResource(self)

    @cached_property
    def images(self) -> ImagesResource:
        from .resources.images import ImagesResource

        return ImagesResource(self)

    @cached_property
    def videos(self) -> VideosResource:
        from .resources.videos import VideosResource

        return VideosResource(self)

    @cached_property
    def audio(self) -> AudioResource:
        from .resources.audio import AudioResource

        return AudioResource(self)

    @cached_property
    def models(self) -> ModelsResource:
        from .resources.models import ModelsResource

        return ModelsResource(self)

    @cached_property
    def endpoints(self) -> EndpointsResource:
        from .resources.endpoints import EndpointsResource

        return EndpointsResource(self)

    @cached_property
    def hardware(self) -> HardwareResource:
        from .resources.hardware import HardwareResource

        return HardwareResource(self)

    @cached_property
    def rerank(self) -> RerankResource:
        from .resources.rerank import RerankResource

        return RerankResource(self)

    @cached_property
    def batches(self) -> BatchesResource:
        from .resources.batches import BatchesResource

        return BatchesResource(self)

    @cached_property
    def evals(self) -> EvalsResource:
        from .resources.evals import EvalsResource

        return EvalsResource(self)

    @cached_property
    def with_raw_response(self) -> TogetherWithRawResponse:
        return TogetherWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TogetherWithStreamedResponse:
        return TogetherWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        client = self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )
        client._base_url_overridden = self._base_url_overridden or base_url is not None
        return client

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncTogether(AsyncAPIClient):
    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncTogether client instance.

        This automatically infers the `api_key` argument from the `TOGETHER_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("TOGETHER_API_KEY")
        if api_key is None and "google.colab" in sys.modules:
            api_key = get_google_colab_secret("TOGETHER_API_KEY")
        if api_key is None:
            raise TogetherError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TOGETHER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("TOGETHER_BASE_URL")
        self._base_url_overridden = base_url is not None
        if base_url is None:
            base_url = f"https://api.together.xyz/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = AsyncStream

    @cached_property
    def beta(self) -> AsyncBetaResource:
        from .resources.beta import AsyncBetaResource

        return AsyncBetaResource(self)

    @cached_property
    def chat(self) -> AsyncChatResource:
        from .resources.chat import AsyncChatResource

        return AsyncChatResource(self)

    @cached_property
    def completions(self) -> AsyncCompletionsResource:
        from .resources.completions import AsyncCompletionsResource

        return AsyncCompletionsResource(self)

    @cached_property
    def embeddings(self) -> AsyncEmbeddingsResource:
        from .resources.embeddings import AsyncEmbeddingsResource

        return AsyncEmbeddingsResource(self)

    @cached_property
    def files(self) -> AsyncFilesResource:
        from .resources.files import AsyncFilesResource

        return AsyncFilesResource(self)

    @cached_property
    def fine_tuning(self) -> AsyncFineTuningResource:
        from .resources.fine_tuning import AsyncFineTuningResource

        return AsyncFineTuningResource(self)

    @cached_property
    def code_interpreter(self) -> AsyncCodeInterpreterResource:
        from .resources.code_interpreter import AsyncCodeInterpreterResource

        return AsyncCodeInterpreterResource(self)

    @cached_property
    def images(self) -> AsyncImagesResource:
        from .resources.images import AsyncImagesResource

        return AsyncImagesResource(self)

    @cached_property
    def videos(self) -> AsyncVideosResource:
        from .resources.videos import AsyncVideosResource

        return AsyncVideosResource(self)

    @cached_property
    def audio(self) -> AsyncAudioResource:
        from .resources.audio import AsyncAudioResource

        return AsyncAudioResource(self)

    @cached_property
    def models(self) -> AsyncModelsResource:
        from .resources.models import AsyncModelsResource

        return AsyncModelsResource(self)

    @cached_property
    def endpoints(self) -> AsyncEndpointsResource:
        from .resources.endpoints import AsyncEndpointsResource

        return AsyncEndpointsResource(self)

    @cached_property
    def hardware(self) -> AsyncHardwareResource:
        from .resources.hardware import AsyncHardwareResource

        return AsyncHardwareResource(self)

    @cached_property
    def rerank(self) -> AsyncRerankResource:
        from .resources.rerank import AsyncRerankResource

        return AsyncRerankResource(self)

    @cached_property
    def batches(self) -> AsyncBatchesResource:
        from .resources.batches import AsyncBatchesResource

        return AsyncBatchesResource(self)

    @cached_property
    def evals(self) -> AsyncEvalsResource:
        from .resources.evals import AsyncEvalsResource

        return AsyncEvalsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncTogetherWithRawResponse:
        return AsyncTogetherWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTogetherWithStreamedResponse:
        return AsyncTogetherWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        client = self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )
        client._base_url_overridden = self._base_url_overridden or base_url is not None
        return client

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class TogetherWithRawResponse:
    _client: Together

    def __init__(self, client: Together) -> None:
        self._client = client

    @cached_property
    def beta(self) -> beta.BetaResourceWithRawResponse:
        from .resources.beta import BetaResourceWithRawResponse

        return BetaResourceWithRawResponse(self._client.beta)

    @cached_property
    def chat(self) -> chat.ChatResourceWithRawResponse:
        from .resources.chat import ChatResourceWithRawResponse

        return ChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithRawResponse:
        from .resources.completions import CompletionsResourceWithRawResponse

        return CompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsResourceWithRawResponse:
        from .resources.embeddings import EmbeddingsResourceWithRawResponse

        return EmbeddingsResourceWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesResourceWithRawResponse:
        from .resources.files import FilesResourceWithRawResponse

        return FilesResourceWithRawResponse(self._client.files)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningResourceWithRawResponse:
        from .resources.fine_tuning import FineTuningResourceWithRawResponse

        return FineTuningResourceWithRawResponse(self._client.fine_tuning)

    @cached_property
    def code_interpreter(self) -> code_interpreter.CodeInterpreterResourceWithRawResponse:
        from .resources.code_interpreter import CodeInterpreterResourceWithRawResponse

        return CodeInterpreterResourceWithRawResponse(self._client.code_interpreter)

    @cached_property
    def images(self) -> images.ImagesResourceWithRawResponse:
        from .resources.images import ImagesResourceWithRawResponse

        return ImagesResourceWithRawResponse(self._client.images)

    @cached_property
    def videos(self) -> videos.VideosResourceWithRawResponse:
        from .resources.videos import VideosResourceWithRawResponse

        return VideosResourceWithRawResponse(self._client.videos)

    @cached_property
    def audio(self) -> audio.AudioResourceWithRawResponse:
        from .resources.audio import AudioResourceWithRawResponse

        return AudioResourceWithRawResponse(self._client.audio)

    @cached_property
    def models(self) -> models.ModelsResourceWithRawResponse:
        from .resources.models import ModelsResourceWithRawResponse

        return ModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def endpoints(self) -> endpoints.EndpointsResourceWithRawResponse:
        from .resources.endpoints import EndpointsResourceWithRawResponse

        return EndpointsResourceWithRawResponse(self._client.endpoints)

    @cached_property
    def hardware(self) -> hardware.HardwareResourceWithRawResponse:
        from .resources.hardware import HardwareResourceWithRawResponse

        return HardwareResourceWithRawResponse(self._client.hardware)

    @cached_property
    def rerank(self) -> rerank.RerankResourceWithRawResponse:
        from .resources.rerank import RerankResourceWithRawResponse

        return RerankResourceWithRawResponse(self._client.rerank)

    @cached_property
    def batches(self) -> batches.BatchesResourceWithRawResponse:
        from .resources.batches import BatchesResourceWithRawResponse

        return BatchesResourceWithRawResponse(self._client.batches)

    @cached_property
    def evals(self) -> evals.EvalsResourceWithRawResponse:
        from .resources.evals import EvalsResourceWithRawResponse

        return EvalsResourceWithRawResponse(self._client.evals)


class AsyncTogetherWithRawResponse:
    _client: AsyncTogether

    def __init__(self, client: AsyncTogether) -> None:
        self._client = client

    @cached_property
    def beta(self) -> beta.AsyncBetaResourceWithRawResponse:
        from .resources.beta import AsyncBetaResourceWithRawResponse

        return AsyncBetaResourceWithRawResponse(self._client.beta)

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithRawResponse:
        from .resources.chat import AsyncChatResourceWithRawResponse

        return AsyncChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithRawResponse:
        from .resources.completions import AsyncCompletionsResourceWithRawResponse

        return AsyncCompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsResourceWithRawResponse:
        from .resources.embeddings import AsyncEmbeddingsResourceWithRawResponse

        return AsyncEmbeddingsResourceWithRawResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithRawResponse:
        from .resources.files import AsyncFilesResourceWithRawResponse

        return AsyncFilesResourceWithRawResponse(self._client.files)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningResourceWithRawResponse:
        from .resources.fine_tuning import AsyncFineTuningResourceWithRawResponse

        return AsyncFineTuningResourceWithRawResponse(self._client.fine_tuning)

    @cached_property
    def code_interpreter(self) -> code_interpreter.AsyncCodeInterpreterResourceWithRawResponse:
        from .resources.code_interpreter import AsyncCodeInterpreterResourceWithRawResponse

        return AsyncCodeInterpreterResourceWithRawResponse(self._client.code_interpreter)

    @cached_property
    def images(self) -> images.AsyncImagesResourceWithRawResponse:
        from .resources.images import AsyncImagesResourceWithRawResponse

        return AsyncImagesResourceWithRawResponse(self._client.images)

    @cached_property
    def videos(self) -> videos.AsyncVideosResourceWithRawResponse:
        from .resources.videos import AsyncVideosResourceWithRawResponse

        return AsyncVideosResourceWithRawResponse(self._client.videos)

    @cached_property
    def audio(self) -> audio.AsyncAudioResourceWithRawResponse:
        from .resources.audio import AsyncAudioResourceWithRawResponse

        return AsyncAudioResourceWithRawResponse(self._client.audio)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithRawResponse:
        from .resources.models import AsyncModelsResourceWithRawResponse

        return AsyncModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def endpoints(self) -> endpoints.AsyncEndpointsResourceWithRawResponse:
        from .resources.endpoints import AsyncEndpointsResourceWithRawResponse

        return AsyncEndpointsResourceWithRawResponse(self._client.endpoints)

    @cached_property
    def hardware(self) -> hardware.AsyncHardwareResourceWithRawResponse:
        from .resources.hardware import AsyncHardwareResourceWithRawResponse

        return AsyncHardwareResourceWithRawResponse(self._client.hardware)

    @cached_property
    def rerank(self) -> rerank.AsyncRerankResourceWithRawResponse:
        from .resources.rerank import AsyncRerankResourceWithRawResponse

        return AsyncRerankResourceWithRawResponse(self._client.rerank)

    @cached_property
    def batches(self) -> batches.AsyncBatchesResourceWithRawResponse:
        from .resources.batches import AsyncBatchesResourceWithRawResponse

        return AsyncBatchesResourceWithRawResponse(self._client.batches)

    @cached_property
    def evals(self) -> evals.AsyncEvalsResourceWithRawResponse:
        from .resources.evals import AsyncEvalsResourceWithRawResponse

        return AsyncEvalsResourceWithRawResponse(self._client.evals)


class TogetherWithStreamedResponse:
    _client: Together

    def __init__(self, client: Together) -> None:
        self._client = client

    @cached_property
    def beta(self) -> beta.BetaResourceWithStreamingResponse:
        from .resources.beta import BetaResourceWithStreamingResponse

        return BetaResourceWithStreamingResponse(self._client.beta)

    @cached_property
    def chat(self) -> chat.ChatResourceWithStreamingResponse:
        from .resources.chat import ChatResourceWithStreamingResponse

        return ChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithStreamingResponse:
        from .resources.completions import CompletionsResourceWithStreamingResponse

        return CompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsResourceWithStreamingResponse:
        from .resources.embeddings import EmbeddingsResourceWithStreamingResponse

        return EmbeddingsResourceWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.FilesResourceWithStreamingResponse:
        from .resources.files import FilesResourceWithStreamingResponse

        return FilesResourceWithStreamingResponse(self._client.files)

    @cached_property
    def fine_tuning(self) -> fine_tuning.FineTuningResourceWithStreamingResponse:
        from .resources.fine_tuning import FineTuningResourceWithStreamingResponse

        return FineTuningResourceWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def code_interpreter(self) -> code_interpreter.CodeInterpreterResourceWithStreamingResponse:
        from .resources.code_interpreter import CodeInterpreterResourceWithStreamingResponse

        return CodeInterpreterResourceWithStreamingResponse(self._client.code_interpreter)

    @cached_property
    def images(self) -> images.ImagesResourceWithStreamingResponse:
        from .resources.images import ImagesResourceWithStreamingResponse

        return ImagesResourceWithStreamingResponse(self._client.images)

    @cached_property
    def videos(self) -> videos.VideosResourceWithStreamingResponse:
        from .resources.videos import VideosResourceWithStreamingResponse

        return VideosResourceWithStreamingResponse(self._client.videos)

    @cached_property
    def audio(self) -> audio.AudioResourceWithStreamingResponse:
        from .resources.audio import AudioResourceWithStreamingResponse

        return AudioResourceWithStreamingResponse(self._client.audio)

    @cached_property
    def models(self) -> models.ModelsResourceWithStreamingResponse:
        from .resources.models import ModelsResourceWithStreamingResponse

        return ModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def endpoints(self) -> endpoints.EndpointsResourceWithStreamingResponse:
        from .resources.endpoints import EndpointsResourceWithStreamingResponse

        return EndpointsResourceWithStreamingResponse(self._client.endpoints)

    @cached_property
    def hardware(self) -> hardware.HardwareResourceWithStreamingResponse:
        from .resources.hardware import HardwareResourceWithStreamingResponse

        return HardwareResourceWithStreamingResponse(self._client.hardware)

    @cached_property
    def rerank(self) -> rerank.RerankResourceWithStreamingResponse:
        from .resources.rerank import RerankResourceWithStreamingResponse

        return RerankResourceWithStreamingResponse(self._client.rerank)

    @cached_property
    def batches(self) -> batches.BatchesResourceWithStreamingResponse:
        from .resources.batches import BatchesResourceWithStreamingResponse

        return BatchesResourceWithStreamingResponse(self._client.batches)

    @cached_property
    def evals(self) -> evals.EvalsResourceWithStreamingResponse:
        from .resources.evals import EvalsResourceWithStreamingResponse

        return EvalsResourceWithStreamingResponse(self._client.evals)


class AsyncTogetherWithStreamedResponse:
    _client: AsyncTogether

    def __init__(self, client: AsyncTogether) -> None:
        self._client = client

    @cached_property
    def beta(self) -> beta.AsyncBetaResourceWithStreamingResponse:
        from .resources.beta import AsyncBetaResourceWithStreamingResponse

        return AsyncBetaResourceWithStreamingResponse(self._client.beta)

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithStreamingResponse:
        from .resources.chat import AsyncChatResourceWithStreamingResponse

        return AsyncChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithStreamingResponse:
        from .resources.completions import AsyncCompletionsResourceWithStreamingResponse

        return AsyncCompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsResourceWithStreamingResponse:
        from .resources.embeddings import AsyncEmbeddingsResourceWithStreamingResponse

        return AsyncEmbeddingsResourceWithStreamingResponse(self._client.embeddings)

    @cached_property
    def files(self) -> files.AsyncFilesResourceWithStreamingResponse:
        from .resources.files import AsyncFilesResourceWithStreamingResponse

        return AsyncFilesResourceWithStreamingResponse(self._client.files)

    @cached_property
    def fine_tuning(self) -> fine_tuning.AsyncFineTuningResourceWithStreamingResponse:
        from .resources.fine_tuning import AsyncFineTuningResourceWithStreamingResponse

        return AsyncFineTuningResourceWithStreamingResponse(self._client.fine_tuning)

    @cached_property
    def code_interpreter(self) -> code_interpreter.AsyncCodeInterpreterResourceWithStreamingResponse:
        from .resources.code_interpreter import AsyncCodeInterpreterResourceWithStreamingResponse

        return AsyncCodeInterpreterResourceWithStreamingResponse(self._client.code_interpreter)

    @cached_property
    def images(self) -> images.AsyncImagesResourceWithStreamingResponse:
        from .resources.images import AsyncImagesResourceWithStreamingResponse

        return AsyncImagesResourceWithStreamingResponse(self._client.images)

    @cached_property
    def videos(self) -> videos.AsyncVideosResourceWithStreamingResponse:
        from .resources.videos import AsyncVideosResourceWithStreamingResponse

        return AsyncVideosResourceWithStreamingResponse(self._client.videos)

    @cached_property
    def audio(self) -> audio.AsyncAudioResourceWithStreamingResponse:
        from .resources.audio import AsyncAudioResourceWithStreamingResponse

        return AsyncAudioResourceWithStreamingResponse(self._client.audio)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithStreamingResponse:
        from .resources.models import AsyncModelsResourceWithStreamingResponse

        return AsyncModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def endpoints(self) -> endpoints.AsyncEndpointsResourceWithStreamingResponse:
        from .resources.endpoints import AsyncEndpointsResourceWithStreamingResponse

        return AsyncEndpointsResourceWithStreamingResponse(self._client.endpoints)

    @cached_property
    def hardware(self) -> hardware.AsyncHardwareResourceWithStreamingResponse:
        from .resources.hardware import AsyncHardwareResourceWithStreamingResponse

        return AsyncHardwareResourceWithStreamingResponse(self._client.hardware)

    @cached_property
    def rerank(self) -> rerank.AsyncRerankResourceWithStreamingResponse:
        from .resources.rerank import AsyncRerankResourceWithStreamingResponse

        return AsyncRerankResourceWithStreamingResponse(self._client.rerank)

    @cached_property
    def batches(self) -> batches.AsyncBatchesResourceWithStreamingResponse:
        from .resources.batches import AsyncBatchesResourceWithStreamingResponse

        return AsyncBatchesResourceWithStreamingResponse(self._client.batches)

    @cached_property
    def evals(self) -> evals.AsyncEvalsResourceWithStreamingResponse:
        from .resources.evals import AsyncEvalsResourceWithStreamingResponse

        return AsyncEvalsResourceWithStreamingResponse(self._client.evals)


Client = Together

AsyncClient = AsyncTogether
