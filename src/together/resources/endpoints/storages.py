# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ...types.endpoints import storage_create_shared_volume_params, storage_update_shared_volume_params
from ...types.beta.clusters.cluster_storage import ClusterStorage
from ...types.endpoints.storage_list_shared_volumes_response import StorageListSharedVolumesResponse
from ...types.endpoints.storage_create_shared_volume_response import StorageCreateSharedVolumeResponse
from ...types.endpoints.storage_delete_shared_volume_response import StorageDeleteSharedVolumeResponse

__all__ = ["StoragesResource", "AsyncStoragesResource"]


class StoragesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StoragesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return StoragesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StoragesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return StoragesResourceWithStreamingResponse(self)

    def create_shared_volume(
        self,
        *,
        region: str,
        size_tib: int,
        volume_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageCreateSharedVolumeResponse:
        """Create a shared volume.

        Args:
          region: Region name.

        Usable regions can be found from `client.clusters.list_regions()`

          size_tib: Volume size in whole tebibytes (TiB).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/clusters/storages",
            body=maybe_transform(
                {
                    "region": region,
                    "size_tib": size_tib,
                    "volume_name": volume_name,
                },
                storage_create_shared_volume_params.StorageCreateSharedVolumeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageCreateSharedVolumeResponse,
        )

    def delete_shared_volume(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteSharedVolumeResponse:
        """
        Delete shared volume by volume id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return self._delete(
            f"/clusters/storages/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteSharedVolumeResponse,
        )

    def list_shared_volumes(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageListSharedVolumesResponse:
        """List all shared volumes."""
        return self._get(
            "/clusters/storages",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageListSharedVolumesResponse,
        )

    def retrieve_shared_volume(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterStorage:
        """
        Get shared volume by volume Id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return self._get(
            f"/clusters/storages/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    def update_shared_volume(
        self,
        *,
        size_tib: int | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterStorage:
        """
        Update a shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/clusters/storages",
            body=maybe_transform(
                {
                    "size_tib": size_tib,
                    "volume_id": volume_id,
                },
                storage_update_shared_volume_params.StorageUpdateSharedVolumeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )


class AsyncStoragesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStoragesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncStoragesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStoragesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncStoragesResourceWithStreamingResponse(self)

    async def create_shared_volume(
        self,
        *,
        region: str,
        size_tib: int,
        volume_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageCreateSharedVolumeResponse:
        """Create a shared volume.

        Args:
          region: Region name.

        Usable regions can be found from `client.clusters.list_regions()`

          size_tib: Volume size in whole tebibytes (TiB).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/clusters/storages",
            body=await async_maybe_transform(
                {
                    "region": region,
                    "size_tib": size_tib,
                    "volume_name": volume_name,
                },
                storage_create_shared_volume_params.StorageCreateSharedVolumeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageCreateSharedVolumeResponse,
        )

    async def delete_shared_volume(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteSharedVolumeResponse:
        """
        Delete shared volume by volume id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return await self._delete(
            f"/clusters/storages/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteSharedVolumeResponse,
        )

    async def list_shared_volumes(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageListSharedVolumesResponse:
        """List all shared volumes."""
        return await self._get(
            "/clusters/storages",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageListSharedVolumesResponse,
        )

    async def retrieve_shared_volume(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterStorage:
        """
        Get shared volume by volume Id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return await self._get(
            f"/clusters/storages/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    async def update_shared_volume(
        self,
        *,
        size_tib: int | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterStorage:
        """
        Update a shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/clusters/storages",
            body=await async_maybe_transform(
                {
                    "size_tib": size_tib,
                    "volume_id": volume_id,
                },
                storage_update_shared_volume_params.StorageUpdateSharedVolumeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )


class StoragesResourceWithRawResponse:
    def __init__(self, storages: StoragesResource) -> None:
        self._storages = storages

        self.create_shared_volume = to_raw_response_wrapper(
            storages.create_shared_volume,
        )
        self.delete_shared_volume = to_raw_response_wrapper(
            storages.delete_shared_volume,
        )
        self.list_shared_volumes = to_raw_response_wrapper(
            storages.list_shared_volumes,
        )
        self.retrieve_shared_volume = to_raw_response_wrapper(
            storages.retrieve_shared_volume,
        )
        self.update_shared_volume = to_raw_response_wrapper(
            storages.update_shared_volume,
        )


class AsyncStoragesResourceWithRawResponse:
    def __init__(self, storages: AsyncStoragesResource) -> None:
        self._storages = storages

        self.create_shared_volume = async_to_raw_response_wrapper(
            storages.create_shared_volume,
        )
        self.delete_shared_volume = async_to_raw_response_wrapper(
            storages.delete_shared_volume,
        )
        self.list_shared_volumes = async_to_raw_response_wrapper(
            storages.list_shared_volumes,
        )
        self.retrieve_shared_volume = async_to_raw_response_wrapper(
            storages.retrieve_shared_volume,
        )
        self.update_shared_volume = async_to_raw_response_wrapper(
            storages.update_shared_volume,
        )


class StoragesResourceWithStreamingResponse:
    def __init__(self, storages: StoragesResource) -> None:
        self._storages = storages

        self.create_shared_volume = to_streamed_response_wrapper(
            storages.create_shared_volume,
        )
        self.delete_shared_volume = to_streamed_response_wrapper(
            storages.delete_shared_volume,
        )
        self.list_shared_volumes = to_streamed_response_wrapper(
            storages.list_shared_volumes,
        )
        self.retrieve_shared_volume = to_streamed_response_wrapper(
            storages.retrieve_shared_volume,
        )
        self.update_shared_volume = to_streamed_response_wrapper(
            storages.update_shared_volume,
        )


class AsyncStoragesResourceWithStreamingResponse:
    def __init__(self, storages: AsyncStoragesResource) -> None:
        self._storages = storages

        self.create_shared_volume = async_to_streamed_response_wrapper(
            storages.create_shared_volume,
        )
        self.delete_shared_volume = async_to_streamed_response_wrapper(
            storages.delete_shared_volume,
        )
        self.list_shared_volumes = async_to_streamed_response_wrapper(
            storages.list_shared_volumes,
        )
        self.retrieve_shared_volume = async_to_streamed_response_wrapper(
            storages.retrieve_shared_volume,
        )
        self.update_shared_volume = async_to_streamed_response_wrapper(
            storages.update_shared_volume,
        )
