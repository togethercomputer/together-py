# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .....pagination import SyncCursorPagination, AsyncCursorPagination
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.endpoints.shadow_experiments import (
    target_list_params,
    target_create_params,
    target_delete_params,
    target_update_params,
)
from .....types.beta.endpoints.shadow_experiments.target_delete_response import TargetDeleteResponse
from .....types.beta.endpoints.shadow_experiments.shadow_experiment_target import ShadowExperimentTarget

__all__ = ["TargetsResource", "AsyncTargetsResource"]


class TargetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return TargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return TargetsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        name: str,
        target_deployment_id: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """
        Adds a deployment under the same endpoint as a target for mirrored requests.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          name: Human-readable target name, unique within the shadow experiment. At most 256
              characters.

          target_deployment_id: Deployment under the parent endpoint that receives mirrored traffic. Exclude it
              from the endpoint's live traffic split.

          description: Optional free-form target description.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
            ),
            body=maybe_transform(
                {
                    "name": name,
                    "target_deployment_id": target_deployment_id,
                    "description": description,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperimentTarget,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """
        Retrieves one target configured to receive mirrored requests from a shadow
        experiment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperimentTarget,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        update_mask: str,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        target_deployment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """Updates a shadow target's name, deployment, or description.

        `updateMask` is
        required and must select at least one mutable field.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

          update_mask: Comma-separated fields to update. Supported fields are `name`,
              `targetDeploymentId`, and `description`.

          description: Updated free-form target description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          name: Updated human-readable target name.

          target_deployment_id: Replacement deployment under the parent endpoint. Exclude it from the endpoint's
              live traffic split.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "name": name,
                    "target_deployment_id": target_deployment_id,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, target_update_params.TargetUpdateParams),
            ),
            cast_to=ShadowExperimentTarget,
        )

    def list(
        self,
        endpoint_id: str,
        experiment_id: str,
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
    ) -> SyncCursorPagination[ShadowExperimentTarget]:
        """
        Lists the deployments that receive mirrored requests from a shadow experiment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          after: Cursor from a previous shadow experiment target list response.

          limit: Maximum number of targets to return. Max 500, defaults to 50.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
            ),
            page=SyncCursorPagination[ShadowExperimentTarget],
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
                    target_list_params.TargetListParams,
                ),
            ),
            model=ShadowExperimentTarget,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TargetDeleteResponse:
        """
        Removes a target from a shadow experiment without deleting the underlying
        deployment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

          etag: Etag for optimistic concurrency.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, target_delete_params.TargetDeleteParams),
            ),
            cast_to=TargetDeleteResponse,
        )


class AsyncTargetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncTargetsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        name: str,
        target_deployment_id: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """
        Adds a deployment under the same endpoint as a target for mirrored requests.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          name: Human-readable target name, unique within the shadow experiment. At most 256
              characters.

          target_deployment_id: Deployment under the parent endpoint that receives mirrored traffic. Exclude it
              from the endpoint's live traffic split.

          description: Optional free-form target description.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
            ),
            body=await async_maybe_transform(
                {
                    "name": name,
                    "target_deployment_id": target_deployment_id,
                    "description": description,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperimentTarget,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """
        Retrieves one target configured to receive mirrored requests from a shadow
        experiment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperimentTarget,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        update_mask: str,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        target_deployment_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperimentTarget:
        """Updates a shadow target's name, deployment, or description.

        `updateMask` is
        required and must select at least one mutable field.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

          update_mask: Comma-separated fields to update. Supported fields are `name`,
              `targetDeploymentId`, and `description`.

          description: Updated free-form target description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          name: Updated human-readable target name.

          target_deployment_id: Replacement deployment under the parent endpoint. Exclude it from the endpoint's
              live traffic split.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "name": name,
                    "target_deployment_id": target_deployment_id,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, target_update_params.TargetUpdateParams
                ),
            ),
            cast_to=ShadowExperimentTarget,
        )

    def list(
        self,
        endpoint_id: str,
        experiment_id: str,
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
    ) -> AsyncPaginator[ShadowExperimentTarget, AsyncCursorPagination[ShadowExperimentTarget]]:
        """
        Lists the deployments that receive mirrored requests from a shadow experiment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          after: Cursor from a previous shadow experiment target list response.

          limit: Maximum number of targets to return. Max 500, defaults to 50.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
            ),
            page=AsyncCursorPagination[ShadowExperimentTarget],
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
                    target_list_params.TargetListParams,
                ),
            ),
            model=ShadowExperimentTarget,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        experiment_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TargetDeleteResponse:
        """
        Removes a target from a shadow experiment without deleting the underlying
        deployment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          experiment_id: Shadow experiment identifier.

          id: Shadow experiment target identifier.

          etag: Etag for optimistic concurrency.

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
        if not experiment_id:
            raise ValueError(f"Expected a non-empty value for `experiment_id` but received {experiment_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{experiment_id}/targets/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                experiment_id=experiment_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, target_delete_params.TargetDeleteParams),
            ),
            cast_to=TargetDeleteResponse,
        )


class TargetsResourceWithRawResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = to_raw_response_wrapper(
            targets.update,
        )
        self.list = to_raw_response_wrapper(
            targets.list,
        )
        self.delete = to_raw_response_wrapper(
            targets.delete,
        )


class AsyncTargetsResourceWithRawResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            targets.update,
        )
        self.list = async_to_raw_response_wrapper(
            targets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            targets.delete,
        )


class TargetsResourceWithStreamingResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            targets.update,
        )
        self.list = to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = to_streamed_response_wrapper(
            targets.delete,
        )


class AsyncTargetsResourceWithStreamingResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            targets.update,
        )
        self.list = async_to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            targets.delete,
        )
