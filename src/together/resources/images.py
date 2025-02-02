# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal

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
from .._base_client import make_request_options
from ..types.image_file import ImageFile

__all__ = ["ImagesResource", "AsyncImagesResource"]


class ImagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ImagesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: Union[
            Literal[
                "black-forest-labs/FLUX.1-schnell-Free",
                "black-forest-labs/FLUX.1-schnell",
                "black-forest-labs/FLUX.1.1-pro",
            ],
            str,
        ],
        prompt: str,
        guidance: float | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        image_loras: Iterable[image_create_params.ImageLora] | NotGiven = NOT_GIVEN,
        image_url: str | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        negative_prompt: str | NotGiven = NOT_GIVEN,
        output_format: Literal["jpeg", "png"] | NotGiven = NOT_GIVEN,
        response_format: Literal["base64", "url"] | NotGiven = NOT_GIVEN,
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

              [See all of Together AI's image models](https://docs.together.ai/docs/serverless-models#image-models)

          prompt: A description of the desired images. Maximum length varies by model.

          guidance: Adjusts the alignment of the generated image with the input prompt. Higher
              values (e.g., 8-10) make the output more faithful to the prompt, while lower
              values (e.g., 1-5) encourage more creative freedom.

          height: Height of the image to generate in number of pixels.

          image_loras: An array of objects that define LoRAs (Low-Rank Adaptations) to influence the
              generated image.

          image_url: URL of an image to use for image models that support it.

          n: Number of image results to generate.

          negative_prompt: The prompt or prompts not to guide the image generation.

          output_format: The format of the image response. Can be either be `jpeg` or `png`. Defaults to
              `jpeg`.

          response_format: Format of the image response. Can be either a base64 string or a URL.

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
                    "guidance": guidance,
                    "height": height,
                    "image_loras": image_loras,
                    "image_url": image_url,
                    "n": n,
                    "negative_prompt": negative_prompt,
                    "output_format": output_format,
                    "response_format": response_format,
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
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncImagesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: Union[
            Literal[
                "black-forest-labs/FLUX.1-schnell-Free",
                "black-forest-labs/FLUX.1-schnell",
                "black-forest-labs/FLUX.1.1-pro",
            ],
            str,
        ],
        prompt: str,
        guidance: float | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        image_loras: Iterable[image_create_params.ImageLora] | NotGiven = NOT_GIVEN,
        image_url: str | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        negative_prompt: str | NotGiven = NOT_GIVEN,
        output_format: Literal["jpeg", "png"] | NotGiven = NOT_GIVEN,
        response_format: Literal["base64", "url"] | NotGiven = NOT_GIVEN,
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

              [See all of Together AI's image models](https://docs.together.ai/docs/serverless-models#image-models)

          prompt: A description of the desired images. Maximum length varies by model.

          guidance: Adjusts the alignment of the generated image with the input prompt. Higher
              values (e.g., 8-10) make the output more faithful to the prompt, while lower
              values (e.g., 1-5) encourage more creative freedom.

          height: Height of the image to generate in number of pixels.

          image_loras: An array of objects that define LoRAs (Low-Rank Adaptations) to influence the
              generated image.

          image_url: URL of an image to use for image models that support it.

          n: Number of image results to generate.

          negative_prompt: The prompt or prompts not to guide the image generation.

          output_format: The format of the image response. Can be either be `jpeg` or `png`. Defaults to
              `jpeg`.

          response_format: Format of the image response. Can be either a base64 string or a URL.

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
                    "guidance": guidance,
                    "height": height,
                    "image_loras": image_loras,
                    "image_url": image_url,
                    "n": n,
                    "negative_prompt": negative_prompt,
                    "output_format": output_format,
                    "response_format": response_format,
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
