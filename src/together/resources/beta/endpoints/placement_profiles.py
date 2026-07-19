# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform
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
from ....types.beta.endpoints import placement_profile_list_params
from ....types.beta.endpoints.placement_profile import PlacementProfile

__all__ = ["PlacementProfilesResource", "AsyncPlacementProfilesResource"]


class PlacementProfilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PlacementProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return PlacementProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PlacementProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return PlacementProfilesResourceWithStreamingResponse(self)

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
    ) -> PlacementProfile:
        """
        Retrieves a reusable placement profile and its ordered region preferences.

        Args:
          project_id: Project identifier.

          id: Placement profile identifier.

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
            + path_template("/projects/{project_id}/placement-profiles/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlacementProfile,
        )

    def list(
        self,
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
    ) -> SyncCursorPagination[PlacementProfile]:
        """
        Lists reusable, project-visible placement policies that control the regions
        where deployments may be scheduled.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous placement profile list response.

          limit: Maximum number of profiles to return. Max 500, defaults to 50.

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
            + path_template("/projects/{project_id}/placement-profiles", project_id=project_id),
            page=SyncCursorPagination[PlacementProfile],
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
                    placement_profile_list_params.PlacementProfileListParams,
                ),
            ),
            model=PlacementProfile,
        )


class AsyncPlacementProfilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPlacementProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncPlacementProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPlacementProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncPlacementProfilesResourceWithStreamingResponse(self)

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
    ) -> PlacementProfile:
        """
        Retrieves a reusable placement profile and its ordered region preferences.

        Args:
          project_id: Project identifier.

          id: Placement profile identifier.

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
            + path_template("/projects/{project_id}/placement-profiles/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PlacementProfile,
        )

    def list(
        self,
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
    ) -> AsyncPaginator[PlacementProfile, AsyncCursorPagination[PlacementProfile]]:
        """
        Lists reusable, project-visible placement policies that control the regions
        where deployments may be scheduled.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous placement profile list response.

          limit: Maximum number of profiles to return. Max 500, defaults to 50.

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
            + path_template("/projects/{project_id}/placement-profiles", project_id=project_id),
            page=AsyncCursorPagination[PlacementProfile],
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
                    placement_profile_list_params.PlacementProfileListParams,
                ),
            ),
            model=PlacementProfile,
        )


class PlacementProfilesResourceWithRawResponse:
    def __init__(self, placement_profiles: PlacementProfilesResource) -> None:
        self._placement_profiles = placement_profiles

        self.retrieve = to_raw_response_wrapper(
            placement_profiles.retrieve,
        )
        self.list = to_raw_response_wrapper(
            placement_profiles.list,
        )


class AsyncPlacementProfilesResourceWithRawResponse:
    def __init__(self, placement_profiles: AsyncPlacementProfilesResource) -> None:
        self._placement_profiles = placement_profiles

        self.retrieve = async_to_raw_response_wrapper(
            placement_profiles.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            placement_profiles.list,
        )


class PlacementProfilesResourceWithStreamingResponse:
    def __init__(self, placement_profiles: PlacementProfilesResource) -> None:
        self._placement_profiles = placement_profiles

        self.retrieve = to_streamed_response_wrapper(
            placement_profiles.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            placement_profiles.list,
        )


class AsyncPlacementProfilesResourceWithStreamingResponse:
    def __init__(self, placement_profiles: AsyncPlacementProfilesResource) -> None:
        self._placement_profiles = placement_profiles

        self.retrieve = async_to_streamed_response_wrapper(
            placement_profiles.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            placement_profiles.list,
        )
