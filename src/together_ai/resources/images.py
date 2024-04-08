# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import ImageCreateResponse, image_create_params
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

__all__ = ["Images", "AsyncImages"]


class Images(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesWithRawResponse:
        return ImagesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesWithStreamingResponse:
        return ImagesWithStreamingResponse(self)

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
    ) -> ImageCreateResponse:
        """
        Generate images based on a given prompt using a specified model

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
            cast_to=ImageCreateResponse,
        )


class AsyncImages(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImagesWithRawResponse:
        return AsyncImagesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesWithStreamingResponse:
        return AsyncImagesWithStreamingResponse(self)

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
    ) -> ImageCreateResponse:
        """
        Generate images based on a given prompt using a specified model

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
            cast_to=ImageCreateResponse,
        )


class ImagesWithRawResponse:
    def __init__(self, images: Images) -> None:
        self._images = images

        self.create = to_raw_response_wrapper(
            images.create,
        )


class AsyncImagesWithRawResponse:
    def __init__(self, images: AsyncImages) -> None:
        self._images = images

        self.create = async_to_raw_response_wrapper(
            images.create,
        )


class ImagesWithStreamingResponse:
    def __init__(self, images: Images) -> None:
        self._images = images

        self.create = to_streamed_response_wrapper(
            images.create,
        )


class AsyncImagesWithStreamingResponse:
    def __init__(self, images: AsyncImages) -> None:
        self._images = images

        self.create = async_to_streamed_response_wrapper(
            images.create,
        )
