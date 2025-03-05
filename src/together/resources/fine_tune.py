# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal

import httpx

from ..types import fine_tune_create_params, fine_tune_download_params
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
from .._base_client import make_request_options
from ..types.fine_tune import FineTune
from ..types.fine_tune_event import FineTuneEvent
from ..types.fine_tune_list_response import FineTuneListResponse
from ..types.fine_tune_download_response import FineTuneDownloadResponse

__all__ = ["FineTuneResource", "AsyncFineTuneResource"]


class FineTuneResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FineTuneResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return FineTuneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTuneResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return FineTuneResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: int | NotGiven = NOT_GIVEN,
        learning_rate: float | NotGiven = NOT_GIVEN,
        lr_scheduler: fine_tune_create_params.LrScheduler | NotGiven = NOT_GIVEN,
        max_grad_norm: float | NotGiven = NOT_GIVEN,
        n_checkpoints: int | NotGiven = NOT_GIVEN,
        n_epochs: int | NotGiven = NOT_GIVEN,
        n_evals: int | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        train_on_inputs: Union[bool, Literal["auto"]] | NotGiven = NOT_GIVEN,
        training_type: fine_tune_create_params.TrainingType | NotGiven = NOT_GIVEN,
        validation_file: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        wandb_base_url: str | NotGiven = NOT_GIVEN,
        wandb_name: str | NotGiven = NOT_GIVEN,
        wandb_project_name: str | NotGiven = NOT_GIVEN,
        warmup_ratio: float | NotGiven = NOT_GIVEN,
        weight_decay: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTune:
        """
        Use a model to create a fine-tuning job.

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a training file uploaded to the Together API

          batch_size: Number of training examples processed together (larger batches use more memory
              but may train faster)

          learning_rate: Controls how quickly the model adapts to new information (too high may cause
              instability, too low may slow convergence)

          max_grad_norm: Max gradient norm to be used for gradient clipping. Set to 0 to disable.

          n_checkpoints: Number of intermediate model versions saved during training for evaluation

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          suffix: Suffix that will be added to your fine-tuned model name

          train_on_inputs: Whether to mask the user messages in conversational data or prompts in
              instruction data.

          validation_file: File-ID of a validation file uploaded to the Together API

          wandb_api_key: Integration key for tracking experiments and model metrics on W&B platform

          wandb_base_url: The base URL of a dedicated Weights & Biases instance.

          wandb_name: The Weights & Biases name for your run.

          wandb_project_name: The Weights & Biases project for your run. If not specified, will use `together`
              as the project name.

          warmup_ratio: The percent of steps at the start of training to linearly increase the learning
              rate.

          weight_decay: Weight decay

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
                    "lr_scheduler": lr_scheduler,
                    "max_grad_norm": max_grad_norm,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "suffix": suffix,
                    "train_on_inputs": train_on_inputs,
                    "training_type": training_type,
                    "validation_file": validation_file,
                    "wandb_api_key": wandb_api_key,
                    "wandb_base_url": wandb_base_url,
                    "wandb_name": wandb_name,
                    "wandb_project_name": wandb_project_name,
                    "warmup_ratio": warmup_ratio,
                    "weight_decay": weight_decay,
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
        List the metadata for a single fine-tuning job.

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
        """List the metadata for all fine-tuning jobs."""
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
        Cancel a currently running fine-tuning job.

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
        checkpoint: Literal["merged", "adapter"] | NotGiven = NOT_GIVEN,
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
        Download a compressed fine-tuned model or checkpoint to local disk.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint: Specifies checkpoint type to download - `merged` vs `adapter`. This field is
              required if the checkpoint_step is not set.

          checkpoint_step: Specifies step number for checkpoint to download. Ignores `checkpoint` value if
              set.

          output: Specifies output file name for downloaded model. Defaults to
              `$PWD/{model_name}.{extension}`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/finetune/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ft_id": ft_id,
                        "checkpoint": checkpoint,
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
    ) -> FineTuneEvent:
        """
        List the events for a single fine-tuning job.

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
            cast_to=FineTuneEvent,
        )


class AsyncFineTuneResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFineTuneResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncFineTuneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTuneResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncFineTuneResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: int | NotGiven = NOT_GIVEN,
        learning_rate: float | NotGiven = NOT_GIVEN,
        lr_scheduler: fine_tune_create_params.LrScheduler | NotGiven = NOT_GIVEN,
        max_grad_norm: float | NotGiven = NOT_GIVEN,
        n_checkpoints: int | NotGiven = NOT_GIVEN,
        n_epochs: int | NotGiven = NOT_GIVEN,
        n_evals: int | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        train_on_inputs: Union[bool, Literal["auto"]] | NotGiven = NOT_GIVEN,
        training_type: fine_tune_create_params.TrainingType | NotGiven = NOT_GIVEN,
        validation_file: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        wandb_base_url: str | NotGiven = NOT_GIVEN,
        wandb_name: str | NotGiven = NOT_GIVEN,
        wandb_project_name: str | NotGiven = NOT_GIVEN,
        warmup_ratio: float | NotGiven = NOT_GIVEN,
        weight_decay: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTune:
        """
        Use a model to create a fine-tuning job.

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a training file uploaded to the Together API

          batch_size: Number of training examples processed together (larger batches use more memory
              but may train faster)

          learning_rate: Controls how quickly the model adapts to new information (too high may cause
              instability, too low may slow convergence)

          max_grad_norm: Max gradient norm to be used for gradient clipping. Set to 0 to disable.

          n_checkpoints: Number of intermediate model versions saved during training for evaluation

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          suffix: Suffix that will be added to your fine-tuned model name

          train_on_inputs: Whether to mask the user messages in conversational data or prompts in
              instruction data.

          validation_file: File-ID of a validation file uploaded to the Together API

          wandb_api_key: Integration key for tracking experiments and model metrics on W&B platform

          wandb_base_url: The base URL of a dedicated Weights & Biases instance.

          wandb_name: The Weights & Biases name for your run.

          wandb_project_name: The Weights & Biases project for your run. If not specified, will use `together`
              as the project name.

          warmup_ratio: The percent of steps at the start of training to linearly increase the learning
              rate.

          weight_decay: Weight decay

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
                    "lr_scheduler": lr_scheduler,
                    "max_grad_norm": max_grad_norm,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "suffix": suffix,
                    "train_on_inputs": train_on_inputs,
                    "training_type": training_type,
                    "validation_file": validation_file,
                    "wandb_api_key": wandb_api_key,
                    "wandb_base_url": wandb_base_url,
                    "wandb_name": wandb_name,
                    "wandb_project_name": wandb_project_name,
                    "warmup_ratio": warmup_ratio,
                    "weight_decay": weight_decay,
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
        List the metadata for a single fine-tuning job.

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
        """List the metadata for all fine-tuning jobs."""
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
        Cancel a currently running fine-tuning job.

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
        checkpoint: Literal["merged", "adapter"] | NotGiven = NOT_GIVEN,
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
        Download a compressed fine-tuned model or checkpoint to local disk.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint: Specifies checkpoint type to download - `merged` vs `adapter`. This field is
              required if the checkpoint_step is not set.

          checkpoint_step: Specifies step number for checkpoint to download. Ignores `checkpoint` value if
              set.

          output: Specifies output file name for downloaded model. Defaults to
              `$PWD/{model_name}.{extension}`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/finetune/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "ft_id": ft_id,
                        "checkpoint": checkpoint,
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
    ) -> FineTuneEvent:
        """
        List the events for a single fine-tuning job.

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
            cast_to=FineTuneEvent,
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
