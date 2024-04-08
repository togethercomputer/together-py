# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    FineTuneListResponse,
    FineTuneCancelResponse,
    FineTuneCreateResponse,
    FineTuneRetrieveResponse,
    fine_tune_create_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import (
    make_request_options,
)

__all__ = ["FineTunes", "AsyncFineTunes"]


class FineTunes(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FineTunesWithRawResponse:
        return FineTunesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTunesWithStreamingResponse:
        return FineTunesWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: int | NotGiven = NOT_GIVEN,
        learning_rate: float | NotGiven = NOT_GIVEN,
        n_checkpoints: int | NotGiven = NOT_GIVEN,
        n_epochs: int | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneCreateResponse:
        """
        Create a fine-tuning job

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a file uploaded to the Together API

          batch_size: Batch size for fine-tuning

          learning_rate: Learning rate multiplier to use for training

          n_checkpoints: Number of checkpoints to save during fine-tuning

          n_epochs: Number of epochs for fine-tuning

          suffix: Suffix that will be added to your fine-tuned model name

          wandb_api_key: API key for Weights & Biases integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/fine-tunes",
            body=maybe_transform(
                {
                    "model": model,
                    "training_file": training_file,
                    "batch_size": batch_size,
                    "learning_rate": learning_rate,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "suffix": suffix,
                    "wandb_api_key": wandb_api_key,
                },
                fine_tune_create_params.FineTuneCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneRetrieveResponse:
        """
        Retrieve fine-tune job details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/fine-tunes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneListResponse:
        """List fine-tune job history"""
        return self._get(
            "/fine-tunes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneListResponse,
        )

    def cancel(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneCancelResponse:
        """
        Cancels a running fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/fine-tunes/{id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneCancelResponse,
        )


class AsyncFineTunes(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFineTunesWithRawResponse:
        return AsyncFineTunesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTunesWithStreamingResponse:
        return AsyncFineTunesWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: int | NotGiven = NOT_GIVEN,
        learning_rate: float | NotGiven = NOT_GIVEN,
        n_checkpoints: int | NotGiven = NOT_GIVEN,
        n_epochs: int | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneCreateResponse:
        """
        Create a fine-tuning job

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a file uploaded to the Together API

          batch_size: Batch size for fine-tuning

          learning_rate: Learning rate multiplier to use for training

          n_checkpoints: Number of checkpoints to save during fine-tuning

          n_epochs: Number of epochs for fine-tuning

          suffix: Suffix that will be added to your fine-tuned model name

          wandb_api_key: API key for Weights & Biases integration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/fine-tunes",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "training_file": training_file,
                    "batch_size": batch_size,
                    "learning_rate": learning_rate,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "suffix": suffix,
                    "wandb_api_key": wandb_api_key,
                },
                fine_tune_create_params.FineTuneCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneRetrieveResponse:
        """
        Retrieve fine-tune job details

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/fine-tunes/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneListResponse:
        """List fine-tune job history"""
        return await self._get(
            "/fine-tunes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneListResponse,
        )

    async def cancel(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneCancelResponse:
        """
        Cancels a running fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/fine-tunes/{id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneCancelResponse,
        )


class FineTunesWithRawResponse:
    def __init__(self, fine_tunes: FineTunes) -> None:
        self._fine_tunes = fine_tunes

        self.create = to_raw_response_wrapper(
            fine_tunes.create,
        )
        self.retrieve = to_raw_response_wrapper(
            fine_tunes.retrieve,
        )
        self.list = to_raw_response_wrapper(
            fine_tunes.list,
        )
        self.cancel = to_raw_response_wrapper(
            fine_tunes.cancel,
        )


class AsyncFineTunesWithRawResponse:
    def __init__(self, fine_tunes: AsyncFineTunes) -> None:
        self._fine_tunes = fine_tunes

        self.create = async_to_raw_response_wrapper(
            fine_tunes.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            fine_tunes.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            fine_tunes.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            fine_tunes.cancel,
        )


class FineTunesWithStreamingResponse:
    def __init__(self, fine_tunes: FineTunes) -> None:
        self._fine_tunes = fine_tunes

        self.create = to_streamed_response_wrapper(
            fine_tunes.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            fine_tunes.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            fine_tunes.list,
        )
        self.cancel = to_streamed_response_wrapper(
            fine_tunes.cancel,
        )


class AsyncFineTunesWithStreamingResponse:
    def __init__(self, fine_tunes: AsyncFineTunes) -> None:
        self._fine_tunes = fine_tunes

        self.create = async_to_streamed_response_wrapper(
            fine_tunes.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            fine_tunes.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            fine_tunes.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            fine_tunes.cancel,
        )
