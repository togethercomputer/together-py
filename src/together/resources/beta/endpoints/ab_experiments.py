# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
    ab_experiment_list_params,
    ab_experiment_create_params,
    ab_experiment_delete_params,
    ab_experiment_update_params,
)
from ....types.beta.ab_member_param import AbMemberParam
from ....types.beta.endpoints.ab_experiment import AbExperiment
from ....types.beta.endpoints.ab_experiment_delete_response import AbExperimentDeleteResponse

__all__ = ["AbExperimentsResource", "AsyncAbExperimentsResource"]


class AbExperimentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AbExperimentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AbExperimentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AbExperimentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AbExperimentsResourceWithStreamingResponse(self)

    def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        members: Iterable[AbMemberParam],
        name: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AbExperiment:
        """
        Creates a managed control/variant split across two to 20 deployments under the
        same endpoint. Exactly one member is the control, member percentages must add up
        to 100, and the split applies only to traffic that the endpoint would otherwise
        send to the control.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          members: Two to 20 participating deployments with exactly one control. Integer traffic
              percentages across all members must add up to 100.

          name: Human-readable A/B experiment name, unique within the endpoint.

          description: Optional free-form description.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=maybe_transform(
                {
                    "members": members,
                    "name": name,
                    "description": description,
                },
                ab_experiment_create_params.AbExperimentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AbExperiment,
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
    ) -> AbExperiment:
        """
        Retrieves an A/B experiment and its participating deployments, roles, and
        traffic percentages.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AbExperiment,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str | Omit = omit,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        members: Iterable[AbMemberParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AbExperiment:
        """Updates an experiment's description or member traffic percentages.

        Use the
        experiment etag for optimistic concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

          update_mask: Fields to update. If omitted, all mutable fields are overwritten.

          description: Updated free-form description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          members: Complete replacement member set. Requires two to 20 deployments, exactly one
              control, and percentages that add up to 100.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "members": members,
                },
                ab_experiment_update_params.AbExperimentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"update_mask": update_mask}, ab_experiment_update_params.AbExperimentUpdateParams
                ),
            ),
            cast_to=AbExperiment,
        )

    def list(
        self,
        endpoint_id: str,
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
    ) -> SyncCursorPagination[AbExperiment]:
        """
        Lists the managed live-traffic experiments configured for an endpoint.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous A/B experiment list response.

          limit: Maximum number of A/B experiments to return. Max 500, defaults to 50.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=SyncCursorPagination[AbExperiment],
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
                    ab_experiment_list_params.AbExperimentListParams,
                ),
            ),
            model=AbExperiment,
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
    ) -> AbExperimentDeleteResponse:
        """Deletes an A/B experiment and removes its managed traffic split.

        The deployments
        themselves are not deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, ab_experiment_delete_params.AbExperimentDeleteParams),
            ),
            cast_to=AbExperimentDeleteResponse,
        )


class AsyncAbExperimentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAbExperimentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAbExperimentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAbExperimentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncAbExperimentsResourceWithStreamingResponse(self)

    async def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        members: Iterable[AbMemberParam],
        name: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AbExperiment:
        """
        Creates a managed control/variant split across two to 20 deployments under the
        same endpoint. Exactly one member is the control, member percentages must add up
        to 100, and the split applies only to traffic that the endpoint would otherwise
        send to the control.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          members: Two to 20 participating deployments with exactly one control. Integer traffic
              percentages across all members must add up to 100.

          name: Human-readable A/B experiment name, unique within the endpoint.

          description: Optional free-form description.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=await async_maybe_transform(
                {
                    "members": members,
                    "name": name,
                    "description": description,
                },
                ab_experiment_create_params.AbExperimentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AbExperiment,
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
    ) -> AbExperiment:
        """
        Retrieves an A/B experiment and its participating deployments, roles, and
        traffic percentages.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AbExperiment,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        update_mask: str | Omit = omit,
        description: str | Omit = omit,
        etag: str | Omit = omit,
        members: Iterable[AbMemberParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AbExperiment:
        """Updates an experiment's description or member traffic percentages.

        Use the
        experiment etag for optimistic concurrency.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

          update_mask: Fields to update. If omitted, all mutable fields are overwritten.

          description: Updated free-form description.

          etag: Opaque version tag from a prior read for optimistic concurrency.

          members: Complete replacement member set. Requires two to 20 deployments, exactly one
              control, and percentages that add up to 100.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "description": description,
                    "etag": etag,
                    "members": members,
                },
                ab_experiment_update_params.AbExperimentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, ab_experiment_update_params.AbExperimentUpdateParams
                ),
            ),
            cast_to=AbExperiment,
        )

    def list(
        self,
        endpoint_id: str,
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
    ) -> AsyncPaginator[AbExperiment, AsyncCursorPagination[AbExperiment]]:
        """
        Lists the managed live-traffic experiments configured for an endpoint.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous A/B experiment list response.

          limit: Maximum number of A/B experiments to return. Max 500, defaults to 50.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=AsyncCursorPagination[AbExperiment],
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
                    ab_experiment_list_params.AbExperimentListParams,
                ),
            ),
            model=AbExperiment,
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
    ) -> AbExperimentDeleteResponse:
        """Deletes an A/B experiment and removes its managed traffic split.

        The deployments
        themselves are not deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: A/B experiment identifier.

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
                "/projects/{project_id}/endpoints/{endpoint_id}/abExperiments/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, ab_experiment_delete_params.AbExperimentDeleteParams),
            ),
            cast_to=AbExperimentDeleteResponse,
        )


class AbExperimentsResourceWithRawResponse:
    def __init__(self, ab_experiments: AbExperimentsResource) -> None:
        self._ab_experiments = ab_experiments

        self.create = to_raw_response_wrapper(
            ab_experiments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            ab_experiments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            ab_experiments.update,
        )
        self.list = to_raw_response_wrapper(
            ab_experiments.list,
        )
        self.delete = to_raw_response_wrapper(
            ab_experiments.delete,
        )


class AsyncAbExperimentsResourceWithRawResponse:
    def __init__(self, ab_experiments: AsyncAbExperimentsResource) -> None:
        self._ab_experiments = ab_experiments

        self.create = async_to_raw_response_wrapper(
            ab_experiments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            ab_experiments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            ab_experiments.update,
        )
        self.list = async_to_raw_response_wrapper(
            ab_experiments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            ab_experiments.delete,
        )


class AbExperimentsResourceWithStreamingResponse:
    def __init__(self, ab_experiments: AbExperimentsResource) -> None:
        self._ab_experiments = ab_experiments

        self.create = to_streamed_response_wrapper(
            ab_experiments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            ab_experiments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            ab_experiments.update,
        )
        self.list = to_streamed_response_wrapper(
            ab_experiments.list,
        )
        self.delete = to_streamed_response_wrapper(
            ab_experiments.delete,
        )


class AsyncAbExperimentsResourceWithStreamingResponse:
    def __init__(self, ab_experiments: AsyncAbExperimentsResource) -> None:
        self._ab_experiments = ab_experiments

        self.create = async_to_streamed_response_wrapper(
            ab_experiments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            ab_experiments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            ab_experiments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            ab_experiments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            ab_experiments.delete,
        )
