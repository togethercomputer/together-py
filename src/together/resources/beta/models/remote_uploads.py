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
from ....types.beta.models import remote_upload_list_params, remote_upload_create_params, remote_upload_events_params
from ....types.beta.models.remote_upload_list_response import RemoteUploadListResponse
from ....types.beta.models.remote_upload_create_response import RemoteUploadCreateResponse
from ....types.beta.models.remote_upload_events_response import RemoteUploadEventsResponse
from ....types.beta.models.remote_upload_retrieve_response import RemoteUploadRetrieveResponse

__all__ = ["RemoteUploadsResource", "AsyncRemoteUploadsResource"]


class RemoteUploadsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RemoteUploadsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RemoteUploadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RemoteUploadsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RemoteUploadsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        project_id: str | None = None,
        model_id: str,
        remote_url: str,
        token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RemoteUploadCreateResponse:
        """
        Starts an asynchronous job that imports model files from Hugging Face or a
        presigned URL into a registered model and creates a model revision when the
        import completes.

        Args:
          project_id: Project identifier.

          model_id: ID of the registered model that will receive the imported files.

          remote_url: Hugging Face repository URL or presigned archive URL to import.

          token: Optional source credential used to access a private remote location. The value
              is write-only and is not returned.

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
            + path_template("/projects/{project_id}/models/uploads", project_id=project_id),
            body=maybe_transform(
                {
                    "model_id": model_id,
                    "remote_url": remote_url,
                    "token": token,
                },
                remote_upload_create_params.RemoteUploadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RemoteUploadCreateResponse,
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
    ) -> RemoteUploadRetrieveResponse:
        """
        Retrieves the status, progress details, retry counts, and timestamps for a
        remote model import job.

        Args:
          project_id: Project identifier.

          id: Remote upload identifier.

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
            + path_template("/projects/{project_id}/models/uploads/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RemoteUploadRetrieveResponse,
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
    ) -> SyncCursorPagination[RemoteUploadListResponse]:
        """
        Lists asynchronous jobs that import model files from Hugging Face or a presigned
        remote URL.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous remote upload list response.

          limit: Maximum number of uploads to return.

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
            + path_template("/projects/{project_id}/models/uploads", project_id=project_id),
            page=SyncCursorPagination[RemoteUploadListResponse],
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
                    remote_upload_list_params.RemoteUploadListParams,
                ),
            ),
            model=RemoteUploadListResponse,
        )

    def events(
        self,
        id: str,
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
    ) -> RemoteUploadEventsResponse:
        """
        Lists progress and diagnostic events for a remote model import job.

        Args:
          project_id: Project identifier.

          id: Remote upload identifier.

          after: Cursor from a previous remote upload event list response.

          limit: Maximum number of events to return.

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
            + path_template("/projects/{project_id}/models/uploads/{id}/events", project_id=project_id, id=id),
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
                    remote_upload_events_params.RemoteUploadEventsParams,
                ),
            ),
            cast_to=RemoteUploadEventsResponse,
        )


class AsyncRemoteUploadsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRemoteUploadsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRemoteUploadsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRemoteUploadsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRemoteUploadsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        project_id: str | None = None,
        model_id: str,
        remote_url: str,
        token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RemoteUploadCreateResponse:
        """
        Starts an asynchronous job that imports model files from Hugging Face or a
        presigned URL into a registered model and creates a model revision when the
        import completes.

        Args:
          project_id: Project identifier.

          model_id: ID of the registered model that will receive the imported files.

          remote_url: Hugging Face repository URL or presigned archive URL to import.

          token: Optional source credential used to access a private remote location. The value
              is write-only and is not returned.

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
            + path_template("/projects/{project_id}/models/uploads", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "model_id": model_id,
                    "remote_url": remote_url,
                    "token": token,
                },
                remote_upload_create_params.RemoteUploadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RemoteUploadCreateResponse,
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
    ) -> RemoteUploadRetrieveResponse:
        """
        Retrieves the status, progress details, retry counts, and timestamps for a
        remote model import job.

        Args:
          project_id: Project identifier.

          id: Remote upload identifier.

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
            + path_template("/projects/{project_id}/models/uploads/{id}", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RemoteUploadRetrieveResponse,
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
    ) -> AsyncPaginator[RemoteUploadListResponse, AsyncCursorPagination[RemoteUploadListResponse]]:
        """
        Lists asynchronous jobs that import model files from Hugging Face or a presigned
        remote URL.

        Args:
          project_id: Project identifier.

          after: Cursor from a previous remote upload list response.

          limit: Maximum number of uploads to return.

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
            + path_template("/projects/{project_id}/models/uploads", project_id=project_id),
            page=AsyncCursorPagination[RemoteUploadListResponse],
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
                    remote_upload_list_params.RemoteUploadListParams,
                ),
            ),
            model=RemoteUploadListResponse,
        )

    async def events(
        self,
        id: str,
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
    ) -> RemoteUploadEventsResponse:
        """
        Lists progress and diagnostic events for a remote model import job.

        Args:
          project_id: Project identifier.

          id: Remote upload identifier.

          after: Cursor from a previous remote upload event list response.

          limit: Maximum number of events to return.

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
            + path_template("/projects/{project_id}/models/uploads/{id}/events", project_id=project_id, id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    remote_upload_events_params.RemoteUploadEventsParams,
                ),
            ),
            cast_to=RemoteUploadEventsResponse,
        )


class RemoteUploadsResourceWithRawResponse:
    def __init__(self, remote_uploads: RemoteUploadsResource) -> None:
        self._remote_uploads = remote_uploads

        self.create = to_raw_response_wrapper(
            remote_uploads.create,
        )
        self.retrieve = to_raw_response_wrapper(
            remote_uploads.retrieve,
        )
        self.list = to_raw_response_wrapper(
            remote_uploads.list,
        )
        self.events = to_raw_response_wrapper(
            remote_uploads.events,
        )


class AsyncRemoteUploadsResourceWithRawResponse:
    def __init__(self, remote_uploads: AsyncRemoteUploadsResource) -> None:
        self._remote_uploads = remote_uploads

        self.create = async_to_raw_response_wrapper(
            remote_uploads.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            remote_uploads.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            remote_uploads.list,
        )
        self.events = async_to_raw_response_wrapper(
            remote_uploads.events,
        )


class RemoteUploadsResourceWithStreamingResponse:
    def __init__(self, remote_uploads: RemoteUploadsResource) -> None:
        self._remote_uploads = remote_uploads

        self.create = to_streamed_response_wrapper(
            remote_uploads.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            remote_uploads.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            remote_uploads.list,
        )
        self.events = to_streamed_response_wrapper(
            remote_uploads.events,
        )


class AsyncRemoteUploadsResourceWithStreamingResponse:
    def __init__(self, remote_uploads: AsyncRemoteUploadsResource) -> None:
        self._remote_uploads = remote_uploads

        self.create = async_to_streamed_response_wrapper(
            remote_uploads.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            remote_uploads.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            remote_uploads.list,
        )
        self.events = async_to_streamed_response_wrapper(
            remote_uploads.events,
        )
