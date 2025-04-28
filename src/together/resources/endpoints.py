# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..types import endpoint_list_params, endpoint_create_params, endpoint_update_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ..types.endpoint_list_response import EndpointListResponse
from ..types.endpoint_create_response import EndpointCreateResponse
from ..types.endpoint_update_response import EndpointUpdateResponse
from ..types.endpoint_retrieve_response import EndpointRetrieveResponse

__all__ = ["EndpointsResource", "AsyncEndpointsResource"]


class EndpointsResource(SyncAPIResource):
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
        autoscaling: endpoint_create_params.Autoscaling,
        hardware: str,
        model: str,
        disable_prompt_cache: bool | NotGiven = NOT_GIVEN,
        disable_speculative_decoding: bool | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        inactive_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        state: Literal["STARTED", "STOPPED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointCreateResponse:
        """Creates a new dedicated endpoint for serving models.

        The endpoint will
        automatically start after creation. You can deploy any supported model on
        hardware configurations that meet the model's requirements.

        Args:
          autoscaling: Configuration for automatic scaling of the endpoint

          hardware: The hardware configuration to use for this endpoint

          model: The model to deploy on this endpoint

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
            cast_to=EndpointCreateResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointRetrieveResponse:
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
            cast_to=EndpointRetrieveResponse,
        )

    def update(
        self,
        endpoint_id: str,
        *,
        autoscaling: endpoint_update_params.Autoscaling | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        inactive_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        state: Literal["STARTED", "STOPPED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointUpdateResponse:
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
            cast_to=EndpointUpdateResponse,
        )

    def list(
        self,
        *,
        type: Literal["dedicated", "serverless"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointListResponse:
        """Returns a list of all endpoints associated with your account.

        You can filter the
        results by type (dedicated or serverless).

        Args:
          type: Filter endpoints by type

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
                query=maybe_transform({"type": type}, endpoint_list_params.EndpointListParams),
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
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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


class AsyncEndpointsResource(AsyncAPIResource):
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
        autoscaling: endpoint_create_params.Autoscaling,
        hardware: str,
        model: str,
        disable_prompt_cache: bool | NotGiven = NOT_GIVEN,
        disable_speculative_decoding: bool | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        inactive_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        state: Literal["STARTED", "STOPPED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointCreateResponse:
        """Creates a new dedicated endpoint for serving models.

        The endpoint will
        automatically start after creation. You can deploy any supported model on
        hardware configurations that meet the model's requirements.

        Args:
          autoscaling: Configuration for automatic scaling of the endpoint

          hardware: The hardware configuration to use for this endpoint

          model: The model to deploy on this endpoint

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
            cast_to=EndpointCreateResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointRetrieveResponse:
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
            cast_to=EndpointRetrieveResponse,
        )

    async def update(
        self,
        endpoint_id: str,
        *,
        autoscaling: endpoint_update_params.Autoscaling | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        inactive_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        state: Literal["STARTED", "STOPPED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointUpdateResponse:
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
            cast_to=EndpointUpdateResponse,
        )

    async def list(
        self,
        *,
        type: Literal["dedicated", "serverless"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndpointListResponse:
        """Returns a list of all endpoints associated with your account.

        You can filter the
        results by type (dedicated or serverless).

        Args:
          type: Filter endpoints by type

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
                query=await async_maybe_transform({"type": type}, endpoint_list_params.EndpointListParams),
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
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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
