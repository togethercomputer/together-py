# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...types import model_list_params, model_upload_params
from .uploads import (
    UploadsResource,
    AsyncUploadsResource,
    UploadsResourceWithRawResponse,
    AsyncUploadsResourceWithRawResponse,
    UploadsResourceWithStreamingResponse,
    AsyncUploadsResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.model_list_response import ModelListResponse
from ...types.model_upload_response import ModelUploadResponse

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def uploads(self) -> UploadsResource:
        return UploadsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        dedicated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        Lists all of Together's open-source models

        Args:
          dedicated: Filter models to only return dedicated models

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"dedicated": dedicated}, model_list_params.ModelListParams),
            ),
            cast_to=ModelListResponse,
        )

    def upload(
        self,
        *,
        model_name: str,
        model_source: str,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        hf_token: str | Omit = omit,
        lora_model: str | Omit = omit,
        model_type: Literal["model", "adapter"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelUploadResponse:
        """
        Upload a custom model or adapter from Hugging Face or S3

        Args:
          model_name: The name to give to your uploaded model

          model_source: The source location of the model (Hugging Face repo or S3 path)

          base_model: The base model to use for an adapter if setting it to run against a serverless
              pool. Only used for model_type `adapter`.

          description: A description of your model

          hf_token: Hugging Face token (if uploading from Hugging Face)

          lora_model: The lora pool to use for an adapter if setting it to run against, say, a
              dedicated pool. Only used for model_type `adapter`.

          model_type: Whether the model is a full model or an adapter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/models",
            body=maybe_transform(
                {
                    "model_name": model_name,
                    "model_source": model_source,
                    "base_model": base_model,
                    "description": description,
                    "hf_token": hf_token,
                    "lora_model": lora_model,
                    "model_type": model_type,
                },
                model_upload_params.ModelUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelUploadResponse,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def uploads(self) -> AsyncUploadsResource:
        return AsyncUploadsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        dedicated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        Lists all of Together's open-source models

        Args:
          dedicated: Filter models to only return dedicated models

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"dedicated": dedicated}, model_list_params.ModelListParams),
            ),
            cast_to=ModelListResponse,
        )

    async def upload(
        self,
        *,
        model_name: str,
        model_source: str,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        hf_token: str | Omit = omit,
        lora_model: str | Omit = omit,
        model_type: Literal["model", "adapter"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelUploadResponse:
        """
        Upload a custom model or adapter from Hugging Face or S3

        Args:
          model_name: The name to give to your uploaded model

          model_source: The source location of the model (Hugging Face repo or S3 path)

          base_model: The base model to use for an adapter if setting it to run against a serverless
              pool. Only used for model_type `adapter`.

          description: A description of your model

          hf_token: Hugging Face token (if uploading from Hugging Face)

          lora_model: The lora pool to use for an adapter if setting it to run against, say, a
              dedicated pool. Only used for model_type `adapter`.

          model_type: Whether the model is a full model or an adapter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/models",
            body=await async_maybe_transform(
                {
                    "model_name": model_name,
                    "model_source": model_source,
                    "base_model": base_model,
                    "description": description,
                    "hf_token": hf_token,
                    "lora_model": lora_model,
                    "model_type": model_type,
                },
                model_upload_params.ModelUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelUploadResponse,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.upload = to_raw_response_wrapper(
            models.upload,
        )

    @cached_property
    def uploads(self) -> UploadsResourceWithRawResponse:
        return UploadsResourceWithRawResponse(self._models.uploads)


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.upload = async_to_raw_response_wrapper(
            models.upload,
        )

    @cached_property
    def uploads(self) -> AsyncUploadsResourceWithRawResponse:
        return AsyncUploadsResourceWithRawResponse(self._models.uploads)


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.upload = to_streamed_response_wrapper(
            models.upload,
        )

    @cached_property
    def uploads(self) -> UploadsResourceWithStreamingResponse:
        return UploadsResourceWithStreamingResponse(self._models.uploads)


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.upload = async_to_streamed_response_wrapper(
            models.upload,
        )

    @cached_property
    def uploads(self) -> AsyncUploadsResourceWithStreamingResponse:
        return AsyncUploadsResourceWithStreamingResponse(self._models.uploads)
