# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....pagination import SyncCursorPagination, AsyncCursorPagination
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.endpoints import (
    adapter_list_params,
    adapter_create_params,
    adapter_delete_params,
    adapter_update_params,
)
from ....types.beta.endpoints.adapter_list_response import AdapterListResponse
from ....types.beta.endpoints.adapter_create_response import AdapterCreateResponse
from ....types.beta.endpoints.adapter_delete_response import AdapterDeleteResponse
from ....types.beta.endpoints.adapter_update_response import AdapterUpdateResponse
from ....types.beta.endpoints.adapter_retrieve_response import AdapterRetrieveResponse

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

    def create(
        self,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        adapter_model_id: str,
        adapter_revision_id: str | Omit = omit,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterCreateResponse:
        """Attaches a LoRA adapter to a deployment.

        If the deployment is at adapter
        capacity, force can evict the oldest adapter.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          adapter_model_id: Adapter model identifier to attach.

          adapter_revision_id: Optional adapter revision to pin. If omitted, the latest revision is resolved at
              request time.

          force: Whether to evict the oldest adapter if the deployment is at adapter capacity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
            ),
            body=maybe_transform(
                {
                    "adapter_model_id": adapter_model_id,
                    "adapter_revision_id": adapter_revision_id,
                    "force": force,
                },
                adapter_create_params.AdapterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterRetrieveResponse:
        """
        Gets an attached adapter and its per-cluster load state.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        adapter_revision_id: str,
        etag: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterUpdateResponse:
        """
        Updates the pinned revision of an attached adapter using its row-level etag for
        optimistic concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          adapter_revision_id: New adapter revision to pin.

          etag: Row-level etag from a prior AddAdapter, UpdateAdapter, GetAdapter, or
              ListAdapters response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "adapter_revision_id": adapter_revision_id,
                    "etag": etag,
                },
                adapter_update_params.AdapterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterUpdateResponse,
        )

    def list(
        self,
        endpoint_id: str,
        deployment_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[AdapterListResponse]:
        """
        Lists LoRA adapters attached to a deployment with per-cluster load state.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          after: Cursor from a previous adapter list response.

          limit: Maximum number of adapters to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
            ),
            page=SyncCursorPagination[AdapterListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    adapter_list_params.AdapterListParams,
                ),
            ),
            model=AdapterListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        etag: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterDeleteResponse:
        """
        Detaches an adapter from a deployment using its row-level etag for optimistic
        concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          etag: Adapter etag from a previous add, update, get, or list response. The removal is
              rejected if the adapter changed after that response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, adapter_delete_params.AdapterDeleteParams),
            ),
            cast_to=AdapterDeleteResponse,
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

    async def create(
        self,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        adapter_model_id: str,
        adapter_revision_id: str | Omit = omit,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterCreateResponse:
        """Attaches a LoRA adapter to a deployment.

        If the deployment is at adapter
        capacity, force can evict the oldest adapter.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          adapter_model_id: Adapter model identifier to attach.

          adapter_revision_id: Optional adapter revision to pin. If omitted, the latest revision is resolved at
              request time.

          force: Whether to evict the oldest adapter if the deployment is at adapter capacity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
            ),
            body=await async_maybe_transform(
                {
                    "adapter_model_id": adapter_model_id,
                    "adapter_revision_id": adapter_revision_id,
                    "force": force,
                },
                adapter_create_params.AdapterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterRetrieveResponse:
        """
        Gets an attached adapter and its per-cluster load state.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        adapter_revision_id: str,
        etag: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterUpdateResponse:
        """
        Updates the pinned revision of an attached adapter using its row-level etag for
        optimistic concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          adapter_revision_id: New adapter revision to pin.

          etag: Row-level etag from a prior AddAdapter, UpdateAdapter, GetAdapter, or
              ListAdapters response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "adapter_revision_id": adapter_revision_id,
                    "etag": etag,
                },
                adapter_update_params.AdapterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AdapterUpdateResponse,
        )

    def list(
        self,
        endpoint_id: str,
        deployment_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[AdapterListResponse, AsyncCursorPagination[AdapterListResponse]]:
        """
        Lists LoRA adapters attached to a deployment with per-cluster load state.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          after: Cursor from a previous adapter list response.

          limit: Maximum number of adapters to return.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
            ),
            page=AsyncCursorPagination[AdapterListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    adapter_list_params.AdapterListParams,
                ),
            ),
            model=AdapterListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        deployment_id: str,
        etag: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdapterDeleteResponse:
        """
        Detaches an adapter from a deployment using its row-level etag for optimistic
        concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          deployment_id: Deployment identifier.

          id: Adapter model identifier.

          etag: Adapter etag from a previous add, update, get, or list response. The removal is
              rejected if the adapter changed after that response.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{deployment_id}/adapters/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                deployment_id=deployment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, adapter_delete_params.AdapterDeleteParams),
            ),
            cast_to=AdapterDeleteResponse,
        )


class AdaptersResourceWithRawResponse:
    def __init__(self, adapters: AdaptersResource) -> None:
        self._adapters = adapters

        self.create = to_raw_response_wrapper(
            adapters.create,
        )
        self.retrieve = to_raw_response_wrapper(
            adapters.retrieve,
        )
        self.update = to_raw_response_wrapper(
            adapters.update,
        )
        self.list = to_raw_response_wrapper(
            adapters.list,
        )
        self.delete = to_raw_response_wrapper(
            adapters.delete,
        )


class AsyncAdaptersResourceWithRawResponse:
    def __init__(self, adapters: AsyncAdaptersResource) -> None:
        self._adapters = adapters

        self.create = async_to_raw_response_wrapper(
            adapters.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            adapters.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            adapters.update,
        )
        self.list = async_to_raw_response_wrapper(
            adapters.list,
        )
        self.delete = async_to_raw_response_wrapper(
            adapters.delete,
        )


class AdaptersResourceWithStreamingResponse:
    def __init__(self, adapters: AdaptersResource) -> None:
        self._adapters = adapters

        self.create = to_streamed_response_wrapper(
            adapters.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            adapters.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            adapters.update,
        )
        self.list = to_streamed_response_wrapper(
            adapters.list,
        )
        self.delete = to_streamed_response_wrapper(
            adapters.delete,
        )


class AsyncAdaptersResourceWithStreamingResponse:
    def __init__(self, adapters: AsyncAdaptersResource) -> None:
        self._adapters = adapters

        self.create = async_to_streamed_response_wrapper(
            adapters.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            adapters.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            adapters.update,
        )
        self.list = async_to_streamed_response_wrapper(
            adapters.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            adapters.delete,
        )
