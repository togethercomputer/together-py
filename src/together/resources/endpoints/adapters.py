# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._utils import path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.endpoints import adapter_add_params, adapter_remove_params
from ...types.endpoints.adapter_add_response import AdapterAddResponse
from ...types.endpoints.adapter_list_response import AdapterListResponse
from ...types.endpoints.adapter_remove_response import AdapterRemoveResponse

__all__ = ["AdaptersResource", "AsyncAdaptersResource"]


class AdaptersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AdaptersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AdaptersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdaptersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AdaptersResourceWithStreamingResponse(self)

    def list(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterListResponse:
        """
        Returns all LoRA adapters bound to the specified dedicated endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._get(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterListResponse,
        )

    def add(
        self,
        endpoint_id: str,
        *,
        model_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterAddResponse:
        """Adds a LoRA adapter model to a dedicated endpoint.

        After this call, inference
        requests to the adapter model name will be routed to the specified endpoint. The
        endpoint must have LoRA enabled, and the adapter's base model must be compatible
        with the endpoint's model. The endpoint name prefix in model_id must match the
        resolved endpoint.

        Args:
          model_id: Combined identifier in format "endpoint_name:adapter_model_name".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._post(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            body=maybe_transform({"model_id": model_id}, adapter_add_params.AdapterAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterAddResponse,
        )

    def remove(
        self,
        endpoint_id: str,
        *,
        model_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterRemoveResponse:
        """Removes the routing rule that binds an adapter to an endpoint.

        The adapter must
        be currently bound to this specific endpoint.

        Args:
          model_id: Combined identifier in format "endpoint_name:adapter_model_name".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._delete(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            body=maybe_transform({"model_id": model_id}, adapter_remove_params.AdapterRemoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterRemoveResponse,
        )


class AsyncAdaptersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAdaptersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAdaptersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdaptersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncAdaptersResourceWithStreamingResponse(self)

    async def list(
        self,
        endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterListResponse:
        """
        Returns all LoRA adapters bound to the specified dedicated endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._get(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterListResponse,
        )

    async def add(
        self,
        endpoint_id: str,
        *,
        model_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterAddResponse:
        """Adds a LoRA adapter model to a dedicated endpoint.

        After this call, inference
        requests to the adapter model name will be routed to the specified endpoint. The
        endpoint must have LoRA enabled, and the adapter's base model must be compatible
        with the endpoint's model. The endpoint name prefix in model_id must match the
        resolved endpoint.

        Args:
          model_id: Combined identifier in format "endpoint_name:adapter_model_name".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._post(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            body=await async_maybe_transform({"model_id": model_id}, adapter_add_params.AdapterAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterAddResponse,
        )

    async def remove(
        self,
        endpoint_id: str,
        *,
        model_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterRemoveResponse:
        """Removes the routing rule that binds an adapter to an endpoint.

        The adapter must
        be currently bound to this specific endpoint.

        Args:
          model_id: Combined identifier in format "endpoint_name:adapter_model_name".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._delete(
            path_template("/endpoints/{endpoint_id}/adapters", endpoint_id=endpoint_id),
            body=await async_maybe_transform({"model_id": model_id}, adapter_remove_params.AdapterRemoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterRemoveResponse,
        )


class AdaptersResourceWithRawResponse:
    def __init__(self, adapters: AdaptersResource) -> None:
        self._adapters = adapters

        self.list = to_raw_response_wrapper(
            adapters.list,
        )
        self.add = to_raw_response_wrapper(
            adapters.add,
        )
        self.remove = to_raw_response_wrapper(
            adapters.remove,
        )


class AsyncAdaptersResourceWithRawResponse:
    def __init__(self, adapters: AsyncAdaptersResource) -> None:
        self._adapters = adapters

        self.list = async_to_raw_response_wrapper(
            adapters.list,
        )
        self.add = async_to_raw_response_wrapper(
            adapters.add,
        )
        self.remove = async_to_raw_response_wrapper(
            adapters.remove,
        )


class AdaptersResourceWithStreamingResponse:
    def __init__(self, adapters: AdaptersResource) -> None:
        self._adapters = adapters

        self.list = to_streamed_response_wrapper(
            adapters.list,
        )
        self.add = to_streamed_response_wrapper(
            adapters.add,
        )
        self.remove = to_streamed_response_wrapper(
            adapters.remove,
        )


class AsyncAdaptersResourceWithStreamingResponse:
    def __init__(self, adapters: AsyncAdaptersResource) -> None:
        self._adapters = adapters

        self.list = async_to_streamed_response_wrapper(
            adapters.list,
        )
        self.add = async_to_streamed_response_wrapper(
            adapters.add,
        )
        self.remove = async_to_streamed_response_wrapper(
            adapters.remove,
        )
