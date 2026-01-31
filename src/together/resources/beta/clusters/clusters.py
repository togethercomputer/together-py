# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .storage import (
    StorageResource,
    AsyncStorageResource,
    StorageResourceWithRawResponse,
    AsyncStorageResourceWithRawResponse,
    StorageResourceWithStreamingResponse,
    AsyncStorageResourceWithStreamingResponse,
)
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
from ....types.beta import cluster_create_params, cluster_update_params
from ...._base_client import make_request_options
from ....types.beta.cluster import Cluster
from ....types.beta.cluster_list_response import ClusterListResponse
from ....types.beta.cluster_delete_response import ClusterDeleteResponse
from ....types.beta.cluster_list_regions_response import ClusterListRegionsResponse

__all__ = ["ClustersResource", "AsyncClustersResource"]


class ClustersResource(SyncAPIResource):
    @cached_property
    def storage(self) -> StorageResource:
        return StorageResource(self._client)

    @cached_property
    def with_raw_response(self) -> ClustersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ClustersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClustersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ClustersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        billing_type: Literal["RESERVED", "ON_DEMAND"],
        cluster_name: str,
        driver_version: Literal["CUDA_12_5_555", "CUDA_12_6_560", "CUDA_12_6_565", "CUDA_12_8_570"],
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        region: Literal["us-central-8", "us-central-4"],
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        duration_days: int | Omit = omit,
        shared_volume: cluster_create_params.SharedVolume | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """Create an Instant Cluster on Together's high-performance GPU clusters.

        With
        features like on-demand scaling, long-lived resizable high-bandwidth shared
        DC-local storage, Kubernetes and Slurm cluster flavors, a REST API, and
        Terraform support, you can run workloads flexibly without complex infrastructure
        management.

        Args:
          cluster_name: Name of the GPU cluster.

          driver_version: NVIDIA driver version to use in the cluster.

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          region: Region to create the GPU cluster in. Valid values are us-central-8 and
              us-central-4.

          duration_days: Duration in days to keep the cluster running.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/compute/clusters",
            body=maybe_transform(
                {
                    "billing_type": billing_type,
                    "cluster_name": cluster_name,
                    "driver_version": driver_version,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "region": region,
                    "cluster_type": cluster_type,
                    "duration_days": duration_days,
                    "shared_volume": shared_volume,
                    "volume_id": volume_id,
                },
                cluster_create_params.ClusterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    def retrieve(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """
        Retrieve information about a specific GPU cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._get(
            f"/compute/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    def update(
        self,
        cluster_id: str,
        *,
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        num_gpus: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """
        Update the configuration of an existing GPU cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._put(
            f"/compute/clusters/{cluster_id}",
            body=maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                },
                cluster_update_params.ClusterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
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
    ) -> ClusterListResponse:
        """List all GPU clusters."""
        return self._get(
            "/compute/clusters",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterListResponse,
        )

    def delete(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterDeleteResponse:
        """
        Delete a GPU cluster by cluster ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._delete(
            f"/compute/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterDeleteResponse,
        )

    def list_regions(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterListRegionsResponse:
        """List regions and corresponding supported driver versions"""
        return self._get(
            "/compute/regions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterListRegionsResponse,
        )


class AsyncClustersResource(AsyncAPIResource):
    @cached_property
    def storage(self) -> AsyncStorageResource:
        return AsyncStorageResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncClustersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncClustersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClustersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncClustersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        billing_type: Literal["RESERVED", "ON_DEMAND"],
        cluster_name: str,
        driver_version: Literal["CUDA_12_5_555", "CUDA_12_6_560", "CUDA_12_6_565", "CUDA_12_8_570"],
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        region: Literal["us-central-8", "us-central-4"],
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        duration_days: int | Omit = omit,
        shared_volume: cluster_create_params.SharedVolume | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """Create an Instant Cluster on Together's high-performance GPU clusters.

        With
        features like on-demand scaling, long-lived resizable high-bandwidth shared
        DC-local storage, Kubernetes and Slurm cluster flavors, a REST API, and
        Terraform support, you can run workloads flexibly without complex infrastructure
        management.

        Args:
          cluster_name: Name of the GPU cluster.

          driver_version: NVIDIA driver version to use in the cluster.

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          region: Region to create the GPU cluster in. Valid values are us-central-8 and
              us-central-4.

          duration_days: Duration in days to keep the cluster running.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/compute/clusters",
            body=await async_maybe_transform(
                {
                    "billing_type": billing_type,
                    "cluster_name": cluster_name,
                    "driver_version": driver_version,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "region": region,
                    "cluster_type": cluster_type,
                    "duration_days": duration_days,
                    "shared_volume": shared_volume,
                    "volume_id": volume_id,
                },
                cluster_create_params.ClusterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    async def retrieve(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """
        Retrieve information about a specific GPU cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._get(
            f"/compute/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    async def update(
        self,
        cluster_id: str,
        *,
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        num_gpus: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Cluster:
        """
        Update the configuration of an existing GPU cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._put(
            f"/compute/clusters/{cluster_id}",
            body=await async_maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                },
                cluster_update_params.ClusterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
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
    ) -> ClusterListResponse:
        """List all GPU clusters."""
        return await self._get(
            "/compute/clusters",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterListResponse,
        )

    async def delete(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterDeleteResponse:
        """
        Delete a GPU cluster by cluster ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._delete(
            f"/compute/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterDeleteResponse,
        )

    async def list_regions(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ClusterListRegionsResponse:
        """List regions and corresponding supported driver versions"""
        return await self._get(
            "/compute/regions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClusterListRegionsResponse,
        )


class ClustersResourceWithRawResponse:
    def __init__(self, clusters: ClustersResource) -> None:
        self._clusters = clusters

        self.create = to_raw_response_wrapper(
            clusters.create,
        )
        self.retrieve = to_raw_response_wrapper(
            clusters.retrieve,
        )
        self.update = to_raw_response_wrapper(
            clusters.update,
        )
        self.list = to_raw_response_wrapper(
            clusters.list,
        )
        self.delete = to_raw_response_wrapper(
            clusters.delete,
        )
        self.list_regions = to_raw_response_wrapper(
            clusters.list_regions,
        )

    @cached_property
    def storage(self) -> StorageResourceWithRawResponse:
        return StorageResourceWithRawResponse(self._clusters.storage)


class AsyncClustersResourceWithRawResponse:
    def __init__(self, clusters: AsyncClustersResource) -> None:
        self._clusters = clusters

        self.create = async_to_raw_response_wrapper(
            clusters.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            clusters.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            clusters.update,
        )
        self.list = async_to_raw_response_wrapper(
            clusters.list,
        )
        self.delete = async_to_raw_response_wrapper(
            clusters.delete,
        )
        self.list_regions = async_to_raw_response_wrapper(
            clusters.list_regions,
        )

    @cached_property
    def storage(self) -> AsyncStorageResourceWithRawResponse:
        return AsyncStorageResourceWithRawResponse(self._clusters.storage)


class ClustersResourceWithStreamingResponse:
    def __init__(self, clusters: ClustersResource) -> None:
        self._clusters = clusters

        self.create = to_streamed_response_wrapper(
            clusters.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            clusters.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            clusters.update,
        )
        self.list = to_streamed_response_wrapper(
            clusters.list,
        )
        self.delete = to_streamed_response_wrapper(
            clusters.delete,
        )
        self.list_regions = to_streamed_response_wrapper(
            clusters.list_regions,
        )

    @cached_property
    def storage(self) -> StorageResourceWithStreamingResponse:
        return StorageResourceWithStreamingResponse(self._clusters.storage)


class AsyncClustersResourceWithStreamingResponse:
    def __init__(self, clusters: AsyncClustersResource) -> None:
        self._clusters = clusters

        self.create = async_to_streamed_response_wrapper(
            clusters.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            clusters.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            clusters.update,
        )
        self.list = async_to_streamed_response_wrapper(
            clusters.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            clusters.delete,
        )
        self.list_regions = async_to_streamed_response_wrapper(
            clusters.list_regions,
        )

    @cached_property
    def storage(self) -> AsyncStorageResourceWithStreamingResponse:
        return AsyncStorageResourceWithStreamingResponse(self._clusters.storage)
