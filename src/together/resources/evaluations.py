# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import evaluation_list_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.evaluation_list_response import EvaluationListResponse
from ..types.evaluation_retrieve_response import EvaluationRetrieveResponse
from ..types.evaluation_get_status_response import EvaluationGetStatusResponse
from ..types.evaluation_get_allowed_models_response import EvaluationGetAllowedModelsResponse

__all__ = ["EvaluationsResource", "AsyncEvaluationsResource"]


class EvaluationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return EvaluationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return EvaluationsResourceWithStreamingResponse(self)

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
    ) -> EvaluationRetrieveResponse:
        """
        Get details of a specific evaluation job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/evaluation/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationRetrieveResponse,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        status: Literal["pending", "queued", "running", "completed", "error", "user_error"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationListResponse:
        """
        Get a list of evaluation jobs with optional filtering

        Args:
          limit: Maximum number of results to return (max 100)

          status: Filter by job status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/evaluations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "status": status,
                    },
                    evaluation_list_params.EvaluationListParams,
                ),
            ),
            cast_to=EvaluationListResponse,
        )

    def get_allowed_models(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationGetAllowedModelsResponse:
        """Get the list of models that are allowed for evaluation"""
        return self._get(
            "/evaluations/model-list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationGetAllowedModelsResponse,
        )

    def get_status(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationGetStatusResponse:
        """
        Get the status and results of a specific evaluation job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/evaluation/{id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationGetStatusResponse,
        )


class AsyncEvaluationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncEvaluationsResourceWithStreamingResponse(self)

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
    ) -> EvaluationRetrieveResponse:
        """
        Get details of a specific evaluation job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/evaluation/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationRetrieveResponse,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        status: Literal["pending", "queued", "running", "completed", "error", "user_error"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationListResponse:
        """
        Get a list of evaluation jobs with optional filtering

        Args:
          limit: Maximum number of results to return (max 100)

          status: Filter by job status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/evaluations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "status": status,
                    },
                    evaluation_list_params.EvaluationListParams,
                ),
            ),
            cast_to=EvaluationListResponse,
        )

    async def get_allowed_models(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationGetAllowedModelsResponse:
        """Get the list of models that are allowed for evaluation"""
        return await self._get(
            "/evaluations/model-list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationGetAllowedModelsResponse,
        )

    async def get_status(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluationGetStatusResponse:
        """
        Get the status and results of a specific evaluation job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/evaluation/{id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationGetStatusResponse,
        )


class EvaluationsResourceWithRawResponse:
    def __init__(self, evaluations: EvaluationsResource) -> None:
        self._evaluations = evaluations

        self.retrieve = to_raw_response_wrapper(
            evaluations.retrieve,
        )
        self.list = to_raw_response_wrapper(
            evaluations.list,
        )
        self.get_allowed_models = to_raw_response_wrapper(
            evaluations.get_allowed_models,
        )
        self.get_status = to_raw_response_wrapper(
            evaluations.get_status,
        )


class AsyncEvaluationsResourceWithRawResponse:
    def __init__(self, evaluations: AsyncEvaluationsResource) -> None:
        self._evaluations = evaluations

        self.retrieve = async_to_raw_response_wrapper(
            evaluations.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            evaluations.list,
        )
        self.get_allowed_models = async_to_raw_response_wrapper(
            evaluations.get_allowed_models,
        )
        self.get_status = async_to_raw_response_wrapper(
            evaluations.get_status,
        )


class EvaluationsResourceWithStreamingResponse:
    def __init__(self, evaluations: EvaluationsResource) -> None:
        self._evaluations = evaluations

        self.retrieve = to_streamed_response_wrapper(
            evaluations.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            evaluations.list,
        )
        self.get_allowed_models = to_streamed_response_wrapper(
            evaluations.get_allowed_models,
        )
        self.get_status = to_streamed_response_wrapper(
            evaluations.get_status,
        )


class AsyncEvaluationsResourceWithStreamingResponse:
    def __init__(self, evaluations: AsyncEvaluationsResource) -> None:
        self._evaluations = evaluations

        self.retrieve = async_to_streamed_response_wrapper(
            evaluations.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluations.list,
        )
        self.get_allowed_models = async_to_streamed_response_wrapper(
            evaluations.get_allowed_models,
        )
        self.get_status = async_to_streamed_response_wrapper(
            evaluations.get_status,
        )
