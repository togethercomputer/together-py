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
from ....types.beta.models import config_list_params
from ....types.beta.models.config import Config

__all__ = ["ConfigsResource", "AsyncConfigsResource"]


class ConfigsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return ConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return ConfigsResourceWithStreamingResponse(self)

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
    ) -> Config:
        """
        Retrieves a model configuration revision by ID, including its runtime selectors
        and certifications.

        Args:
          project_id: Project identifier.

          id: Config revision identifier.

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
            + path_template("/projects/{project_id}/configs/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Config,
        )

    def list(
        self,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        reference_model: str | Omit = omit,
        reference_model_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[Config]:
        """Lists production-ready configuration revisions compatible with a reference
        model.

        Specify the model with `referenceModel` or the deprecated
        `referenceModelId`; if both are supplied, they must identify the same model.
        Results include public configurations and configurations owned by the specified
        project.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous list response.

          limit: Maximum number of results to return.

          reference_model: Model resource-name filter using `projects/{projectId}/models/{modelId}`;
              alternative to `referenceModelId`. If both are set, they must agree.

          reference_model_id: Deprecated. Use `referenceModel`. Reference model identifier filter; if both are
              set, they must agree.

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
            + path_template("/projects/{project_id}/configs", project_id=project_id),
            page=SyncCursorPagination[Config],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "reference_model": reference_model,
                        "reference_model_id": reference_model_id,
                    },
                    config_list_params.ConfigListParams,
                ),
            ),
            model=Config,
        )


class AsyncConfigsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncConfigsResourceWithStreamingResponse(self)

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
    ) -> Config:
        """
        Retrieves a model configuration revision by ID, including its runtime selectors
        and certifications.

        Args:
          project_id: Project identifier.

          id: Config revision identifier.

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
            + path_template("/projects/{project_id}/configs/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Config,
        )

    def list(
        self,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        reference_model: str | Omit = omit,
        reference_model_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Config, AsyncCursorPagination[Config]]:
        """Lists production-ready configuration revisions compatible with a reference
        model.

        Specify the model with `referenceModel` or the deprecated
        `referenceModelId`; if both are supplied, they must identify the same model.
        Results include public configurations and configurations owned by the specified
        project.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous list response.

          limit: Maximum number of results to return.

          reference_model: Model resource-name filter using `projects/{projectId}/models/{modelId}`;
              alternative to `referenceModelId`. If both are set, they must agree.

          reference_model_id: Deprecated. Use `referenceModel`. Reference model identifier filter; if both are
              set, they must agree.

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
            + path_template("/projects/{project_id}/configs", project_id=project_id),
            page=AsyncCursorPagination[Config],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "reference_model": reference_model,
                        "reference_model_id": reference_model_id,
                    },
                    config_list_params.ConfigListParams,
                ),
            ),
            model=Config,
        )


class ConfigsResourceWithRawResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.retrieve = to_raw_response_wrapper(
            configs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            configs.list,
        )


class AsyncConfigsResourceWithRawResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.retrieve = async_to_raw_response_wrapper(
            configs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            configs.list,
        )


class ConfigsResourceWithStreamingResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.retrieve = to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            configs.list,
        )


class AsyncConfigsResourceWithStreamingResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.retrieve = async_to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            configs.list,
        )
