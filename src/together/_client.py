# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, List, Union, Mapping, Iterable
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from .types import client_rerank_params
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    maybe_transform,
    get_async_library,
    async_maybe_transform,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import audio, files, images, models, fine_tune, embeddings, completions
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import TogetherError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .resources.chat import chat
from .types.rerank_response import RerankResponse
from .resources.code_interpreter import code_interpreter

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
    chat: chat.ChatResource
    completions: completions.CompletionsResource
    embeddings: embeddings.EmbeddingsResource
    files: files.FilesResource
    fine_tune: fine_tune.FineTuneResource
    code_interpreter: code_interpreter.CodeInterpreterResource
    images: images.ImagesResource
    audio: audio.AudioResource
    models: models.ModelsResource
    with_raw_response: TogetherWithRawResponse
    with_streaming_response: TogetherWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
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
        if api_key is None:
            raise TogetherError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TOGETHER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("TOGETHER_BASE_URL")
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

        self.chat = chat.ChatResource(self)
        self.completions = completions.CompletionsResource(self)
        self.embeddings = embeddings.EmbeddingsResource(self)
        self.files = files.FilesResource(self)
        self.fine_tune = fine_tune.FineTuneResource(self)
        self.code_interpreter = code_interpreter.CodeInterpreterResource(self)
        self.images = images.ImagesResource(self)
        self.audio = audio.AudioResource(self)
        self.models = models.ModelsResource(self)
        self.with_raw_response = TogetherWithRawResponse(self)
        self.with_streaming_response = TogetherWithStreamedResponse(self)

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
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
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
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def rerank(
        self,
        *,
        documents: Union[Iterable[Dict[str, object]], List[str]],
        model: Union[Literal["Salesforce/Llama-Rank-v1"], str],
        query: str,
        rank_fields: List[str] | NotGiven = NOT_GIVEN,
        return_documents: bool | NotGiven = NOT_GIVEN,
        top_n: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RerankResponse:
        """
        Query a reranker model

        Args:
          documents: List of documents, which can be either strings or objects.

          model: The model to be used for the rerank request.

              [See all of Together AI's rerank models](https://docs.together.ai/docs/serverless-models#rerank-models)

          query: The search query to be used for ranking.

          rank_fields: List of keys in the JSON Object document to rank by. Defaults to use all
              supplied keys for ranking.

          return_documents: Whether to return supplied documents with the response.

          top_n: The number of top results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/rerank",
            body=maybe_transform(
                {
                    "documents": documents,
                    "model": model,
                    "query": query,
                    "rank_fields": rank_fields,
                    "return_documents": return_documents,
                    "top_n": top_n,
                },
                client_rerank_params.ClientRerankParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankResponse,
        )

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
    chat: chat.AsyncChatResource
    completions: completions.AsyncCompletionsResource
    embeddings: embeddings.AsyncEmbeddingsResource
    files: files.AsyncFilesResource
    fine_tune: fine_tune.AsyncFineTuneResource
    code_interpreter: code_interpreter.AsyncCodeInterpreterResource
    images: images.AsyncImagesResource
    audio: audio.AsyncAudioResource
    models: models.AsyncModelsResource
    with_raw_response: AsyncTogetherWithRawResponse
    with_streaming_response: AsyncTogetherWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
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
        if api_key is None:
            raise TogetherError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TOGETHER_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("TOGETHER_BASE_URL")
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

        self.chat = chat.AsyncChatResource(self)
        self.completions = completions.AsyncCompletionsResource(self)
        self.embeddings = embeddings.AsyncEmbeddingsResource(self)
        self.files = files.AsyncFilesResource(self)
        self.fine_tune = fine_tune.AsyncFineTuneResource(self)
        self.code_interpreter = code_interpreter.AsyncCodeInterpreterResource(self)
        self.images = images.AsyncImagesResource(self)
        self.audio = audio.AsyncAudioResource(self)
        self.models = models.AsyncModelsResource(self)
        self.with_raw_response = AsyncTogetherWithRawResponse(self)
        self.with_streaming_response = AsyncTogetherWithStreamedResponse(self)

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
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
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
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def rerank(
        self,
        *,
        documents: Union[Iterable[Dict[str, object]], List[str]],
        model: Union[Literal["Salesforce/Llama-Rank-v1"], str],
        query: str,
        rank_fields: List[str] | NotGiven = NOT_GIVEN,
        return_documents: bool | NotGiven = NOT_GIVEN,
        top_n: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RerankResponse:
        """
        Query a reranker model

        Args:
          documents: List of documents, which can be either strings or objects.

          model: The model to be used for the rerank request.

              [See all of Together AI's rerank models](https://docs.together.ai/docs/serverless-models#rerank-models)

          query: The search query to be used for ranking.

          rank_fields: List of keys in the JSON Object document to rank by. Defaults to use all
              supplied keys for ranking.

          return_documents: Whether to return supplied documents with the response.

          top_n: The number of top results to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/rerank",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "model": model,
                    "query": query,
                    "rank_fields": rank_fields,
                    "return_documents": return_documents,
                    "top_n": top_n,
                },
                client_rerank_params.ClientRerankParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RerankResponse,
        )

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
    def __init__(self, client: Together) -> None:
        self.chat = chat.ChatResourceWithRawResponse(client.chat)
        self.completions = completions.CompletionsResourceWithRawResponse(client.completions)
        self.embeddings = embeddings.EmbeddingsResourceWithRawResponse(client.embeddings)
        self.files = files.FilesResourceWithRawResponse(client.files)
        self.fine_tune = fine_tune.FineTuneResourceWithRawResponse(client.fine_tune)
        self.code_interpreter = code_interpreter.CodeInterpreterResourceWithRawResponse(client.code_interpreter)
        self.images = images.ImagesResourceWithRawResponse(client.images)
        self.audio = audio.AudioResourceWithRawResponse(client.audio)
        self.models = models.ModelsResourceWithRawResponse(client.models)

        self.rerank = to_raw_response_wrapper(
            client.rerank,
        )


