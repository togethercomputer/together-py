# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Iterable, cast
from typing_extensions import Literal

import httpx

from ...types import code_interpreter_execute_params
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.execute_response import ExecuteResponse

__all__ = ["CodeInterpreterResource", "AsyncCodeInterpreterResource"]


class CodeInterpreterResource(SyncAPIResource):
    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CodeInterpreterResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return CodeInterpreterResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CodeInterpreterResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return CodeInterpreterResourceWithStreamingResponse(self)

    def execute(
        self,
        *,
        code: str,
        language: Literal["python"],
        files: Iterable[code_interpreter_execute_params.File] | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExecuteResponse:
        """Executes the given code snippet and returns the output.

        Without a session_id, a
        new session will be created to run the code. If you do pass in a valid
        session_id, the code will be run in that session. This is useful for running
        multiple code snippets in the same environment, because dependencies and similar
        things are persisted between calls to the same session.

        Args:
          code: Code snippet to execute.

          language: Programming language for the code to execute. Currently only supports Python,
              but more will be added.

          files: Files to upload to the session. If present, files will be uploaded before
              executing the given code.

          session_id: Identifier of the current session. Used to make follow-up calls. Requests will
              return an error if the session does not belong to the caller or has expired.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            ExecuteResponse,
            self._post(
                "/tci/execute",
                body=maybe_transform(
                    {
                        "code": code,
                        "language": language,
                        "files": files,
                        "session_id": session_id,
                    },
                    code_interpreter_execute_params.CodeInterpreterExecuteParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ExecuteResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncCodeInterpreterResource(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCodeInterpreterResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncCodeInterpreterResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCodeInterpreterResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncCodeInterpreterResourceWithStreamingResponse(self)

    async def execute(
        self,
        *,
        code: str,
        language: Literal["python"],
        files: Iterable[code_interpreter_execute_params.File] | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExecuteResponse:
        """Executes the given code snippet and returns the output.

        Without a session_id, a
        new session will be created to run the code. If you do pass in a valid
        session_id, the code will be run in that session. This is useful for running
        multiple code snippets in the same environment, because dependencies and similar
        things are persisted between calls to the same session.

        Args:
          code: Code snippet to execute.

          language: Programming language for the code to execute. Currently only supports Python,
              but more will be added.

          files: Files to upload to the session. If present, files will be uploaded before
              executing the given code.

          session_id: Identifier of the current session. Used to make follow-up calls. Requests will
              return an error if the session does not belong to the caller or has expired.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            ExecuteResponse,
            await self._post(
                "/tci/execute",
                body=await async_maybe_transform(
                    {
                        "code": code,
                        "language": language,
                        "files": files,
                        "session_id": session_id,
                    },
                    code_interpreter_execute_params.CodeInterpreterExecuteParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ExecuteResponse),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class CodeInterpreterResourceWithRawResponse:
    def __init__(self, code_interpreter: CodeInterpreterResource) -> None:
        self._code_interpreter = code_interpreter

        self.execute = to_raw_response_wrapper(
            code_interpreter.execute,
        )

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._code_interpreter.sessions)


class AsyncCodeInterpreterResourceWithRawResponse:
    def __init__(self, code_interpreter: AsyncCodeInterpreterResource) -> None:
        self._code_interpreter = code_interpreter

        self.execute = async_to_raw_response_wrapper(
            code_interpreter.execute,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._code_interpreter.sessions)


class CodeInterpreterResourceWithStreamingResponse:
    def __init__(self, code_interpreter: CodeInterpreterResource) -> None:
        self._code_interpreter = code_interpreter

        self.execute = to_streamed_response_wrapper(
            code_interpreter.execute,
        )

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._code_interpreter.sessions)


class AsyncCodeInterpreterResourceWithStreamingResponse:
    def __init__(self, code_interpreter: AsyncCodeInterpreterResource) -> None:
        self._code_interpreter = code_interpreter

        self.execute = async_to_streamed_response_wrapper(
            code_interpreter.execute,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._code_interpreter.sessions)
