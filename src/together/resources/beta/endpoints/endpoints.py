# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from datetime import datetime
from typing_extensions import Literal

import httpx

from .adapters import (
    AdaptersResource,
    AsyncAdaptersResource,
    AdaptersResourceWithRawResponse,
    AsyncAdaptersResourceWithRawResponse,
    AdaptersResourceWithStreamingResponse,
    AsyncAdaptersResourceWithStreamingResponse,
)
from .hardware import (
    HardwareResource,
    AsyncHardwareResource,
    HardwareResourceWithRawResponse,
    AsyncHardwareResourceWithRawResponse,
    HardwareResourceWithStreamingResponse,
    AsyncHardwareResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from .deployments import (
    DeploymentsResource,
    AsyncDeploymentsResource,
    DeploymentsResourceWithRawResponse,
    AsyncDeploymentsResourceWithRawResponse,
    DeploymentsResourceWithStreamingResponse,
    AsyncDeploymentsResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncCursorPagination, AsyncCursorPagination
from ....types.beta import (
    endpoint_list_params,
    endpoint_create_params,
    endpoint_delete_params,
    endpoint_update_params,
    endpoint_analytics_params,
    endpoint_list_events_params,
    endpoint_list_org_scoped_params,
)
from .ab_experiments import (
    AbExperimentsResource,
    AsyncAbExperimentsResource,
    AbExperimentsResourceWithRawResponse,
    AsyncAbExperimentsResourceWithRawResponse,
    AbExperimentsResourceWithStreamingResponse,
    AsyncAbExperimentsResourceWithStreamingResponse,
)
from ...._base_client import AsyncPaginator, make_request_options
from .placement_profiles import (
    PlacementProfilesResource,
    AsyncPlacementProfilesResource,
    PlacementProfilesResourceWithRawResponse,
    AsyncPlacementProfilesResourceWithRawResponse,
    PlacementProfilesResourceWithStreamingResponse,
    AsyncPlacementProfilesResourceWithStreamingResponse,
)
from ....types.beta.endpoint import Endpoint
from .shadow_experiments.shadow_experiments import (
    ShadowExperimentsResource,
    AsyncShadowExperimentsResource,
    ShadowExperimentsResourceWithRawResponse,
    AsyncShadowExperimentsResourceWithRawResponse,
    ShadowExperimentsResourceWithStreamingResponse,
    AsyncShadowExperimentsResourceWithStreamingResponse,
)
from ....types.beta.endpoint_delete_response import EndpointDeleteResponse
from ....types.beta.endpoint_analytics_response import EndpointAnalyticsResponse
from ....types.beta.endpoint_list_events_response import EndpointListEventsResponse
from ....types.beta.endpoint_traffic_split_entry_param import EndpointTrafficSplitEntryParam

__all__ = ["EndpointsResource", "AsyncEndpointsResource"]


class EndpointsResource(SyncAPIResource):
    @cached_property
    def placement_profiles(self) -> PlacementProfilesResource:
        return PlacementProfilesResource(self._client)

    @cached_property
    def ab_experiments(self) -> AbExperimentsResource:
        return AbExperimentsResource(self._client)

    @cached_property
    def shadow_experiments(self) -> ShadowExperimentsResource:
        return ShadowExperimentsResource(self._client)

    @cached_property
    def hardware(self) -> HardwareResource:
        return HardwareResource(self._client)

    @cached_property
    def adapters(self) -> AdaptersResource:
        return AdaptersResource(self._client)

    @cached_property
    def deployments(self) -> DeploymentsResource:
        return DeploymentsResource(self._client)

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
        project_id: str | None = None,
        name: str,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """Creates a stable, inference-addressable endpoint.

        Add one or more deployments
        and configure its traffic split before sending inference requests to the
        endpoint name.

        Args:
          project_id: Project identifier.

          name: Inference-addressable endpoint name to create.

          visibility: Who can discover the endpoint. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints", project_id=project_id),
            body=maybe_transform(
                {
                    "name": name,
                    "visibility": visibility,
                },
                endpoint_create_params.EndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """
        Retrieves an endpoint and lightweight summaries of the deployments attached to
        it.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        update_mask: str | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        traffic_split: Iterable[EndpointTrafficSplitEntryParam] | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """
        Updates mutable endpoint fields such as its endpoint string, visibility, or
        deployment traffic split. Use `updateMask` to select fields explicitly and
        `etag` in the request body for optimistic concurrency.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          update_mask: Fields to update. If not set, the fields populated are updated.

          etag: Current endpoint version. The update is rejected if this value no longer
              matches.

          name: Updated endpoint string.

          traffic_split: Replacement live traffic split. Use an empty list to stop routing live traffic.

          visibility: Who can discover the endpoint. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            body=maybe_transform(
                {
                    "etag": etag,
                    "name": name,
                    "traffic_split": traffic_split,
                    "visibility": visibility,
                },
                endpoint_update_params.EndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"update_mask": update_mask}, endpoint_update_params.EndpointUpdateParams),
            ),
            cast_to=Endpoint,
        )

    def list(
        self,
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
    ) -> SyncCursorPagination[Endpoint]:
        """
        Lists the dedicated inference endpoints owned by the specified project.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous response.

          filter: Filter expression using `name`, `created_at`, or `updated_at` with comparison
              operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
              substring matching with `:` and prefix/suffix wildcards with `*`, and accepts a
              bare endpoint name or `<project_slug>/<endpoint_name>`.

          limit: Maximum number of endpoints to return.

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
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints", project_id=project_id),
            page=SyncCursorPagination[Endpoint],
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
                    endpoint_list_params.EndpointListParams,
                ),
            ),
            model=Endpoint,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeleteResponse:
        """Permanently deletes an endpoint.

        Delete its deployments first; use `etag` to
        reject the request if the endpoint changed after it was read.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, endpoint_delete_params.EndpointDeleteParams),
            ),
            cast_to=EndpointDeleteResponse,
        )

    def analytics(
        self,
        id: str,
        *,
        project_id: str | None = None,
        deployment_id: str | Omit = omit,
        end_time: Union[str, datetime] | Omit = omit,
        granularity: str | Omit = omit,
        include_time_series: bool | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointAnalyticsResponse:
        """
        Returns aggregated request, token, latency, throughput, error, and
        resource-utilization metrics for an endpoint over a time range. Optionally
        includes time-series buckets and a per-deployment breakdown.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          deployment_id: Restrict to a single deployment under this endpoint.

          end_time: Exclusive end of the time range. Defaults to now if unset.

          granularity: Time-series bucket duration, such as `1m`, `1h`, or `1d`. Defaults to `1d`.

          include_time_series: When true, include per-bucket time series in the response.

          start_time: Inclusive start of the time range. Defaults to 24 hours ago if unset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}/analytics", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "end_time": end_time,
                        "granularity": granularity,
                        "include_time_series": include_time_series,
                        "start_time": start_time,
                    },
                    endpoint_analytics_params.EndpointAnalyticsParams,
                ),
            ),
            cast_to=EndpointAnalyticsResponse,
        )

    def list_events(
        self,
        id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        deployment_ids: SequenceNotStr[str] | Omit = omit,
        limit: int | Omit = omit,
        min_level: Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"] | Omit = omit,
        since: Union[str, datetime] | Omit = omit,
        source_kinds: List[Literal["SOURCE_KIND_ENDPOINT", "SOURCE_KIND_DEPLOYMENT"]] | Omit = omit,
        subject_id: str | Omit = omit,
        types: SequenceNotStr[str] | Omit = omit,
        until: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[EndpointListEventsResponse]:
        """Lists an endpoint's audit and lifecycle events newest first.

        The feed combines
        endpoint changes with provisioning, scaling, readiness, rollout, and other
        events from deployments under the endpoint.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          after: Cursor from a previous endpoint event list response.

          deployment_ids: Deployment IDs whose events should be included. Every ID must belong to the
              endpoint. Supplying this filter excludes endpoint-scoped events unless
              `SOURCE_KIND_ENDPOINT` is also included in `sourceKinds`.

          limit: Maximum number of events to return. Max 500, defaults to 50.

          min_level: Minimum severity. Omit to disable severity filtering.

          since: Return only events at or after this time.

          source_kinds: Resource kinds whose events should be included. Omit to include both endpoint-
              and deployment-scoped events.

          subject_id: ID of a subject associated with the event, such as a rollout. Combined with
              other filters using AND.

          types: Event types to include, such as `deployment.scaled` or `condition.set`. Combined
              with other filters using AND.

          until: Return only events strictly before this time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}/events", project_id=project_id, id=id),
            page=SyncCursorPagination[EndpointListEventsResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "deployment_ids": deployment_ids,
                        "limit": limit,
                        "min_level": min_level,
                        "since": since,
                        "source_kinds": source_kinds,
                        "subject_id": subject_id,
                        "types": types,
                        "until": until,
                    },
                    endpoint_list_events_params.EndpointListEventsParams,
                ),
            ),
            model=EndpointListEventsResponse,
        )

    def list_org_scoped(
        self,
        organization_id: str,
        *,
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
    ) -> SyncCursorPagination[Endpoint]:
        """
        Lists endpoints shared with every project in the specified organization.
        Project-private and public endpoints are not included.

        Args:
          organization_id: Organization identifier.

          after: Cursor from a previous list response.

          filter: Filter expression using `name`, `created_at`, or `updated_at` with comparison
              operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
              substring matching with `:` and prefix/suffix wildcards with `*`, and must be a
              bare endpoint name.

          limit: Maximum number of results to return.

          order_by: Sort field for the results. Supports `created_at` or `updated_at`, optionally
              followed by `asc` or `desc`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/organizations/{organization_id}/endpoints", organization_id=organization_id),
            page=SyncCursorPagination[Endpoint],
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
                    endpoint_list_org_scoped_params.EndpointListOrgScopedParams,
                ),
            ),
            model=Endpoint,
        )


