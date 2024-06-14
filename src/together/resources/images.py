# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import image_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
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
from ..types.image_file import ImageFile

__all__ = ["ImagesResource", "AsyncImagesResource"]


class ImagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesResourceWithRawResponse:
        return ImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesResourceWithStreamingResponse:
        return ImagesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        prompt: str,
        height: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        negative_prompt: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        steps: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageFile:
        """
        Use an image model to generate an image for a given prompt.

        Args:
          model: The model to use for image generation.

          prompt: A description of the desired images. Maximum length varies by model.

          height: Height of the image to generate in number of pixels.

          n: Number of image results to generate.

          negative_prompt: The prompt or prompts not to guide the image generation.

          seed: Seed used for generation. Can be used to reproduce image generations.

          steps: Number of generation steps.

          width: Width of the image to generate in number of pixels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/images/generations",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "height": height,
                    "n": n,
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "steps": steps,
                    "width": width,
                },
                image_create_params.ImageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageFile,
        )


class AsyncImagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImagesResourceWithRawResponse:
        return AsyncImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesResourceWithStreamingResponse:
        return AsyncImagesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        prompt: str,
        height: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        negative_prompt: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        steps: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageFile:
        """
        Use an image model to generate an image for a given prompt.

        Args:
          model: The model to use for image generation.

          prompt: A description of the desired images. Maximum length varies by model.

          height: Height of the image to generate in number of pixels.

          n: Number of image results to generate.

          negative_prompt: The prompt or prompts not to guide the image generation.

          seed: Seed used for generation. Can be used to reproduce image generations.

          steps: Number of generation steps.

          width: Width of the image to generate in number of pixels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/images/generations",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "height": height,
                    "n": n,
                    "negative_prompt": negative_prompt,
                    "seed": seed,
                    "steps": steps,
                    "width": width,
                },
                image_create_params.ImageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageFile,
        )


class ImagesResourceWithRawResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.create = to_raw_response_wrapper(
            images.create,
        )


class AsyncImagesResourceWithRawResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.create = async_to_raw_response_wrapper(
            images.create,
        )


class ImagesResourceWithStreamingResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.create = to_streamed_response_wrapper(
            images.create,
        )


class AsyncImagesResourceWithStreamingResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.create = async_to_streamed_response_wrapper(
            images.create,
        )
