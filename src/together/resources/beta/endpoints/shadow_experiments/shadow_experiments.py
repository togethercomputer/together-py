# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from .targets import (
    TargetsResource,
    AsyncTargetsResource,
    TargetsResourceWithRawResponse,
    AsyncTargetsResourceWithRawResponse,
    TargetsResourceWithStreamingResponse,
    AsyncTargetsResourceWithStreamingResponse,
)
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
from .....types.beta.endpoints import (
    shadow_experiment_list_params,
    shadow_experiment_create_params,
    shadow_experiment_delete_params,
    shadow_experiment_update_params,
)
from .....types.beta.shadow_source_param import ShadowSourceParam
from .....types.beta.endpoints.shadow_experiment import ShadowExperiment
from .....types.beta.endpoints.shadow_experiment_delete_response import ShadowExperimentDeleteResponse

__all__ = ["ShadowExperimentsResource", "AsyncShadowExperimentsResource"]


class ShadowExperimentsResource(SyncAPIResource):
    @cached_property
    def targets(self) -> TargetsResource:
        return TargetsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ShadowExperimentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ShadowExperimentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ShadowExperimentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ShadowExperimentsResourceWithStreamingResponse(self)

    def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        name: str,
        source: ShadowSourceParam,
        targets: Iterable[shadow_experiment_create_params.Target] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperiment:
        """
        Creates an experiment that mirrors a sampled portion of endpoint traffic to one
        or more target deployments without returning their responses to clients. Add a
        description with the update operation after creation.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          name: Human-readable shadow experiment name, unique within the endpoint. At most 256
              characters.

          source: Traffic source for a shadow experiment. The public API supports endpoint sources
              only.

          targets: Optional initial target deployments. At most 100 targets; manage later changes
              through the target APIs.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=maybe_transform(
                {
                    "name": name,
                    "source": source,
                    "targets": targets,
                },
                shadow_experiment_create_params.ShadowExperimentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperiment,
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
    ) -> ShadowExperiment:
        """
        Retrieves a shadow experiment, including its sampling strategy and target
        deployments.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperiment,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        source: ShadowSourceParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperiment:
        """
        Updates a shadow experiment's description or source sampling strategy.
        `updateMask` is required; source changes also require the current `etag` in the
        request body.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

          update_mask: Required fields to update, such as description or source.

          description: Updated free-form description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          source: Traffic source for a shadow experiment. The public API supports endpoint sources
              only.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "source": source,
                },
                shadow_experiment_update_params.ShadowExperimentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"update_mask": update_mask}, shadow_experiment_update_params.ShadowExperimentUpdateParams
                ),
            ),
            cast_to=ShadowExperiment,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        include_targets: bool | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[ShadowExperiment]:
        """
        Lists experiments that mirror sampled endpoint traffic to target deployments
        without affecting client responses. Set `includeTargets=true` to include target
        details inline.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous shadow experiment list response.

          include_targets: Whether to include target deployments in each returned shadow experiment.

          limit: Maximum number of shadow experiments to return. Max 500, defaults to 50.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=SyncCursorPagination[ShadowExperiment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "include_targets": include_targets,
                        "limit": limit,
                    },
                    shadow_experiment_list_params.ShadowExperimentListParams,
                ),
            ),
            model=ShadowExperiment,
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
    ) -> ShadowExperimentDeleteResponse:
        """Deletes a shadow experiment and its target records.

        The underlying deployments
        are not deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, shadow_experiment_delete_params.ShadowExperimentDeleteParams),
            ),
            cast_to=ShadowExperimentDeleteResponse,
        )


class AsyncShadowExperimentsResource(AsyncAPIResource):
    @cached_property
    def targets(self) -> AsyncTargetsResource:
        return AsyncTargetsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncShadowExperimentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncShadowExperimentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncShadowExperimentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncShadowExperimentsResourceWithStreamingResponse(self)

    async def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        name: str,
        source: ShadowSourceParam,
        targets: Iterable[shadow_experiment_create_params.Target] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperiment:
        """
        Creates an experiment that mirrors a sampled portion of endpoint traffic to one
        or more target deployments without returning their responses to clients. Add a
        description with the update operation after creation.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          name: Human-readable shadow experiment name, unique within the endpoint. At most 256
              characters.

          source: Traffic source for a shadow experiment. The public API supports endpoint sources
              only.

          targets: Optional initial target deployments. At most 100 targets; manage later changes
              through the target APIs.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=await async_maybe_transform(
                {
                    "name": name,
                    "source": source,
                    "targets": targets,
                },
                shadow_experiment_create_params.ShadowExperimentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperiment,
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
    ) -> ShadowExperiment:
        """
        Retrieves a shadow experiment, including its sampling strategy and target
        deployments.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ShadowExperiment,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        source: ShadowSourceParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ShadowExperiment:
        """
        Updates a shadow experiment's description or source sampling strategy.
        `updateMask` is required; source changes also require the current `etag` in the
        request body.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

          update_mask: Required fields to update, such as description or source.

          description: Updated free-form description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          source: Traffic source for a shadow experiment. The public API supports endpoint sources
              only.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "source": source,
                },
                shadow_experiment_update_params.ShadowExperimentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, shadow_experiment_update_params.ShadowExperimentUpdateParams
                ),
            ),
            cast_to=ShadowExperiment,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        include_targets: bool | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ShadowExperiment, AsyncCursorPagination[ShadowExperiment]]:
        """
        Lists experiments that mirror sampled endpoint traffic to target deployments
        without affecting client responses. Set `includeTargets=true` to include target
        details inline.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous shadow experiment list response.

          include_targets: Whether to include target deployments in each returned shadow experiment.

          limit: Maximum number of shadow experiments to return. Max 500, defaults to 50.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=AsyncCursorPagination[ShadowExperiment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "include_targets": include_targets,
                        "limit": limit,
                    },
                    shadow_experiment_list_params.ShadowExperimentListParams,
                ),
            ),
            model=ShadowExperiment,
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
    ) -> ShadowExperimentDeleteResponse:
        """Deletes a shadow experiment and its target records.

        The underlying deployments
        are not deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Shadow experiment identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/shadowExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"etag": etag}, shadow_experiment_delete_params.ShadowExperimentDeleteParams
                ),
            ),
            cast_to=ShadowExperimentDeleteResponse,
        )