class AsyncEndpointsResource(AsyncAPIResource):
    @cached_property
    def placement_profiles(self) -> AsyncPlacementProfilesResource:
        return AsyncPlacementProfilesResource(self._client)

    @cached_property
    def ab_experiments(self) -> AsyncAbExperimentsResource:
        return AsyncAbExperimentsResource(self._client)

    @cached_property
    def shadow_experiments(self) -> AsyncShadowExperimentsResource:
        return AsyncShadowExperimentsResource(self._client)

    @cached_property
    def hardware(self) -> AsyncHardwareResource:
        return AsyncHardwareResource(self._client)

    @cached_property
    def adapters(self) -> AsyncAdaptersResource:
        return AsyncAdaptersResource(self._client)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResource:
        return AsyncDeploymentsResource(self._client)

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
        project_id: str | None = None,
        name: str,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """Creates a stable, inference-addressable endpoint.

        Add one or more deployments
        and configure its traffic split before sending inference requests to the
        endpoint name.

        Args:
          project_id: Project identifier.

          name: Inference-addressable endpoint name to create.

          visibility: Who can discover the endpoint. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "name": name,
                    "visibility": visibility,
                },
                endpoint_create_params.EndpointCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """
        Retrieves an endpoint and lightweight summaries of the deployments attached to
        it.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Endpoint,
        )

    async def update(
        self,
        id: str,
        *,
        project_id: str | None = None,
        update_mask: str | Omit = omit,
        etag: str | Omit = omit,
        name: str | Omit = omit,
        traffic_split: Iterable[EndpointTrafficSplitEntryParam] | Omit = omit,
        visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Endpoint:
        """
        Updates mutable endpoint fields such as its endpoint string, visibility, or
        deployment traffic split. Use `updateMask` to select fields explicitly and
        `etag` in the request body for optimistic concurrency.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          update_mask: Fields to update. If not set, the fields populated are updated.

          etag: Current endpoint version. The update is rejected if this value no longer
              matches.

          name: Updated endpoint string.

          traffic_split: Replacement live traffic split. Use an empty list to stop routing live traffic.

          visibility: Who can discover the endpoint. `VISIBILITY_PRIVATE` restricts it to the project;
              `VISIBILITY_INTERNAL` shares it with the organization.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            body=await async_maybe_transform(
                {
                    "etag": etag,
                    "name": name,
                    "traffic_split": traffic_split,
                    "visibility": visibility,
                },
                endpoint_update_params.EndpointUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"update_mask": update_mask}, endpoint_update_params.EndpointUpdateParams
                ),
            ),
            cast_to=Endpoint,
        )

    def list(
        self,
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
    ) -> AsyncPaginator[Endpoint, AsyncCursorPagination[Endpoint]]:
        """
        Lists the dedicated inference endpoints owned by the specified project.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous response.

          filter: Filter expression using `name`, `created_at`, or `updated_at` with comparison
              operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
              substring matching with `:` and prefix/suffix wildcards with `*`, and accepts a
              bare endpoint name or `<project_slug>/<endpoint_name>`.

          limit: Maximum number of endpoints to return.

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
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints", project_id=project_id),
            page=AsyncCursorPagination[Endpoint],
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
                    endpoint_list_params.EndpointListParams,
                ),
            ),
            model=Endpoint,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointDeleteResponse:
        """Permanently deletes an endpoint.

        Delete its deployments first; use `etag` to
        reject the request if the endpoint changed after it was read.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, endpoint_delete_params.EndpointDeleteParams),
            ),
            cast_to=EndpointDeleteResponse,
        )

    async def analytics(
        self,
        id: str,
        *,
        project_id: str | None = None,
        deployment_id: str | Omit = omit,
        end_time: Union[str, datetime] | Omit = omit,
        granularity: str | Omit = omit,
        include_time_series: bool | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EndpointAnalyticsResponse:
        """
        Returns aggregated request, token, latency, throughput, error, and
        resource-utilization metrics for an endpoint over a time range. Optionally
        includes time-series buckets and a per-deployment breakdown.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          deployment_id: Restrict to a single deployment under this endpoint.

          end_time: Exclusive end of the time range. Defaults to now if unset.

          granularity: Time-series bucket duration, such as `1m`, `1h`, or `1d`. Defaults to `1d`.

          include_time_series: When true, include per-bucket time series in the response.

          start_time: Inclusive start of the time range. Defaults to 24 hours ago if unset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}/analytics", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "end_time": end_time,
                        "granularity": granularity,
                        "include_time_series": include_time_series,
                        "start_time": start_time,
                    },
                    endpoint_analytics_params.EndpointAnalyticsParams,
                ),
            ),
            cast_to=EndpointAnalyticsResponse,
        )

    def list_events(
        self,
        id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        deployment_ids: SequenceNotStr[str] | Omit = omit,
        limit: int | Omit = omit,
        min_level: Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"] | Omit = omit,
        since: Union[str, datetime] | Omit = omit,
        source_kinds: List[Literal["SOURCE_KIND_ENDPOINT", "SOURCE_KIND_DEPLOYMENT"]] | Omit = omit,
        subject_id: str | Omit = omit,
        types: SequenceNotStr[str] | Omit = omit,
        until: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[EndpointListEventsResponse, AsyncCursorPagination[EndpointListEventsResponse]]:
        """Lists an endpoint's audit and lifecycle events newest first.

        The feed combines
        endpoint changes with provisioning, scaling, readiness, rollout, and other
        events from deployments under the endpoint.

        Args:
          project_id: Project identifier.

          id: Endpoint identifier.

          after: Cursor from a previous endpoint event list response.

          deployment_ids: Deployment IDs whose events should be included. Every ID must belong to the
              endpoint. Supplying this filter excludes endpoint-scoped events unless
              `SOURCE_KIND_ENDPOINT` is also included in `sourceKinds`.

          limit: Maximum number of events to return. Max 500, defaults to 50.

          min_level: Minimum severity. Omit to disable severity filtering.

          since: Return only events at or after this time.

          source_kinds: Resource kinds whose events should be included. Omit to include both endpoint-
              and deployment-scoped events.

          subject_id: ID of a subject associated with the event, such as a rollout. Combined with
              other filters using AND.

          types: Event types to include, such as `deployment.scaled` or `condition.set`. Combined
              with other filters using AND.

          until: Return only events strictly before this time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/projects/{project_id}/endpoints/{id}/events", project_id=project_id, id=id),
            page=AsyncCursorPagination[EndpointListEventsResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "deployment_ids": deployment_ids,
                        "limit": limit,
                        "min_level": min_level,
                        "since": since,
                        "source_kinds": source_kinds,
                        "subject_id": subject_id,
                        "types": types,
                        "until": until,
                    },
                    endpoint_list_events_params.EndpointListEventsParams,
                ),
            ),
            model=EndpointListEventsResponse,
        )

    def list_org_scoped(
        self,
        organization_id: str,
        *,
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
    ) -> AsyncPaginator[Endpoint, AsyncCursorPagination[Endpoint]]:
        """
        Lists endpoints shared with every project in the specified organization.
        Project-private and public endpoints are not included.

        Args:
          organization_id: Organization identifier.

          after: Cursor from a previous list response.

          filter: Filter expression using `name`, `created_at`, or `updated_at` with comparison
              operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
              substring matching with `:` and prefix/suffix wildcards with `*`, and must be a
              bare endpoint name.

          limit: Maximum number of results to return.

          order_by: Sort field for the results. Supports `created_at` or `updated_at`, optionally
              followed by `asc` or `desc`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template("/organizations/{organization_id}/endpoints", organization_id=organization_id),
            page=AsyncCursorPagination[Endpoint],
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
                    endpoint_list_org_scoped_params.EndpointListOrgScopedParams,
                ),
            ),
            model=Endpoint,
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
        self.analytics = to_raw_response_wrapper(
            endpoints.analytics,
        )
        self.list_events = to_raw_response_wrapper(
            endpoints.list_events,
        )
        self.list_org_scoped = to_raw_response_wrapper(
            endpoints.list_org_scoped,
        )

    @cached_property
    def placement_profiles(self) -> PlacementProfilesResourceWithRawResponse:
        return PlacementProfilesResourceWithRawResponse(self._endpoints.placement_profiles)

    @cached_property
    def ab_experiments(self) -> AbExperimentsResourceWithRawResponse:
        return AbExperimentsResourceWithRawResponse(self._endpoints.ab_experiments)

    @cached_property
    def shadow_experiments(self) -> ShadowExperimentsResourceWithRawResponse:
        return ShadowExperimentsResourceWithRawResponse(self._endpoints.shadow_experiments)

    @cached_property
    def hardware(self) -> HardwareResourceWithRawResponse:
        return HardwareResourceWithRawResponse(self._endpoints.hardware)

    @cached_property
    def adapters(self) -> AdaptersResourceWithRawResponse:
        return AdaptersResourceWithRawResponse(self._endpoints.adapters)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithRawResponse:
        return DeploymentsResourceWithRawResponse(self._endpoints.deployments)


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
        self.analytics = async_to_raw_response_wrapper(
            endpoints.analytics,
        )
        self.list_events = async_to_raw_response_wrapper(
            endpoints.list_events,
        )
        self.list_org_scoped = async_to_raw_response_wrapper(
            endpoints.list_org_scoped,
        )

    @cached_property
    def placement_profiles(self) -> AsyncPlacementProfilesResourceWithRawResponse:
        return AsyncPlacementProfilesResourceWithRawResponse(self._endpoints.placement_profiles)

    @cached_property
    def ab_experiments(self) -> AsyncAbExperimentsResourceWithRawResponse:
        return AsyncAbExperimentsResourceWithRawResponse(self._endpoints.ab_experiments)

    @cached_property
    def shadow_experiments(self) -> AsyncShadowExperimentsResourceWithRawResponse:
        return AsyncShadowExperimentsResourceWithRawResponse(self._endpoints.shadow_experiments)

    @cached_property
    def hardware(self) -> AsyncHardwareResourceWithRawResponse:
        return AsyncHardwareResourceWithRawResponse(self._endpoints.hardware)

    @cached_property
    def adapters(self) -> AsyncAdaptersResourceWithRawResponse:
        return AsyncAdaptersResourceWithRawResponse(self._endpoints.adapters)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithRawResponse:
        return AsyncDeploymentsResourceWithRawResponse(self._endpoints.deployments)


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
        self.analytics = to_streamed_response_wrapper(
            endpoints.analytics,
        )
        self.list_events = to_streamed_response_wrapper(
            endpoints.list_events,
        )
        self.list_org_scoped = to_streamed_response_wrapper(
            endpoints.list_org_scoped,
        )

    @cached_property
    def placement_profiles(self) -> PlacementProfilesResourceWithStreamingResponse:
        return PlacementProfilesResourceWithStreamingResponse(self._endpoints.placement_profiles)

    @cached_property
    def ab_experiments(self) -> AbExperimentsResourceWithStreamingResponse:
        return AbExperimentsResourceWithStreamingResponse(self._endpoints.ab_experiments)

    @cached_property
    def shadow_experiments(self) -> ShadowExperimentsResourceWithStreamingResponse:
        return ShadowExperimentsResourceWithStreamingResponse(self._endpoints.shadow_experiments)

    @cached_property
    def hardware(self) -> HardwareResourceWithStreamingResponse:
        return HardwareResourceWithStreamingResponse(self._endpoints.hardware)

    @cached_property
    def adapters(self) -> AdaptersResourceWithStreamingResponse:
        return AdaptersResourceWithStreamingResponse(self._endpoints.adapters)

    @cached_property
    def deployments(self) -> DeploymentsResourceWithStreamingResponse:
        return DeploymentsResourceWithStreamingResponse(self._endpoints.deployments)


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
        self.analytics = async_to_streamed_response_wrapper(
            endpoints.analytics,
        )
        self.list_events = async_to_streamed_response_wrapper(
            endpoints.list_events,
        )
        self.list_org_scoped = async_to_streamed_response_wrapper(
            endpoints.list_org_scoped,
        )

    @cached_property
    def placement_profiles(self) -> AsyncPlacementProfilesResourceWithStreamingResponse:
        return AsyncPlacementProfilesResourceWithStreamingResponse(self._endpoints.placement_profiles)

    @cached_property
    def ab_experiments(self) -> AsyncAbExperimentsResourceWithStreamingResponse:
        return AsyncAbExperimentsResourceWithStreamingResponse(self._endpoints.ab_experiments)

    @cached_property
    def shadow_experiments(self) -> AsyncShadowExperimentsResourceWithStreamingResponse:
        return AsyncShadowExperimentsResourceWithStreamingResponse(self._endpoints.shadow_experiments)

    @cached_property
    def hardware(self) -> AsyncHardwareResourceWithStreamingResponse:
        return AsyncHardwareResourceWithStreamingResponse(self._endpoints.hardware)

    @cached_property
    def adapters(self) -> AsyncAdaptersResourceWithStreamingResponse:
        return AsyncAdaptersResourceWithStreamingResponse(self._endpoints.adapters)

    @cached_property
    def deployments(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        return AsyncDeploymentsResourceWithStreamingResponse(self._endpoints.deployments)
