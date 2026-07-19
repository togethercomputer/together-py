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
    deployment_list_params,
    deployment_create_params,
    deployment_delete_params,
    deployment_update_params,
)
from ....types.beta.endpoint_deployment import EndpointDeployment
from ....types.beta.deployment_autoscaling_param import DeploymentAutoscalingParam
from ....types.beta.endpoints.deployment_delete_response import DeploymentDeleteResponse

__all__ = ["DeploymentsResource", "AsyncDeploymentsResource"]


class DeploymentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return DeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return DeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        autoscaling: DeploymentAutoscalingParam,
        name: str,
        validate_only: bool | Omit = omit,
        config: str | Omit = omit,
        config_id: str | Omit = omit,
        enable_lora: bool | Omit = omit,
        model: str | Omit = omit,
        model_id: str | Omit = omit,
        model_revision_id: str | Omit = omit,
        placement: deployment_create_params.Placement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """Creates a model deployment under an endpoint.

        The deployment provisions
        asynchronously; monitor its status before routing live traffic to it.

        Args:
          project_id: ID of the project that owns the endpoint.

          endpoint_id: ID of the endpoint that will contain the deployment.

          autoscaling: Autoscaling configuration for a deployment.

          name: Name for the deployment within its endpoint. Returned as a project- and
              endpoint-qualified inference name.

          validate_only: When true, validates the request without creating or provisioning a deployment.

          config: Immutable config revision in the form
              `projects/{projectId}/configs/{configRevisionId}`. The config must be compatible
              with the model.

          config_id: Deprecated. Use `config`. Config revision identifier to deploy, accepted when
              `config` is unset.

          enable_lora: Enables dynamic loading of LoRA adapters on the deployment.

          model: Model resource name in the form
              `projects/{projectId}/models/{modelId}[/revisions/{revisionId}]`. Omit the
              revision segment to pin the latest revision at creation time.

          model_id: Deprecated. Use `model`. Model identifier to serve, accepted when `model` is
              unset.

          model_revision_id: Deprecated. Use `model` with a /revisions/{revisionId} segment. If omitted, the
              latest revision is resolved at creation.

          placement: Placement controls where a deployment is scheduled.

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
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "name": name,
                    "config": config,
                    "config_id": config_id,
                    "enable_lora": enable_lora,
                    "model": model,
                    "model_id": model_id,
                    "model_revision_id": model_revision_id,
                    "placement": placement,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"validate_only": validate_only}, deployment_create_params.DeploymentCreateParams
                ),
            ),
            cast_to=EndpointDeployment,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """
        Retrieves a deployment's desired configuration, placement, runtime information,
        and current provisioning status.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointDeployment,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str | Omit = omit,
        autoscaling: DeploymentAutoscalingParam | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """
        Updates mutable deployment fields such as its model, configuration, autoscaling
        bounds, or LoRA support. Changes that affect serving may trigger asynchronous
        reprovisioning.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

          update_mask: Fields to update. If not set, the fields populated on `deployment` are updated.

          autoscaling: Autoscaling configuration for a deployment.

          etag: Current deployment version. The update is rejected if this value no longer
              matches.

          name: Updated inference-addressable deployment name.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "etag": etag,
                    "name": name,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, deployment_update_params.DeploymentUpdateParams),
            ),
            cast_to=EndpointDeployment,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        filter: str | Omit = omit,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[EndpointDeployment]:
        """
        Lists the deployments attached to an endpoint, including their model,
        configuration, scaling settings, placement, and current status.

        Args:
          project_id: ID of the project that owns the endpoint.

          endpoint_id: ID of the endpoint whose deployments are listed.

          after: Cursor from a previous deployment list response.

          filter: Filter expression using `name`, `state`, `model`, `created_at`, or `updated_at`
              with comparison operators and AND/OR/NOT; `state` takes a DeploymentState enum
              name and `model` takes a model resource name. `name` supports substring matching
              with `:` and prefix/suffix wildcards with `*`, and accepts a bare deployment
              name or `<project_slug>/<endpoint_name>/<deployment_name>`.

          limit: Maximum number of deployments to return. Max 500, defaults to 50.

          order_by: Sort field for the results. Supports `created_at` or `updated_at`, optionally
              followed by `asc` or `desc`.

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
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=SyncCursorPagination[EndpointDeployment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "filter": filter,
                        "limit": limit,
                        "order_by": order_by,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            model=EndpointDeployment,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentDeleteResponse:
        """Permanently deletes a deployment from its endpoint.

        Remove the deployment from
        live traffic first; use `etag` to reject the request if it changed after it was
        read.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

          etag: Etag for optimistic concurrency. If set, the delete is rejected if the current
              etag does not match.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, deployment_delete_params.DeploymentDeleteParams),
            ),
            cast_to=DeploymentDeleteResponse,
        )


class AsyncDeploymentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        autoscaling: DeploymentAutoscalingParam,
        name: str,
        validate_only: bool | Omit = omit,
        config: str | Omit = omit,
        config_id: str | Omit = omit,
        enable_lora: bool | Omit = omit,
        model: str | Omit = omit,
        model_id: str | Omit = omit,
        model_revision_id: str | Omit = omit,
        placement: deployment_create_params.Placement | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """Creates a model deployment under an endpoint.

        The deployment provisions
        asynchronously; monitor its status before routing live traffic to it.

        Args:
          project_id: ID of the project that owns the endpoint.

          endpoint_id: ID of the endpoint that will contain the deployment.

          autoscaling: Autoscaling configuration for a deployment.

          name: Name for the deployment within its endpoint. Returned as a project- and
              endpoint-qualified inference name.

          validate_only: When true, validates the request without creating or provisioning a deployment.

          config: Immutable config revision in the form
              `projects/{projectId}/configs/{configRevisionId}`. The config must be compatible
              with the model.

          config_id: Deprecated. Use `config`. Config revision identifier to deploy, accepted when
              `config` is unset.

          enable_lora: Enables dynamic loading of LoRA adapters on the deployment.

          model: Model resource name in the form
              `projects/{projectId}/models/{modelId}[/revisions/{revisionId}]`. Omit the
              revision segment to pin the latest revision at creation time.

          model_id: Deprecated. Use `model`. Model identifier to serve, accepted when `model` is
              unset.

          model_revision_id: Deprecated. Use `model` with a /revisions/{revisionId} segment. If omitted, the
              latest revision is resolved at creation.

          placement: Placement controls where a deployment is scheduled.

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
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=await async_maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "name": name,
                    "config": config,
                    "config_id": config_id,
                    "enable_lora": enable_lora,
                    "model": model,
                    "model_id": model_id,
                    "model_revision_id": model_revision_id,
                    "placement": placement,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"validate_only": validate_only}, deployment_create_params.DeploymentCreateParams
                ),
            ),
            cast_to=EndpointDeployment,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """
        Retrieves a deployment's desired configuration, placement, runtime information,
        and current provisioning status.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EndpointDeployment,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str | Omit = omit,
        autoscaling: DeploymentAutoscalingParam | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeployment:
        """
        Updates mutable deployment fields such as its model, configuration, autoscaling
        bounds, or LoRA support. Changes that affect serving may trigger asynchronous
        reprovisioning.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

          update_mask: Fields to update. If not set, the fields populated on `deployment` are updated.

          autoscaling: Autoscaling configuration for a deployment.

          etag: Current deployment version. The update is rejected if this value no longer
              matches.

          name: Updated inference-addressable deployment name.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "autoscaling": autoscaling,
                    "etag": etag,
                    "name": name,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, deployment_update_params.DeploymentUpdateParams
                ),
            ),
            cast_to=EndpointDeployment,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        filter: str | Omit = omit,
        limit: int | Omit = omit,
        order_by: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[EndpointDeployment, AsyncCursorPagination[EndpointDeployment]]:
        """
        Lists the deployments attached to an endpoint, including their model,
        configuration, scaling settings, placement, and current status.

        Args:
          project_id: ID of the project that owns the endpoint.

          endpoint_id: ID of the endpoint whose deployments are listed.

          after: Cursor from a previous deployment list response.

          filter: Filter expression using `name`, `state`, `model`, `created_at`, or `updated_at`
              with comparison operators and AND/OR/NOT; `state` takes a DeploymentState enum
              name and `model` takes a model resource name. `name` supports substring matching
              with `:` and prefix/suffix wildcards with `*`, and accepts a bare deployment
              name or `<project_slug>/<endpoint_name>/<deployment_name>`.

          limit: Maximum number of deployments to return. Max 500, defaults to 50.

          order_by: Sort field for the results. Supports `created_at` or `updated_at`, optionally
              followed by `asc` or `desc`.

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
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=AsyncCursorPagination[EndpointDeployment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "filter": filter,
                        "limit": limit,
                        "order_by": order_by,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            model=EndpointDeployment,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentDeleteResponse:
        """Permanently deletes a deployment from its endpoint.

        Remove the deployment from
        live traffic first; use `etag` to reject the request if it changed after it was
        read.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Deployment identifier.

          etag: Etag for optimistic concurrency. If set, the delete is rejected if the current
              etag does not match.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/deployments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, deployment_delete_params.DeploymentDeleteParams),
            ),
            cast_to=DeploymentDeleteResponse,
        )


class DeploymentsResourceWithRawResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployments.update,
        )
        self.list = to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            deployments.delete,
        )


class AsyncDeploymentsResourceWithRawResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_raw_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployments.delete,
        )


class DeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployments.delete,
        )


class AsyncDeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_streamed_response_wrapper(
            deployments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployments.delete,
        )