class AsyncTogetherWithRawResponse:
    def __init__(self, client: AsyncTogether) -> None:
        self.chat = chat.AsyncChatResourceWithRawResponse(client.chat)
        self.completions = completions.AsyncCompletionsResourceWithRawResponse(client.completions)
        self.embeddings = embeddings.AsyncEmbeddingsResourceWithRawResponse(client.embeddings)
        self.files = files.AsyncFilesResourceWithRawResponse(client.files)
        self.fine_tune = fine_tune.AsyncFineTuneResourceWithRawResponse(client.fine_tune)
        self.code_interpreter = code_interpreter.AsyncCodeInterpreterResourceWithRawResponse(client.code_interpreter)
        self.images = images.AsyncImagesResourceWithRawResponse(client.images)
        self.audio = audio.AsyncAudioResourceWithRawResponse(client.audio)
        self.models = models.AsyncModelsResourceWithRawResponse(client.models)

        self.rerank = async_to_raw_response_wrapper(
            client.rerank,
        )


class TogetherWithStreamedResponse:
    def __init__(self, client: Together) -> None:
        self.chat = chat.ChatResourceWithStreamingResponse(client.chat)
        self.completions = completions.CompletionsResourceWithStreamingResponse(client.completions)
        self.embeddings = embeddings.EmbeddingsResourceWithStreamingResponse(client.embeddings)
        self.files = files.FilesResourceWithStreamingResponse(client.files)
        self.fine_tune = fine_tune.FineTuneResourceWithStreamingResponse(client.fine_tune)
        self.code_interpreter = code_interpreter.CodeInterpreterResourceWithStreamingResponse(client.code_interpreter)
        self.images = images.ImagesResourceWithStreamingResponse(client.images)
        self.audio = audio.AudioResourceWithStreamingResponse(client.audio)
        self.models = models.ModelsResourceWithStreamingResponse(client.models)

        self.rerank = to_streamed_response_wrapper(
            client.rerank,
        )


class AsyncTogetherWithStreamedResponse:
    def __init__(self, client: AsyncTogether) -> None:
        self.chat = chat.AsyncChatResourceWithStreamingResponse(client.chat)
        self.completions = completions.AsyncCompletionsResourceWithStreamingResponse(client.completions)
        self.embeddings = embeddings.AsyncEmbeddingsResourceWithStreamingResponse(client.embeddings)
        self.files = files.AsyncFilesResourceWithStreamingResponse(client.files)
        self.fine_tune = fine_tune.AsyncFineTuneResourceWithStreamingResponse(client.fine_tune)
        self.code_interpreter = code_interpreter.AsyncCodeInterpreterResourceWithStreamingResponse(
            client.code_interpreter
        )
        self.images = images.AsyncImagesResourceWithStreamingResponse(client.images)
        self.audio = audio.AsyncAudioResourceWithStreamingResponse(client.audio)
        self.models = models.AsyncModelsResourceWithStreamingResponse(client.models)

        self.rerank = async_to_streamed_response_wrapper(
            client.rerank,
        )


Client = Together

AsyncClient = AsyncTogether
