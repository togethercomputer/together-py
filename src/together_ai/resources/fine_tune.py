# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    FineTune,
    FineTuneListResponse,
    FineTuneDownloadResponse,
    FineTuneListEventsResponse,
    fine_tune_create_params,
    fine_tune_download_params,
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

__all__ = ["FineTuneResource", "AsyncFineTuneResource"]


class FineTuneResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FineTuneResourceWithRawResponse:
        return FineTuneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTuneResourceWithStreamingResponse:
        return FineTuneResourceWithStreamingResponse(self)

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
    ) -> FineTune:
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
            cast_to=FineTune,
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
    ) -> FineTune:
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
            cast_to=FineTune,
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
    ) -> FineTune:
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
            cast_to=FineTune,
        )

    def download(
        self,
        *,
        ft_id: str,
        checkpoint_step: int | NotGiven = NOT_GIVEN,
        output: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneDownloadResponse:
        """
        Downloads a compressed fine-tuned model or checkpoint to local disk.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint_step: Specifies step number for checkpoint to download. Defaults to -1 (download the
              final model).

          output: Specifies output file name for downloaded model. Defaults to
              `$PWD/{model_name}.{extension}`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/fine-tunes/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ft_id": ft_id,
                        "checkpoint_step": checkpoint_step,
                        "output": output,
                    },
                    fine_tune_download_params.FineTuneDownloadParams,
                ),
            ),
            cast_to=FineTuneDownloadResponse,
        )

    def list_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneListEventsResponse:
        """
        List events of a fine-tune job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/fine-tunes/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneListEventsResponse,
        )


class AsyncFineTuneResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFineTuneResourceWithRawResponse:
        return AsyncFineTuneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTuneResourceWithStreamingResponse:
        return AsyncFineTuneResourceWithStreamingResponse(self)

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
    ) -> FineTune:
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
            cast_to=FineTune,
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
    ) -> FineTune:
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
            cast_to=FineTune,
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
    ) -> FineTune:
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
            cast_to=FineTune,
        )

    async def download(
        self,
        *,
        ft_id: str,
        checkpoint_step: int | NotGiven = NOT_GIVEN,
        output: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneDownloadResponse:
        """
        Downloads a compressed fine-tuned model or checkpoint to local disk.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint_step: Specifies step number for checkpoint to download. Defaults to -1 (download the
              final model).

          output: Specifies output file name for downloaded model. Defaults to
              `$PWD/{model_name}.{extension}`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/fine-tunes/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "ft_id": ft_id,
                        "checkpoint_step": checkpoint_step,
                        "output": output,
                    },
                    fine_tune_download_params.FineTuneDownloadParams,
                ),
            ),
            cast_to=FineTuneDownloadResponse,
        )

    async def list_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneListEventsResponse:
        """
        List events of a fine-tune job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/fine-tunes/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneListEventsResponse,
        )


class FineTuneResourceWithRawResponse:
    def __init__(self, fine_tune: FineTuneResource) -> None:
        self._fine_tune = fine_tune

        self.create = to_raw_response_wrapper(
            fine_tune.create,
        )
        self.retrieve = to_raw_response_wrapper(
            fine_tune.retrieve,
        )
        self.list = to_raw_response_wrapper(
            fine_tune.list,
        )
        self.cancel = to_raw_response_wrapper(
            fine_tune.cancel,
        )
        self.download = to_raw_response_wrapper(
            fine_tune.download,
        )
        self.list_events = to_raw_response_wrapper(
            fine_tune.list_events,
        )


class AsyncFineTuneResourceWithRawResponse:
    def __init__(self, fine_tune: AsyncFineTuneResource) -> None:
        self._fine_tune = fine_tune

        self.create = async_to_raw_response_wrapper(
            fine_tune.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            fine_tune.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            fine_tune.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            fine_tune.cancel,
        )
        self.download = async_to_raw_response_wrapper(
            fine_tune.download,
        )
        self.list_events = async_to_raw_response_wrapper(
            fine_tune.list_events,
        )


class FineTuneResourceWithStreamingResponse:
    def __init__(self, fine_tune: FineTuneResource) -> None:
        self._fine_tune = fine_tune

        self.create = to_streamed_response_wrapper(
            fine_tune.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            fine_tune.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            fine_tune.list,
        )
        self.cancel = to_streamed_response_wrapper(
            fine_tune.cancel,
        )
        self.download = to_streamed_response_wrapper(
            fine_tune.download,
        )
        self.list_events = to_streamed_response_wrapper(
            fine_tune.list_events,
        )


class AsyncFineTuneResourceWithStreamingResponse:
    def __init__(self, fine_tune: AsyncFineTuneResource) -> None:
        self._fine_tune = fine_tune

        self.create = async_to_streamed_response_wrapper(
            fine_tune.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            fine_tune.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            fine_tune.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            fine_tune.cancel,
        )
        self.download = async_to_streamed_response_wrapper(
            fine_tune.download,
        )
        self.list_events = async_to_streamed_response_wrapper(
            fine_tune.list_events,
        )
