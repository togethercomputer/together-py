# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..types import video_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.video_job import VideoJob

__all__ = ["VideosResource", "AsyncVideosResource"]


class VideosResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VideosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return VideosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VideosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return VideosResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        fps: int | Omit = omit,
        frame_images: Iterable[video_create_params.FrameImage] | Omit = omit,
        guidance_scale: int | Omit = omit,
        height: int | Omit = omit,
        negative_prompt: str | Omit = omit,
        output_format: Literal["MP4", "WEBM"] | Omit = omit,
        output_quality: int | Omit = omit,
        prompt: str | Omit = omit,
        reference_images: SequenceNotStr[str] | Omit = omit,
        seconds: str | Omit = omit,
        seed: int | Omit = omit,
        steps: int | Omit = omit,
        width: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoJob:
        """
        Create a video

        Args:
          model: The model to be used for the video creation request.

          fps: Frames per second. Defaults to 24.

          frame_images: Array of images to guide video generation, similar to keyframes.

          guidance_scale: Controls how closely the video generation follows your prompt. Higher values
              make the model adhere more strictly to your text description, while lower values
              allow more creative freedom. guidence_scale affects both visual content and
              temporal consistency.Recommended range is 6.0-10.0 for most video models. Values
              above 12 may cause over-guidance artifacts or unnatural motion patterns.

          negative_prompt: Similar to prompt, but specifies what to avoid instead of what to include

          output_format: Specifies the format of the output video. Defaults to MP4.

          output_quality: Compression quality. Defaults to 20.

          prompt: Text prompt that describes the video to generate.

          reference_images: Unlike frame_images which constrain specific timeline positions, reference
              images guide the general appearance that should appear consistently across the
              video.

          seconds: Clip duration in seconds.

          seed: Seed to use in initializing the video generation. Using the same seed allows
              deterministic video generation. If not provided a random seed is generated for
              each request.

          steps: The number of denoising steps the model performs during video generation. More
              steps typically result in higher quality output but require longer processing
              time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos" if self._client._base_url_overridden else "https://api.together.xyz/v2/videos",
            body=maybe_transform(
                {
                    "model": model,
                    "fps": fps,
                    "frame_images": frame_images,
                    "guidance_scale": guidance_scale,
                    "height": height,
                    "negative_prompt": negative_prompt,
                    "output_format": output_format,
                    "output_quality": output_quality,
                    "prompt": prompt,
                    "reference_images": reference_images,
                    "seconds": seconds,
                    "seed": seed,
                    "steps": steps,
                    "width": width,
                },
                video_create_params.VideoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoJob,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoJob:
        """
        Fetch video metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/videos/{id}" if self._client._base_url_overridden else f"https://api.together.xyz/v2/videos/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoJob,
        )


class AsyncVideosResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVideosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncVideosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVideosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncVideosResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        fps: int | Omit = omit,
        frame_images: Iterable[video_create_params.FrameImage] | Omit = omit,
        guidance_scale: int | Omit = omit,
        height: int | Omit = omit,
        negative_prompt: str | Omit = omit,
        output_format: Literal["MP4", "WEBM"] | Omit = omit,
        output_quality: int | Omit = omit,
        prompt: str | Omit = omit,
        reference_images: SequenceNotStr[str] | Omit = omit,
        seconds: str | Omit = omit,
        seed: int | Omit = omit,
        steps: int | Omit = omit,
        width: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoJob:
        """
        Create a video

        Args:
          model: The model to be used for the video creation request.

          fps: Frames per second. Defaults to 24.

          frame_images: Array of images to guide video generation, similar to keyframes.

          guidance_scale: Controls how closely the video generation follows your prompt. Higher values
              make the model adhere more strictly to your text description, while lower values
              allow more creative freedom. guidence_scale affects both visual content and
              temporal consistency.Recommended range is 6.0-10.0 for most video models. Values
              above 12 may cause over-guidance artifacts or unnatural motion patterns.

          negative_prompt: Similar to prompt, but specifies what to avoid instead of what to include

          output_format: Specifies the format of the output video. Defaults to MP4.

          output_quality: Compression quality. Defaults to 20.

          prompt: Text prompt that describes the video to generate.

          reference_images: Unlike frame_images which constrain specific timeline positions, reference
              images guide the general appearance that should appear consistently across the
              video.

          seconds: Clip duration in seconds.

          seed: Seed to use in initializing the video generation. Using the same seed allows
              deterministic video generation. If not provided a random seed is generated for
              each request.

          steps: The number of denoising steps the model performs during video generation. More
              steps typically result in higher quality output but require longer processing
              time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos" if self._client._base_url_overridden else "https://api.together.xyz/v2/videos",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "fps": fps,
                    "frame_images": frame_images,
                    "guidance_scale": guidance_scale,
                    "height": height,
                    "negative_prompt": negative_prompt,
                    "output_format": output_format,
                    "output_quality": output_quality,
                    "prompt": prompt,
                    "reference_images": reference_images,
                    "seconds": seconds,
                    "seed": seed,
                    "steps": steps,
                    "width": width,
                },
                video_create_params.VideoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoJob,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoJob:
        """
        Fetch video metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/videos/{id}" if self._client._base_url_overridden else f"https://api.together.xyz/v2/videos/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoJob,
        )


class VideosResourceWithRawResponse:
    def __init__(self, videos: VideosResource) -> None:
        self._videos = videos

        self.create = to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = to_raw_response_wrapper(
            videos.retrieve,
        )


class AsyncVideosResourceWithRawResponse:
    def __init__(self, videos: AsyncVideosResource) -> None:
        self._videos = videos

        self.create = async_to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            videos.retrieve,
        )


class VideosResourceWithStreamingResponse:
    def __init__(self, videos: VideosResource) -> None:
        self._videos = videos

        self.create = to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            videos.retrieve,
        )


class AsyncVideosResourceWithStreamingResponse:
    def __init__(self, videos: AsyncVideosResource) -> None:
        self._videos = videos

        self.create = async_to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            videos.retrieve,
        )
