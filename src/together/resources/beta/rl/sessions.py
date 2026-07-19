# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

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
from ....types.beta.rl import session_list_params, session_create_params
from ....types.beta.rl.training_session import TrainingSession
from ....types.beta.rl.lora_config_param import LoraConfigParam
from ....types.beta.rl.session_list_response import SessionListResponse

__all__ = ["SessionsResource", "AsyncSessionsResource"]


class SessionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return SessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return SessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model_resources_id: str,
        lora_config: LoraConfigParam | Omit = omit,
        resume_from_checkpoint_id: str | Omit = omit,
        resume_from_hf_checkpoint: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Creates a training session and returns its details.

        Args:
          model_resources_id: Model resource to attach the session to. The session runs on that resource's GPU
              pods.

          lora_config: LoRA adapter configuration for the session

          resume_from_checkpoint_id: Checkpoint ID to resume from

          resume_from_hf_checkpoint: HuggingFace repo (or hf://) to resume model weights from. Accepts either a full
              model or a PEFT adapter directory. Mutually exclusive with
              resume_from_checkpoint_id.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/rl/training-sessions",
            body=maybe_transform(
                {
                    "model_resources_id": model_resources_id,
                    "lora_config": lora_config,
                    "resume_from_checkpoint_id": resume_from_checkpoint_id,
                    "resume_from_hf_checkpoint": resume_from_hf_checkpoint,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )

    def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Gets a training session by its ID and returns its details.

        Args:
          session_id: ID of the training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            path_template("/rl/training-sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        created_by: str | Omit = omit,
        limit: int | Omit = omit,
        model_resources_id: str | Omit = omit,
        status: List[
            Literal[
                "TRAINING_SESSION_STATUS_CREATING",
                "TRAINING_SESSION_STATUS_RUNNING",
                "TRAINING_SESSION_STATUS_STOPPED",
                "TRAINING_SESSION_STATUS_STOPPING",
                "TRAINING_SESSION_STATUS_ERROR",
                "TRAINING_SESSION_STATUS_EXPIRED",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionListResponse:
        """
        Lists all training sessions.

        Args:
          after: Cursor for pagination (ID of the last session from the previous page)

          created_by: Filter sessions in the current project by the creator ID. Pass "me" to show
              sessions you created.

          limit: Maximum number of sessions to return (1-100)

          model_resources_id: Filter sessions by the model resource they are attached to

          status: Status filters. When omitted, sessions in any status are returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/rl/training-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "created_by": created_by,
                        "limit": limit,
                        "model_resources_id": model_resources_id,
                        "status": status,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionListResponse,
        )

    def stop(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Stops a training session.

        Args:
          session_id: ID of the training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/stop", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )


class AsyncSessionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model_resources_id: str,
        lora_config: LoraConfigParam | Omit = omit,
        resume_from_checkpoint_id: str | Omit = omit,
        resume_from_hf_checkpoint: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Creates a training session and returns its details.

        Args:
          model_resources_id: Model resource to attach the session to. The session runs on that resource's GPU
              pods.

          lora_config: LoRA adapter configuration for the session

          resume_from_checkpoint_id: Checkpoint ID to resume from

          resume_from_hf_checkpoint: HuggingFace repo (or hf://) to resume model weights from. Accepts either a full
              model or a PEFT adapter directory. Mutually exclusive with
              resume_from_checkpoint_id.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/rl/training-sessions",
            body=await async_maybe_transform(
                {
                    "model_resources_id": model_resources_id,
                    "lora_config": lora_config,
                    "resume_from_checkpoint_id": resume_from_checkpoint_id,
                    "resume_from_hf_checkpoint": resume_from_hf_checkpoint,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )

    async def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Gets a training session by its ID and returns its details.

        Args:
          session_id: ID of the training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            path_template("/rl/training-sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )

    async def list(
        self,
        *,
        after: str | Omit = omit,
        created_by: str | Omit = omit,
        limit: int | Omit = omit,
        model_resources_id: str | Omit = omit,
        status: List[
            Literal[
                "TRAINING_SESSION_STATUS_CREATING",
                "TRAINING_SESSION_STATUS_RUNNING",
                "TRAINING_SESSION_STATUS_STOPPED",
                "TRAINING_SESSION_STATUS_STOPPING",
                "TRAINING_SESSION_STATUS_ERROR",
                "TRAINING_SESSION_STATUS_EXPIRED",
            ]
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionListResponse:
        """
        Lists all training sessions.

        Args:
          after: Cursor for pagination (ID of the last session from the previous page)

          created_by: Filter sessions in the current project by the creator ID. Pass "me" to show
              sessions you created.

          limit: Maximum number of sessions to return (1-100)

          model_resources_id: Filter sessions by the model resource they are attached to

          status: Status filters. When omitted, sessions in any status are returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/rl/training-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "created_by": created_by,
                        "limit": limit,
                        "model_resources_id": model_resources_id,
                        "status": status,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionListResponse,
        )

    async def stop(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingSession:
        """
        Stops a training session.

        Args:
          session_id: ID of the training session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/stop", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingSession,
        )


class SessionsResourceWithRawResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.list = to_raw_response_wrapper(
            sessions.list,
        )
        self.stop = to_raw_response_wrapper(
            sessions.stop,
        )


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            sessions.list,
        )
        self.stop = async_to_raw_response_wrapper(
            sessions.stop,
        )


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            sessions.list,
        )
        self.stop = to_streamed_response_wrapper(
            sessions.stop,
        )


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            sessions.list,
        )
        self.stop = async_to_streamed_response_wrapper(
            sessions.stop,
        )
