# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
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
from ...._utils import path_template, maybe_transform, async_maybe_transform
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
        billing_type: Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"],
        cluster_name: str,
        cuda_version: str,
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        nvidia_driver_version: str,
        region: str,
        auto_scale_max_gpus: int | Omit = omit,
        auto_scaled: bool | Omit = omit,
        capacity_pool_id: str | Omit = omit,
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        duration_days: int | Omit = omit,
        gpu_node_failover_enabled: bool | Omit = omit,
        install_traefik: bool | Omit = omit,
        reservation_end_time: Union[str, datetime] | Omit = omit,
        reservation_start_time: Union[str, datetime] | Omit = omit,
        shared_volume: cluster_create_params.SharedVolume | Omit = omit,
        slurm_image: str | Omit = omit,
        slurm_shm_size_gib: int | Omit = omit,
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
          billing_type: RESERVED billing types allow you to specify the duration of the cluster
              reservation via the duration_days field. ON_DEMAND billing types will give you
              ownership of the cluster until you delete it.

          cluster_name: Name of the GPU cluster.

          cuda_version: CUDA version for this cluster. For example, 12.5

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          nvidia_driver_version: Nvidia driver version for this cluster. For example, 550. Only some combination
              of cuda_version and nvidia_driver_version are supported.

          region: Region to create the GPU cluster in. Usable regions can be found from
              `client.clusters.list_regions()`

          auto_scale_max_gpus: Maximum number of GPUs to which the cluster can be auto-scaled up. This field is
              required if auto_scaled is true.

          auto_scaled: Whether GPU cluster should be auto-scaled based on the workload. By default, it
              is not auto-scaled.

          capacity_pool_id: ID of the capacity pool to use for the cluster. This field is optional and only
              applicable if the cluster is created from a capacity pool.

          cluster_type: Type of cluster to create.

          duration_days: Duration in days to keep the cluster running.

          gpu_node_failover_enabled: Whether automated GPU node failover should be enabled for this cluster. By
              default, it is disabled.

          install_traefik: Whether to install Traefik ingress controller in the cluster. This field is only
              applicable for Kubernetes clusters and is false by default.

          reservation_end_time: Reservation end time of the cluster. This field is required for SCHEDULED
              billing to specify the reservation end time for the cluster.

          reservation_start_time: Reservation start time of the cluster. This field is required for SCHEDULED
              billing to specify the reservation start time for the cluster. If not provided,
              the cluster will be provisioned immediately.

          shared_volume: Inline configuration to create a shared volume with the cluster creation.

          slurm_image: Custom Slurm image for Slurm clusters.

          slurm_shm_size_gib: Shared memory size in GiB for Slurm cluster. This field is required if
              cluster_type is SLURM.

          volume_id: ID of an existing volume to use with the cluster creation.

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
                    "cuda_version": cuda_version,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "nvidia_driver_version": nvidia_driver_version,
                    "region": region,
                    "auto_scale_max_gpus": auto_scale_max_gpus,
                    "auto_scaled": auto_scaled,
                    "capacity_pool_id": capacity_pool_id,
                    "cluster_type": cluster_type,
                    "duration_days": duration_days,
                    "gpu_node_failover_enabled": gpu_node_failover_enabled,
                    "install_traefik": install_traefik,
                    "reservation_end_time": reservation_end_time,
                    "reservation_start_time": reservation_start_time,
                    "shared_volume": shared_volume,
                    "slurm_image": slurm_image,
                    "slurm_shm_size_gib": slurm_shm_size_gib,
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
          cluster_id: The ID of the cluster to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._get(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
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
        reservation_end_time: Union[str, datetime] | Omit = omit,
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
          cluster_id: The ID of the cluster to update

          cluster_type: Type of cluster to update.

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          reservation_end_time: Timestamp at which the cluster should be decommissioned. Only accepted for
              prepaid clusters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._put(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
            body=maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                    "reservation_end_time": reservation_end_time,
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
          cluster_id: The ID of the cluster to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._delete(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
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
        billing_type: Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"],
        cluster_name: str,
        cuda_version: str,
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        nvidia_driver_version: str,
        region: str,
        auto_scale_max_gpus: int | Omit = omit,
        auto_scaled: bool | Omit = omit,
        capacity_pool_id: str | Omit = omit,
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        duration_days: int | Omit = omit,
        gpu_node_failover_enabled: bool | Omit = omit,
        install_traefik: bool | Omit = omit,
        reservation_end_time: Union[str, datetime] | Omit = omit,
        reservation_start_time: Union[str, datetime] | Omit = omit,
        shared_volume: cluster_create_params.SharedVolume | Omit = omit,
        slurm_image: str | Omit = omit,
        slurm_shm_size_gib: int | Omit = omit,
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
          billing_type: RESERVED billing types allow you to specify the duration of the cluster
              reservation via the duration_days field. ON_DEMAND billing types will give you
              ownership of the cluster until you delete it.

          cluster_name: Name of the GPU cluster.

          cuda_version: CUDA version for this cluster. For example, 12.5

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          nvidia_driver_version: Nvidia driver version for this cluster. For example, 550. Only some combination
              of cuda_version and nvidia_driver_version are supported.

          region: Region to create the GPU cluster in. Usable regions can be found from
              `client.clusters.list_regions()`

          auto_scale_max_gpus: Maximum number of GPUs to which the cluster can be auto-scaled up. This field is
              required if auto_scaled is true.

          auto_scaled: Whether GPU cluster should be auto-scaled based on the workload. By default, it
              is not auto-scaled.

          capacity_pool_id: ID of the capacity pool to use for the cluster. This field is optional and only
              applicable if the cluster is created from a capacity pool.

          cluster_type: Type of cluster to create.

          duration_days: Duration in days to keep the cluster running.

          gpu_node_failover_enabled: Whether automated GPU node failover should be enabled for this cluster. By
              default, it is disabled.

          install_traefik: Whether to install Traefik ingress controller in the cluster. This field is only
              applicable for Kubernetes clusters and is false by default.

          reservation_end_time: Reservation end time of the cluster. This field is required for SCHEDULED
              billing to specify the reservation end time for the cluster.

          reservation_start_time: Reservation start time of the cluster. This field is required for SCHEDULED
              billing to specify the reservation start time for the cluster. If not provided,
              the cluster will be provisioned immediately.

          shared_volume: Inline configuration to create a shared volume with the cluster creation.

          slurm_image: Custom Slurm image for Slurm clusters.

          slurm_shm_size_gib: Shared memory size in GiB for Slurm cluster. This field is required if
              cluster_type is SLURM.

          volume_id: ID of an existing volume to use with the cluster creation.

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
                    "cuda_version": cuda_version,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "nvidia_driver_version": nvidia_driver_version,
                    "region": region,
                    "auto_scale_max_gpus": auto_scale_max_gpus,
                    "auto_scaled": auto_scaled,
                    "capacity_pool_id": capacity_pool_id,
                    "cluster_type": cluster_type,
                    "duration_days": duration_days,
                    "gpu_node_failover_enabled": gpu_node_failover_enabled,
                    "install_traefik": install_traefik,
                    "reservation_end_time": reservation_end_time,
                    "reservation_start_time": reservation_start_time,
                    "shared_volume": shared_volume,
                    "slurm_image": slurm_image,
                    "slurm_shm_size_gib": slurm_shm_size_gib,
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
          cluster_id: The ID of the cluster to retrieve

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._get(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
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
        reservation_end_time: Union[str, datetime] | Omit = omit,
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
          cluster_id: The ID of the cluster to update

          cluster_type: Type of cluster to update.

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          reservation_end_time: Timestamp at which the cluster should be decommissioned. Only accepted for
              prepaid clusters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._put(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
            body=await async_maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                    "reservation_end_time": reservation_end_time,
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
          cluster_id: The ID of the cluster to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._delete(
            path_template("/compute/clusters/{cluster_id}", cluster_id=cluster_id),
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
