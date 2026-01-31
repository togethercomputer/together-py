# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.clusters import storage_create_params, storage_update_params
from ....types.beta.clusters.cluster_storage import ClusterStorage
from ....types.beta.clusters.storage_list_response import StorageListResponse
from ....types.beta.clusters.storage_delete_response import StorageDeleteResponse

__all__ = ["StorageResource", "AsyncStorageResource"]


class StorageResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return StorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return StorageResourceWithStreamingResponse(self)

    def create(
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
    ) -> ClusterStorage:
        """
        Instant Clusters supports long-lived, resizable in-DC shared storage with user
        data persistence. You can dynamically create and attach volumes to your cluster
        at cluster creation time, and resize as your data grows. All shared storage is
        backed by multi-NIC bare metal paths, ensuring high-throughput and low-latency
        performance for shared storage.

        Args:
          region: Region name. Usable regions can be found from `client.clusters.list_regions()`

          size_tib: Volume size in whole tebibytes (TiB).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/compute/clusters/storage/volumes",
            body=maybe_transform(
                {
                    "region": region,
                    "size_tib": size_tib,
                    "volume_name": volume_name,
                },
                storage_create_params.StorageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    def retrieve(
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
        Retrieve information about a specific shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return self._get(
            f"/compute/clusters/storage/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    def update(
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
        Update the configuration of an existing shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/compute/clusters/storage/volumes",
            body=maybe_transform(
                {
                    "size_tib": size_tib,
                    "volume_id": volume_id,
                },
                storage_update_params.StorageUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageListResponse:
        """List all shared volumes."""
        return self._get(
            "/compute/clusters/storage/volumes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageListResponse,
        )

    def delete(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteResponse:
        """Delete a shared volume.

        Note that if this volume is attached to a cluster,
        deleting will fail.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return self._delete(
            f"/compute/clusters/storage/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteResponse,
        )


class AsyncStorageResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncStorageResourceWithStreamingResponse(self)

    async def create(
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
    ) -> ClusterStorage:
        """
        Instant Clusters supports long-lived, resizable in-DC shared storage with user
        data persistence. You can dynamically create and attach volumes to your cluster
        at cluster creation time, and resize as your data grows. All shared storage is
        backed by multi-NIC bare metal paths, ensuring high-throughput and low-latency
        performance for shared storage.

        Args:
          region: Region name. Usable regions can be found from `client.clusters.list_regions()`

          size_tib: Volume size in whole tebibytes (TiB).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/compute/clusters/storage/volumes",
            body=await async_maybe_transform(
                {
                    "region": region,
                    "size_tib": size_tib,
                    "volume_name": volume_name,
                },
                storage_create_params.StorageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    async def retrieve(
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
        Retrieve information about a specific shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return await self._get(
            f"/compute/clusters/storage/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    async def update(
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
        Update the configuration of an existing shared volume.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/compute/clusters/storage/volumes",
            body=await async_maybe_transform(
                {
                    "size_tib": size_tib,
                    "volume_id": volume_id,
                },
                storage_update_params.StorageUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterStorage,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageListResponse:
        """List all shared volumes."""
        return await self._get(
            "/compute/clusters/storage/volumes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageListResponse,
        )

    async def delete(
        self,
        volume_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageDeleteResponse:
        """Delete a shared volume.

        Note that if this volume is attached to a cluster,
        deleting will fail.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not volume_id:
            raise ValueError(f"Expected a non-empty value for `volume_id` but received {volume_id!r}")
        return await self._delete(
            f"/compute/clusters/storage/volumes/{volume_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StorageDeleteResponse,
        )


class StorageResourceWithRawResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.create = to_raw_response_wrapper(
            storage.create,
        )
        self.retrieve = to_raw_response_wrapper(
            storage.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage.update,
        )
        self.list = to_raw_response_wrapper(
            storage.list,
        )
        self.delete = to_raw_response_wrapper(
            storage.delete,
        )


class AsyncStorageResourceWithRawResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.create = async_to_raw_response_wrapper(
            storage.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            storage.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage.update,
        )
        self.list = async_to_raw_response_wrapper(
            storage.list,
        )
        self.delete = async_to_raw_response_wrapper(
            storage.delete,
        )


class StorageResourceWithStreamingResponse:
    def __init__(self, storage: StorageResource) -> None:
        self._storage = storage

        self.create = to_streamed_response_wrapper(
            storage.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            storage.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage.update,
        )
        self.list = to_streamed_response_wrapper(
            storage.list,
        )
        self.delete = to_streamed_response_wrapper(
            storage.delete,
        )


class AsyncStorageResourceWithStreamingResponse:
    def __init__(self, storage: AsyncStorageResource) -> None:
        self._storage = storage

        self.create = async_to_streamed_response_wrapper(
            storage.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            storage.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage.update,
        )
        self.list = async_to_streamed_response_wrapper(
            storage.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage.delete,
        )
