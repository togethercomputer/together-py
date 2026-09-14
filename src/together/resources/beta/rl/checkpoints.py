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
from ...._base_client import make_request_options
from ....types.beta.rl import CheckpointVariant, checkpoint_list_params, checkpoint_download_params
from ....types.beta.rl.checkpoint import Checkpoint
from ....types.beta.rl.checkpoint_variant import CheckpointVariant
from ....types.beta.rl.checkpoints_list_response import CheckpointsListResponse
from ....types.beta.rl.checkpoint_download_response import CheckpointDownloadResponse

__all__ = ["CheckpointsResource", "AsyncCheckpointsResource"]


class CheckpointsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CheckpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return CheckpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CheckpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return CheckpointsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Checkpoint:
        """
        Returns metadata for a checkpoint: type, base model, LoRA rank, step, and owning
        session.

        Args:
          id: ID of the checkpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/rl/checkpoints/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Checkpoint,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        base_model: str | Omit = omit,
        limit: int | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckpointsListResponse:
        """Lists training checkpoints owned by the caller.

        Filter by session or base model
        to recover a checkpoint ID for resume. Inference checkpoints are not included;
        they remain on the training session and in the model catalog.

        Args:
          after: Cursor for pagination (ID of the last checkpoint from the previous page)

          base_model: Only return checkpoints trained from this base model. Match is exact.

          limit: Maximum number of checkpoints to return (1-100)

          session_id: Only return checkpoints produced by this training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/rl/checkpoints",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "base_model": base_model,
                        "limit": limit,
                        "session_id": session_id,
                    },
                    checkpoint_list_params.CheckpointListParams,
                ),
            ),
            cast_to=CheckpointsListResponse,
        )

    def download(
        self,
        id: str,
        *,
        variant: CheckpointVariant,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckpointDownloadResponse:
        """Returns presigned URLs for downloading a checkpoint's model files.

        Only
        inference checkpoints support downloading.

        Args:
          id: ID of the checkpoint

          variant: Checkpoint variant to download: merged (full model) or adapter (LoRA weights
              only)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/rl/checkpoints/{id}/download", id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"variant": variant}, checkpoint_download_params.CheckpointDownloadParams),
            ),
            cast_to=CheckpointDownloadResponse,
        )


class AsyncCheckpointsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCheckpointsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncCheckpointsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCheckpointsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncCheckpointsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Checkpoint:
        """
        Returns metadata for a checkpoint: type, base model, LoRA rank, step, and owning
        session.

        Args:
          id: ID of the checkpoint

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/rl/checkpoints/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Checkpoint,
        )

    async def list(
        self,
        *,
        after: str | Omit = omit,
        base_model: str | Omit = omit,
        limit: int | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckpointsListResponse:
        """Lists training checkpoints owned by the caller.

        Filter by session or base model
        to recover a checkpoint ID for resume. Inference checkpoints are not included;
        they remain on the training session and in the model catalog.

        Args:
          after: Cursor for pagination (ID of the last checkpoint from the previous page)

          base_model: Only return checkpoints trained from this base model. Match is exact.

          limit: Maximum number of checkpoints to return (1-100)

          session_id: Only return checkpoints produced by this training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/rl/checkpoints",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "base_model": base_model,
                        "limit": limit,
                        "session_id": session_id,
                    },
                    checkpoint_list_params.CheckpointListParams,
                ),
            ),
            cast_to=CheckpointsListResponse,
        )

    async def download(
        self,
        id: str,
        *,
        variant: CheckpointVariant,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckpointDownloadResponse:
        """Returns presigned URLs for downloading a checkpoint's model files.

        Only
        inference checkpoints support downloading.

        Args:
          id: ID of the checkpoint

          variant: Checkpoint variant to download: merged (full model) or adapter (LoRA weights
              only)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/rl/checkpoints/{id}/download", id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"variant": variant}, checkpoint_download_params.CheckpointDownloadParams
                ),
            ),
            cast_to=CheckpointDownloadResponse,
        )


class CheckpointsResourceWithRawResponse:
    def __init__(self, checkpoints: CheckpointsResource) -> None:
        self._checkpoints = checkpoints

        self.retrieve = to_raw_response_wrapper(
            checkpoints.retrieve,
        )
        self.list = to_raw_response_wrapper(
            checkpoints.list,
        )
        self.download = to_raw_response_wrapper(
            checkpoints.download,
        )


class AsyncCheckpointsResourceWithRawResponse:
    def __init__(self, checkpoints: AsyncCheckpointsResource) -> None:
        self._checkpoints = checkpoints

        self.retrieve = async_to_raw_response_wrapper(
            checkpoints.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            checkpoints.list,
        )
        self.download = async_to_raw_response_wrapper(
            checkpoints.download,
        )


class CheckpointsResourceWithStreamingResponse:
    def __init__(self, checkpoints: CheckpointsResource) -> None:
        self._checkpoints = checkpoints

        self.retrieve = to_streamed_response_wrapper(
            checkpoints.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            checkpoints.list,
        )
        self.download = to_streamed_response_wrapper(
            checkpoints.download,
        )


class AsyncCheckpointsResourceWithStreamingResponse:
    def __init__(self, checkpoints: AsyncCheckpointsResource) -> None:
        self._checkpoints = checkpoints

        self.retrieve = async_to_streamed_response_wrapper(
            checkpoints.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            checkpoints.list,
        )
        self.download = async_to_streamed_response_wrapper(
            checkpoints.download,
        )
