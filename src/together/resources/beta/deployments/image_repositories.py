# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.deployments.image_repository_list_response import ImageRepositoryListResponse
from ....types.beta.deployments.image_repository_retrieve_images_response import ImageRepositoryRetrieveImagesResponse

__all__ = ["ImageRepositoriesResource", "AsyncImageRepositoriesResource"]


class ImageRepositoriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImageRepositoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ImageRepositoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImageRepositoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ImageRepositoriesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageRepositoryListResponse:
        """Retrieve all container image repositories available in your project"""
        return self._get(
            "/image-repositories",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageRepositoryListResponse,
        )

    def retrieve_images(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageRepositoryRetrieveImagesResponse:
        """
        Retrieve all container images (tags) available in a specific repository

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/image-repositories/{id}/images",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageRepositoryRetrieveImagesResponse,
        )


class AsyncImageRepositoriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImageRepositoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncImageRepositoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImageRepositoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncImageRepositoriesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageRepositoryListResponse:
        """Retrieve all container image repositories available in your project"""
        return await self._get(
            "/image-repositories",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageRepositoryListResponse,
        )

    async def retrieve_images(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ImageRepositoryRetrieveImagesResponse:
        """
        Retrieve all container images (tags) available in a specific repository

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/image-repositories/{id}/images",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageRepositoryRetrieveImagesResponse,
        )


class ImageRepositoriesResourceWithRawResponse:
    def __init__(self, image_repositories: ImageRepositoriesResource) -> None:
        self._image_repositories = image_repositories

        self.list = to_raw_response_wrapper(
            image_repositories.list,
        )
        self.retrieve_images = to_raw_response_wrapper(
            image_repositories.retrieve_images,
        )


class AsyncImageRepositoriesResourceWithRawResponse:
    def __init__(self, image_repositories: AsyncImageRepositoriesResource) -> None:
        self._image_repositories = image_repositories

        self.list = async_to_raw_response_wrapper(
            image_repositories.list,
        )
        self.retrieve_images = async_to_raw_response_wrapper(
            image_repositories.retrieve_images,
        )


class ImageRepositoriesResourceWithStreamingResponse:
    def __init__(self, image_repositories: ImageRepositoriesResource) -> None:
        self._image_repositories = image_repositories

        self.list = to_streamed_response_wrapper(
            image_repositories.list,
        )
        self.retrieve_images = to_streamed_response_wrapper(
            image_repositories.retrieve_images,
        )


class AsyncImageRepositoriesResourceWithStreamingResponse:
    def __init__(self, image_repositories: AsyncImageRepositoriesResource) -> None:
        self._image_repositories = image_repositories

        self.list = async_to_streamed_response_wrapper(
            image_repositories.list,
        )
        self.retrieve_images = async_to_streamed_response_wrapper(
            image_repositories.retrieve_images,
        )