class ShadowExperimentsResourceWithRawResponse:
    def __init__(self, shadow_experiments: ShadowExperimentsResource) -> None:
        self._shadow_experiments = shadow_experiments

        self.create = to_raw_response_wrapper(
            shadow_experiments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            shadow_experiments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            shadow_experiments.update,
        )
        self.list = to_raw_response_wrapper(
            shadow_experiments.list,
        )
        self.delete = to_raw_response_wrapper(
            shadow_experiments.delete,
        )

    @cached_property
    def targets(self) -> TargetsResourceWithRawResponse:
        return TargetsResourceWithRawResponse(self._shadow_experiments.targets)


class AsyncShadowExperimentsResourceWithRawResponse:
    def __init__(self, shadow_experiments: AsyncShadowExperimentsResource) -> None:
        self._shadow_experiments = shadow_experiments

        self.create = async_to_raw_response_wrapper(
            shadow_experiments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            shadow_experiments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            shadow_experiments.update,
        )
        self.list = async_to_raw_response_wrapper(
            shadow_experiments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            shadow_experiments.delete,
        )

    @cached_property
    def targets(self) -> AsyncTargetsResourceWithRawResponse:
        return AsyncTargetsResourceWithRawResponse(self._shadow_experiments.targets)


class ShadowExperimentsResourceWithStreamingResponse:
    def __init__(self, shadow_experiments: ShadowExperimentsResource) -> None:
        self._shadow_experiments = shadow_experiments

        self.create = to_streamed_response_wrapper(
            shadow_experiments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            shadow_experiments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            shadow_experiments.update,
        )
        self.list = to_streamed_response_wrapper(
            shadow_experiments.list,
        )
        self.delete = to_streamed_response_wrapper(
            shadow_experiments.delete,
        )

    @cached_property
    def targets(self) -> TargetsResourceWithStreamingResponse:
        return TargetsResourceWithStreamingResponse(self._shadow_experiments.targets)


class AsyncShadowExperimentsResourceWithStreamingResponse:
    def __init__(self, shadow_experiments: AsyncShadowExperimentsResource) -> None:
        self._shadow_experiments = shadow_experiments

        self.create = async_to_streamed_response_wrapper(
            shadow_experiments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            shadow_experiments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            shadow_experiments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            shadow_experiments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            shadow_experiments.delete,
        )

    @cached_property
    def targets(self) -> AsyncTargetsResourceWithStreamingResponse:
        return AsyncTargetsResourceWithStreamingResponse(self._shadow_experiments.targets)
