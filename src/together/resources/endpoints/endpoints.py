# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ...types import (
    endpoint_list_params,
    endpoint_create_params,
    endpoint_update_params,
    endpoint_create_cluster_params,
    endpoint_update_cluster_params,
)
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from .storages import (
    StoragesResource,
    AsyncStoragesResource,
    StoragesResourceWithRawResponse,
    AsyncStoragesResourceWithRawResponse,
    StoragesResourceWithStreamingResponse,
    AsyncStoragesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.beta.cluster import Cluster
from ...types.autoscaling_param import AutoscalingParam
from ...types.dedicated_endpoint import DedicatedEndpoint
from ...types.endpoint_list_response import EndpointListResponse
from ...types.endpoint_list_avzones_response import EndpointListAvzonesResponse
from ...types.endpoint_list_regions_response import EndpointListRegionsResponse
from ...types.endpoint_list_clusters_response import EndpointListClustersResponse
from ...types.endpoint_create_cluster_response import EndpointCreateClusterResponse
from ...types.endpoint_delete_cluster_response import EndpointDeleteClusterResponse
from ...types.endpoint_update_cluster_response import EndpointUpdateClusterResponse

__all__ = ["EndpointsResource", "AsyncEndpointsResource"]


class EndpointsResource(SyncAPIResource):
    @cached_property
    def storages(self) -> StoragesResource:
        return StoragesResource(self._client)

    @cached_property
    def with_raw_response(self) -> EndpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return EndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EndpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return EndpointsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        autoscaling: AutoscalingParam,
        hardware: str,
        model: str,
        availability_zone: str | Omit = omit,
        disable_prompt_cache: bool | Omit = omit,
        disable_speculative_decoding: bool | Omit = omit,
        display_name: str | Omit = omit,
        inactive_timeout: Optional[int] | Omit = omit,
        state: Literal["STARTED", "STOPPED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """Creates a new dedicated endpoint for serving models.

        The endpoint will
        automatically start after creation. You can deploy any supported model on
        hardware configurations that meet the model's requirements.

        Args:
          autoscaling: Configuration for automatic scaling of the endpoint

          hardware: The hardware configuration to use for this endpoint

          model: The model to deploy on this endpoint

          availability_zone: Create the endpoint in a specified availability zone (e.g., us-central-4b)

          disable_prompt_cache: Whether to disable the prompt cache for this endpoint

          disable_speculative_decoding: Whether to disable speculative decoding for this endpoint

          display_name: A human-readable name for the endpoint

          inactive_timeout: The number of minutes of inactivity after which the endpoint will be
              automatically stopped. Set to null, omit or set to 0 to disable automatic
              timeout.

          state: The desired state of the endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/endpoints",
            body=maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "hardware": hardware,
                    "model": model,
                    "availability_zone": availability_zone,
                    "disable_prompt_cache": disable_prompt_cache,
                    "disable_speculative_decoding": disable_speculative_decoding,
                    "display_name": display_name,
                    "inactive_timeout": inactive_timeout,
                    "state": state,
                },
                endpoint_create_params.EndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    def retrieve(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """
        Retrieves details about a specific endpoint, including its current state,
        configuration, and scaling settings.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._get(
            f"/endpoints/{endpoint_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    def update(
        self,
        endpoint_id: str,
        *,
        autoscaling: AutoscalingParam | Omit = omit,
        display_name: str | Omit = omit,
        inactive_timeout: Optional[int] | Omit = omit,
        state: Literal["STARTED", "STOPPED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """Updates an existing endpoint's configuration.

        You can modify the display name,
        autoscaling settings, or change the endpoint's state (start/stop).

        Args:
          autoscaling: New autoscaling configuration for the endpoint

          display_name: A human-readable name for the endpoint

          inactive_timeout: The number of minutes of inactivity after which the endpoint will be
              automatically stopped. Set to 0 to disable automatic timeout.

          state: The desired state of the endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._patch(
            f"/endpoints/{endpoint_id}",
            body=maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "display_name": display_name,
                    "inactive_timeout": inactive_timeout,
                    "state": state,
                },
                endpoint_update_params.EndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    def list(
        self,
        *,
        mine: bool | Omit = omit,
        type: Literal["dedicated", "serverless"] | Omit = omit,
        usage_type: Literal["on-demand", "reserved"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListResponse:
        """Returns a list of all endpoints associated with your account.

        You can filter the
        results by type (dedicated or serverless).

        Args:
          mine: If true, return only endpoints owned by the caller

          type: Filter endpoints by type

          usage_type: Filter endpoints by usage type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/endpoints",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "mine": mine,
                        "type": type,
                        "usage_type": usage_type,
                    },
                    endpoint_list_params.EndpointListParams,
                ),
            ),
            cast_to=EndpointListResponse,
        )

    def delete(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Permanently deletes an endpoint.

        This action cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/endpoints/{endpoint_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_cluster(
        self,
        *,
        billing_type: Literal["RESERVED", "ON_DEMAND"],
        cluster_name: str,
        driver_version: Literal["CUDA_12_5_555", "CUDA_12_6_560", "CUDA_12_6_565", "CUDA_12_8_570"],
        duration_days: int,
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        region: Literal["us-central-8", "us-central-4"],
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        shared_volume: endpoint_create_cluster_params.SharedVolume | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointCreateClusterResponse:
        """
        Create GPU Cluster

        Args:
          cluster_name: Name of the GPU cluster.

          driver_version: NVIDIA driver version to use in the cluster.

          duration_days: Duration in days to keep the cluster running.

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          region: Region to create the GPU cluster in. Valid values are us-central-8 and
              us-central-4.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/clusters",
            body=maybe_transform(
                {
                    "billing_type": billing_type,
                    "cluster_name": cluster_name,
                    "driver_version": driver_version,
                    "duration_days": duration_days,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "region": region,
                    "cluster_type": cluster_type,
                    "shared_volume": shared_volume,
                    "volume_id": volume_id,
                },
                endpoint_create_cluster_params.EndpointCreateClusterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointCreateClusterResponse,
        )

    def delete_cluster(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeleteClusterResponse:
        """
        Delete GPU cluster by cluster ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._delete(
            f"/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointDeleteClusterResponse,
        )

    def list_avzones(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListAvzonesResponse:
        """List all available availability zones."""
        return self._get(
            "/clusters/availability-zones",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListAvzonesResponse,
        )

    def list_clusters(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListClustersResponse:
        """List all GPU clusters."""
        return self._get(
            "/clusters",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListClustersResponse,
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
    ) -> EndpointListRegionsResponse:
        """List regions and corresponding supported driver versions"""
        return self._get(
            "/clusters/regions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListRegionsResponse,
        )

    def retrieve_cluster(
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
        Get GPU cluster by cluster ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._get(
            f"/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    def update_cluster(
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
    ) -> EndpointUpdateClusterResponse:
        """
        Update a GPU Cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return self._put(
            f"/clusters/{cluster_id}",
            body=maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                },
                endpoint_update_cluster_params.EndpointUpdateClusterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointUpdateClusterResponse,
        )


class AsyncEndpointsResource(AsyncAPIResource):
    @cached_property
    def storages(self) -> AsyncStoragesResource:
        return AsyncStoragesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEndpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncEndpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEndpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncEndpointsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        autoscaling: AutoscalingParam,
        hardware: str,
        model: str,
        availability_zone: str | Omit = omit,
        disable_prompt_cache: bool | Omit = omit,
        disable_speculative_decoding: bool | Omit = omit,
        display_name: str | Omit = omit,
        inactive_timeout: Optional[int] | Omit = omit,
        state: Literal["STARTED", "STOPPED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """Creates a new dedicated endpoint for serving models.

        The endpoint will
        automatically start after creation. You can deploy any supported model on
        hardware configurations that meet the model's requirements.

        Args:
          autoscaling: Configuration for automatic scaling of the endpoint

          hardware: The hardware configuration to use for this endpoint

          model: The model to deploy on this endpoint

          availability_zone: Create the endpoint in a specified availability zone (e.g., us-central-4b)

          disable_prompt_cache: Whether to disable the prompt cache for this endpoint

          disable_speculative_decoding: Whether to disable speculative decoding for this endpoint

          display_name: A human-readable name for the endpoint

          inactive_timeout: The number of minutes of inactivity after which the endpoint will be
              automatically stopped. Set to null, omit or set to 0 to disable automatic
              timeout.

          state: The desired state of the endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/endpoints",
            body=await async_maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "hardware": hardware,
                    "model": model,
                    "availability_zone": availability_zone,
                    "disable_prompt_cache": disable_prompt_cache,
                    "disable_speculative_decoding": disable_speculative_decoding,
                    "display_name": display_name,
                    "inactive_timeout": inactive_timeout,
                    "state": state,
                },
                endpoint_create_params.EndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    async def retrieve(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """
        Retrieves details about a specific endpoint, including its current state,
        configuration, and scaling settings.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._get(
            f"/endpoints/{endpoint_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    async def update(
        self,
        endpoint_id: str,
        *,
        autoscaling: AutoscalingParam | Omit = omit,
        display_name: str | Omit = omit,
        inactive_timeout: Optional[int] | Omit = omit,
        state: Literal["STARTED", "STOPPED"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DedicatedEndpoint:
        """Updates an existing endpoint's configuration.

        You can modify the display name,
        autoscaling settings, or change the endpoint's state (start/stop).

        Args:
          autoscaling: New autoscaling configuration for the endpoint

          display_name: A human-readable name for the endpoint

          inactive_timeout: The number of minutes of inactivity after which the endpoint will be
              automatically stopped. Set to 0 to disable automatic timeout.

          state: The desired state of the endpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._patch(
            f"/endpoints/{endpoint_id}",
            body=await async_maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "display_name": display_name,
                    "inactive_timeout": inactive_timeout,
                    "state": state,
                },
                endpoint_update_params.EndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DedicatedEndpoint,
        )

    async def list(
        self,
        *,
        mine: bool | Omit = omit,
        type: Literal["dedicated", "serverless"] | Omit = omit,
        usage_type: Literal["on-demand", "reserved"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListResponse:
        """Returns a list of all endpoints associated with your account.

        You can filter the
        results by type (dedicated or serverless).

        Args:
          mine: If true, return only endpoints owned by the caller

          type: Filter endpoints by type

          usage_type: Filter endpoints by usage type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/endpoints",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "mine": mine,
                        "type": type,
                        "usage_type": usage_type,
                    },
                    endpoint_list_params.EndpointListParams,
                ),
            ),
            cast_to=EndpointListResponse,
        )

    async def delete(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Permanently deletes an endpoint.

        This action cannot be undone.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/endpoints/{endpoint_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_cluster(
        self,
        *,
        billing_type: Literal["RESERVED", "ON_DEMAND"],
        cluster_name: str,
        driver_version: Literal["CUDA_12_5_555", "CUDA_12_6_560", "CUDA_12_6_565", "CUDA_12_8_570"],
        duration_days: int,
        gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"],
        num_gpus: int,
        region: Literal["us-central-8", "us-central-4"],
        cluster_type: Literal["KUBERNETES", "SLURM"] | Omit = omit,
        shared_volume: endpoint_create_cluster_params.SharedVolume | Omit = omit,
        volume_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointCreateClusterResponse:
        """
        Create GPU Cluster

        Args:
          cluster_name: Name of the GPU cluster.

          driver_version: NVIDIA driver version to use in the cluster.

          duration_days: Duration in days to keep the cluster running.

          gpu_type: Type of GPU to use in the cluster

          num_gpus: Number of GPUs to allocate in the cluster. This must be multiple of 8. For
              example, 8, 16 or 24

          region: Region to create the GPU cluster in. Valid values are us-central-8 and
              us-central-4.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/clusters",
            body=await async_maybe_transform(
                {
                    "billing_type": billing_type,
                    "cluster_name": cluster_name,
                    "driver_version": driver_version,
                    "duration_days": duration_days,
                    "gpu_type": gpu_type,
                    "num_gpus": num_gpus,
                    "region": region,
                    "cluster_type": cluster_type,
                    "shared_volume": shared_volume,
                    "volume_id": volume_id,
                },
                endpoint_create_cluster_params.EndpointCreateClusterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointCreateClusterResponse,
        )

    async def delete_cluster(
        self,
        cluster_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeleteClusterResponse:
        """
        Delete GPU cluster by cluster ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._delete(
            f"/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointDeleteClusterResponse,
        )

    async def list_avzones(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListAvzonesResponse:
        """List all available availability zones."""
        return await self._get(
            "/clusters/availability-zones",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListAvzonesResponse,
        )

    async def list_clusters(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointListClustersResponse:
        """List all GPU clusters."""
        return await self._get(
            "/clusters",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListClustersResponse,
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
    ) -> EndpointListRegionsResponse:
        """List regions and corresponding supported driver versions"""
        return await self._get(
            "/clusters/regions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointListRegionsResponse,
        )

    async def retrieve_cluster(
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
        Get GPU cluster by cluster ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._get(
            f"/clusters/{cluster_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Cluster,
        )

    async def update_cluster(
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
    ) -> EndpointUpdateClusterResponse:
        """
        Update a GPU Cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        return await self._put(
            f"/clusters/{cluster_id}",
            body=await async_maybe_transform(
                {
                    "cluster_type": cluster_type,
                    "num_gpus": num_gpus,
                },
                endpoint_update_cluster_params.EndpointUpdateClusterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointUpdateClusterResponse,
        )


class EndpointsResourceWithRawResponse:
    def __init__(self, endpoints: EndpointsResource) -> None:
        self._endpoints = endpoints

        self.create = to_raw_response_wrapper(
            endpoints.create,
        )
        self.retrieve = to_raw_response_wrapper(
            endpoints.retrieve,
        )
        self.update = to_raw_response_wrapper(
            endpoints.update,
        )
        self.list = to_raw_response_wrapper(
            endpoints.list,
        )
        self.delete = to_raw_response_wrapper(
            endpoints.delete,
        )
        self.create_cluster = to_raw_response_wrapper(
            endpoints.create_cluster,
        )
        self.delete_cluster = to_raw_response_wrapper(
            endpoints.delete_cluster,
        )
        self.list_avzones = to_raw_response_wrapper(
            endpoints.list_avzones,
        )
        self.list_clusters = to_raw_response_wrapper(
            endpoints.list_clusters,
        )
        self.list_regions = to_raw_response_wrapper(
            endpoints.list_regions,
        )
        self.retrieve_cluster = to_raw_response_wrapper(
            endpoints.retrieve_cluster,
        )
        self.update_cluster = to_raw_response_wrapper(
            endpoints.update_cluster,
        )

    @cached_property
    def storages(self) -> StoragesResourceWithRawResponse:
        return StoragesResourceWithRawResponse(self._endpoints.storages)


class AsyncEndpointsResourceWithRawResponse:
    def __init__(self, endpoints: AsyncEndpointsResource) -> None:
        self._endpoints = endpoints

        self.create = async_to_raw_response_wrapper(
            endpoints.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            endpoints.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            endpoints.update,
        )
        self.list = async_to_raw_response_wrapper(
            endpoints.list,
        )
        self.delete = async_to_raw_response_wrapper(
            endpoints.delete,
        )
        self.create_cluster = async_to_raw_response_wrapper(
            endpoints.create_cluster,
        )
        self.delete_cluster = async_to_raw_response_wrapper(
            endpoints.delete_cluster,
        )
        self.list_avzones = async_to_raw_response_wrapper(
            endpoints.list_avzones,
        )
        self.list_clusters = async_to_raw_response_wrapper(
            endpoints.list_clusters,
        )
        self.list_regions = async_to_raw_response_wrapper(
            endpoints.list_regions,
        )
        self.retrieve_cluster = async_to_raw_response_wrapper(
            endpoints.retrieve_cluster,
        )
        self.update_cluster = async_to_raw_response_wrapper(
            endpoints.update_cluster,
        )

    @cached_property
    def storages(self) -> AsyncStoragesResourceWithRawResponse:
        return AsyncStoragesResourceWithRawResponse(self._endpoints.storages)


class EndpointsResourceWithStreamingResponse:
    def __init__(self, endpoints: EndpointsResource) -> None:
        self._endpoints = endpoints

        self.create = to_streamed_response_wrapper(
            endpoints.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            endpoints.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            endpoints.update,
        )
        self.list = to_streamed_response_wrapper(
            endpoints.list,
        )
        self.delete = to_streamed_response_wrapper(
            endpoints.delete,
        )
        self.create_cluster = to_streamed_response_wrapper(
            endpoints.create_cluster,
        )
        self.delete_cluster = to_streamed_response_wrapper(
            endpoints.delete_cluster,
        )
        self.list_avzones = to_streamed_response_wrapper(
            endpoints.list_avzones,
        )
        self.list_clusters = to_streamed_response_wrapper(
            endpoints.list_clusters,
        )
        self.list_regions = to_streamed_response_wrapper(
            endpoints.list_regions,
        )
        self.retrieve_cluster = to_streamed_response_wrapper(
            endpoints.retrieve_cluster,
        )
        self.update_cluster = to_streamed_response_wrapper(
            endpoints.update_cluster,
        )

    @cached_property
    def storages(self) -> StoragesResourceWithStreamingResponse:
        return StoragesResourceWithStreamingResponse(self._endpoints.storages)


class AsyncEndpointsResourceWithStreamingResponse:
    def __init__(self, endpoints: AsyncEndpointsResource) -> None:
        self._endpoints = endpoints

        self.create = async_to_streamed_response_wrapper(
            endpoints.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            endpoints.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            endpoints.update,
        )
        self.list = async_to_streamed_response_wrapper(
            endpoints.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            endpoints.delete,
        )
        self.create_cluster = async_to_streamed_response_wrapper(
            endpoints.create_cluster,
        )
        self.delete_cluster = async_to_streamed_response_wrapper(
            endpoints.delete_cluster,
        )
        self.list_avzones = async_to_streamed_response_wrapper(
            endpoints.list_avzones,
        )
        self.list_clusters = async_to_streamed_response_wrapper(
            endpoints.list_clusters,
        )
        self.list_regions = async_to_streamed_response_wrapper(
            endpoints.list_regions,
        )
        self.retrieve_cluster = async_to_streamed_response_wrapper(
            endpoints.retrieve_cluster,
        )
        self.update_cluster = async_to_streamed_response_wrapper(
            endpoints.update_cluster,
        )

    @cached_property
    def storages(self) -> AsyncStoragesResourceWithStreamingResponse:
        return AsyncStoragesResourceWithStreamingResponse(self._endpoints.storages)
