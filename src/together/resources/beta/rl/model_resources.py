# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

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
from ...._base_client import make_request_options
from ....types.beta.rl import (
    model_resource_list_params,
    model_resource_stop_params,
    model_resource_create_params,
    model_resource_estimate_cost_params,
)
from ....types.beta.rl.model_resources import ModelResources
from ....types.beta.rl.optimizer_config_param import OptimizerConfigParam
from ....types.beta.rl.model_resources_list_response import ModelResourcesListResponse
from ....types.beta.rl.model_resources_estimate_cost_response import ModelResourcesEstimateCostResponse

__all__ = ["ModelResourcesResource", "AsyncModelResourcesResource"]


class ModelResourcesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ModelResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ModelResourcesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        base_model: str,
        compute_config: model_resource_create_params.ComputeConfig | Omit = omit,
        lora_enabled: bool | Omit = omit,
        optimizer_config: OptimizerConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """
        Provisions a standalone model resource that training sessions can attach to.

        Args:
          base_model: Base model to provision the resource for, selected from /rl/supported-models

          compute_config: Compute layout to provision.

          lora_enabled: Whether the resource hosts LoRA sessions or a single full-weight session

          optimizer_config: Optimizer configuration for this resource.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/rl/model-resources",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "compute_config": compute_config,
                    "lora_enabled": lora_enabled,
                    "optimizer_config": optimizer_config,
                },
                model_resource_create_params.ModelResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResources,
        )

    def retrieve(
        self,
        model_resources_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """
        Gets a model resource by its ID and returns its details.

        Args:
          model_resources_id: ID of the model resource

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_resources_id:
            raise ValueError(f"Expected a non-empty value for `model_resources_id` but received {model_resources_id!r}")
        return self._get(
            path_template("/rl/model-resources/{model_resources_id}", model_resources_id=model_resources_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResources,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        created_by: str | Omit = omit,
        limit: int | Omit = omit,
        status: List[
            Literal[
                "MODEL_RESOURCES_STATUS_PENDING",
                "MODEL_RESOURCES_STATUS_CREATING",
                "MODEL_RESOURCES_STATUS_READY",
                "MODEL_RESOURCES_STATUS_ERROR",
                "MODEL_RESOURCES_STATUS_STOPPED",
                "MODEL_RESOURCES_STATUS_STOPPING",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResourcesListResponse:
        """
        Lists the caller's model resources.

        Args:
          after: Cursor for pagination

          created_by: Filter resources in the current project by the creator ID. Pass "me" to show
              resources you created.

          limit: Maximum number of resources to return (1-100)

          status: Status filters. When omitted, resources in any status are returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/rl/model-resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "created_by": created_by,
                        "limit": limit,
                        "status": status,
                    },
                    model_resource_list_params.ModelResourceListParams,
                ),
            ),
            cast_to=ModelResourcesListResponse,
        )

    def estimate_cost(
        self,
        *,
        base_model: str,
        compute_config: model_resource_estimate_cost_params.ComputeConfig | Omit = omit,
        lora_enabled: bool | Omit = omit,
        optimizer_config: OptimizerConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResourcesEstimateCostResponse:
        """
        Estimates a model resource's on-demand hourly price without creating it.

        Args:
          base_model: Base model to provision the resource for, selected from /rl/supported-models

          compute_config: Compute layout to provision.

          lora_enabled: Whether the resource hosts LoRA sessions or a single full-weight session

          optimizer_config: Optimizer configuration for this resource.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/rl/model-resources/estimate-cost",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "compute_config": compute_config,
                    "lora_enabled": lora_enabled,
                    "optimizer_config": optimizer_config,
                },
                model_resource_estimate_cost_params.ModelResourceEstimateCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResourcesEstimateCostResponse,
        )

    def stop(
        self,
        model_resources_id: str,
        *,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """Stops the model resource and releases its allocated compute.

        If active training
        sessions are attached, the request fails unless `force=true`. A forced stop also
        stops all attached training sessions.

        Args:
          model_resources_id: ID of the model resource

          force: When true, also stop all attached training sessions. When false, the request
              fails if any training sessions are active.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_resources_id:
            raise ValueError(f"Expected a non-empty value for `model_resources_id` but received {model_resources_id!r}")
        return self._post(
            path_template("/rl/model-resources/{model_resources_id}/stop", model_resources_id=model_resources_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"force": force}, model_resource_stop_params.ModelResourceStopParams),
            ),
            cast_to=ModelResources,
        )


class AsyncModelResourcesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncModelResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncModelResourcesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        base_model: str,
        compute_config: model_resource_create_params.ComputeConfig | Omit = omit,
        lora_enabled: bool | Omit = omit,
        optimizer_config: OptimizerConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """
        Provisions a standalone model resource that training sessions can attach to.

        Args:
          base_model: Base model to provision the resource for, selected from /rl/supported-models

          compute_config: Compute layout to provision.

          lora_enabled: Whether the resource hosts LoRA sessions or a single full-weight session

          optimizer_config: Optimizer configuration for this resource.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/rl/model-resources",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "compute_config": compute_config,
                    "lora_enabled": lora_enabled,
                    "optimizer_config": optimizer_config,
                },
                model_resource_create_params.ModelResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResources,
        )

    async def retrieve(
        self,
        model_resources_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """
        Gets a model resource by its ID and returns its details.

        Args:
          model_resources_id: ID of the model resource

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_resources_id:
            raise ValueError(f"Expected a non-empty value for `model_resources_id` but received {model_resources_id!r}")
        return await self._get(
            path_template("/rl/model-resources/{model_resources_id}", model_resources_id=model_resources_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResources,
        )

    async def list(
        self,
        *,
        after: str | Omit = omit,
        created_by: str | Omit = omit,
        limit: int | Omit = omit,
        status: List[
            Literal[
                "MODEL_RESOURCES_STATUS_PENDING",
                "MODEL_RESOURCES_STATUS_CREATING",
                "MODEL_RESOURCES_STATUS_READY",
                "MODEL_RESOURCES_STATUS_ERROR",
                "MODEL_RESOURCES_STATUS_STOPPED",
                "MODEL_RESOURCES_STATUS_STOPPING",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResourcesListResponse:
        """
        Lists the caller's model resources.

        Args:
          after: Cursor for pagination

          created_by: Filter resources in the current project by the creator ID. Pass "me" to show
              resources you created.

          limit: Maximum number of resources to return (1-100)

          status: Status filters. When omitted, resources in any status are returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/rl/model-resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "created_by": created_by,
                        "limit": limit,
                        "status": status,
                    },
                    model_resource_list_params.ModelResourceListParams,
                ),
            ),
            cast_to=ModelResourcesListResponse,
        )

    async def estimate_cost(
        self,
        *,
        base_model: str,
        compute_config: model_resource_estimate_cost_params.ComputeConfig | Omit = omit,
        lora_enabled: bool | Omit = omit,
        optimizer_config: OptimizerConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResourcesEstimateCostResponse:
        """
        Estimates a model resource's on-demand hourly price without creating it.

        Args:
          base_model: Base model to provision the resource for, selected from /rl/supported-models

          compute_config: Compute layout to provision.

          lora_enabled: Whether the resource hosts LoRA sessions or a single full-weight session

          optimizer_config: Optimizer configuration for this resource.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/rl/model-resources/estimate-cost",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "compute_config": compute_config,
                    "lora_enabled": lora_enabled,
                    "optimizer_config": optimizer_config,
                },
                model_resource_estimate_cost_params.ModelResourceEstimateCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelResourcesEstimateCostResponse,
        )

    async def stop(
        self,
        model_resources_id: str,
        *,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelResources:
        """Stops the model resource and releases its allocated compute.

        If active training
        sessions are attached, the request fails unless `force=true`. A forced stop also
        stops all attached training sessions.

        Args:
          model_resources_id: ID of the model resource

          force: When true, also stop all attached training sessions. When false, the request
              fails if any training sessions are active.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_resources_id:
            raise ValueError(f"Expected a non-empty value for `model_resources_id` but received {model_resources_id!r}")
        return await self._post(
            path_template("/rl/model-resources/{model_resources_id}/stop", model_resources_id=model_resources_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"force": force}, model_resource_stop_params.ModelResourceStopParams),
            ),
            cast_to=ModelResources,
        )


class ModelResourcesResourceWithRawResponse:
    def __init__(self, model_resources: ModelResourcesResource) -> None:
        self._model_resources = model_resources

        self.create = to_raw_response_wrapper(
            model_resources.create,
        )
        self.retrieve = to_raw_response_wrapper(
            model_resources.retrieve,
        )
        self.list = to_raw_response_wrapper(
            model_resources.list,
        )
        self.estimate_cost = to_raw_response_wrapper(
            model_resources.estimate_cost,
        )
        self.stop = to_raw_response_wrapper(
            model_resources.stop,
        )


class AsyncModelResourcesResourceWithRawResponse:
    def __init__(self, model_resources: AsyncModelResourcesResource) -> None:
        self._model_resources = model_resources

        self.create = async_to_raw_response_wrapper(
            model_resources.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            model_resources.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            model_resources.list,
        )
        self.estimate_cost = async_to_raw_response_wrapper(
            model_resources.estimate_cost,
        )
        self.stop = async_to_raw_response_wrapper(
            model_resources.stop,
        )


class ModelResourcesResourceWithStreamingResponse:
    def __init__(self, model_resources: ModelResourcesResource) -> None:
        self._model_resources = model_resources

        self.create = to_streamed_response_wrapper(
            model_resources.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            model_resources.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            model_resources.list,
        )
        self.estimate_cost = to_streamed_response_wrapper(
            model_resources.estimate_cost,
        )
        self.stop = to_streamed_response_wrapper(
            model_resources.stop,
        )


class AsyncModelResourcesResourceWithStreamingResponse:
    def __init__(self, model_resources: AsyncModelResourcesResource) -> None:
        self._model_resources = model_resources

        self.create = async_to_streamed_response_wrapper(
            model_resources.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            model_resources.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            model_resources.list,
        )
        self.estimate_cost = async_to_streamed_response_wrapper(
            model_resources.estimate_cost,
        )
        self.stop = async_to_streamed_response_wrapper(
            model_resources.stop,
        )
