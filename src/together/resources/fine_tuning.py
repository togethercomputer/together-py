# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal

import httpx

from ..types import fine_tuning_create_params, fine_tuning_delete_params, fine_tuning_download_params
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
from ..types.fine_tune import FineTune
from ..types.lr_scheduler_param import LrSchedulerParam
from ..types.fine_tuning_list_response import FineTuningListResponse
from ..types.fine_tuning_cancel_response import FineTuningCancelResponse
from ..types.fine_tuning_create_response import FineTuningCreateResponse
from ..types.fine_tuning_delete_response import FineTuningDeleteResponse
from ..types.fine_tuning_download_response import FineTuningDownloadResponse
from ..types.fine_tuning_list_events_response import FineTuningListEventsResponse
from ..types.fine_tuning_retrieve_checkpoints_response import FineTuningRetrieveCheckpointsResponse

__all__ = ["FineTuningResource", "AsyncFineTuningResource"]


class FineTuningResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FineTuningResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return FineTuningResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTuningResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return FineTuningResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: Union[int, Literal["max"]] | Omit = omit,
        from_checkpoint: str | Omit = omit,
        from_hf_model: str | Omit = omit,
        hf_api_token: str | Omit = omit,
        hf_model_revision: str | Omit = omit,
        hf_output_repo_name: str | Omit = omit,
        learning_rate: float | Omit = omit,
        lr_scheduler: LrSchedulerParam | Omit = omit,
        max_grad_norm: float | Omit = omit,
        n_checkpoints: int | Omit = omit,
        n_epochs: int | Omit = omit,
        n_evals: int | Omit = omit,
        suffix: str | Omit = omit,
        train_on_inputs: Union[bool, Literal["auto"]] | Omit = omit,
        training_method: fine_tuning_create_params.TrainingMethod | Omit = omit,
        training_type: fine_tuning_create_params.TrainingType | Omit = omit,
        validation_file: str | Omit = omit,
        wandb_api_key: str | Omit = omit,
        wandb_base_url: str | Omit = omit,
        wandb_name: str | Omit = omit,
        wandb_project_name: str | Omit = omit,
        warmup_ratio: float | Omit = omit,
        weight_decay: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningCreateResponse:
        """
        Create a fine-tuning job with the provided model and training data.

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a training file uploaded to the Together API

          batch_size: Number of training examples processed together (larger batches use more memory
              but may train faster). Defaults to "max". We use training optimizations like
              packing, so the effective batch size may be different than the value you set.

          from_checkpoint: The checkpoint identifier to continue training from a previous fine-tuning job.
              Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
              `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
              final checkpoint will be used.

          from_hf_model: The Hugging Face Hub repo to start training from. Should be as close as possible
              to the base model (specified by the `model` argument) in terms of architecture
              and size.

          hf_api_token: The API token for the Hugging Face Hub.

          hf_model_revision: The revision of the Hugging Face Hub model to continue training from. E.g.,
              hf_model_revision=main (default, used if the argument is not provided) or
              hf_model_revision='607a30d783dfa663caf39e06633721c8d4cfcd7e' (specific commit).

          hf_output_repo_name: The name of the Hugging Face repository to upload the fine-tuned model to.

          learning_rate: Controls how quickly the model adapts to new information (too high may cause
              instability, too low may slow convergence)

          lr_scheduler: The learning rate scheduler to use. It specifies how the learning rate is
              adjusted during training.

          max_grad_norm: Max gradient norm to be used for gradient clipping. Set to 0 to disable.

          n_checkpoints: Number of intermediate model versions saved during training for evaluation

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          suffix: Suffix that will be added to your fine-tuned model name

          train_on_inputs: Whether to mask the user messages in conversational data or prompts in
              instruction data.

          training_method: The training method to use. 'sft' for Supervised Fine-Tuning or 'dpo' for Direct
              Preference Optimization.

          validation_file: File-ID of a validation file uploaded to the Together API

          wandb_api_key: Integration key for tracking experiments and model metrics on W&B platform

          wandb_base_url: The base URL of a dedicated Weights & Biases instance.

          wandb_name: The Weights & Biases name for your run.

          wandb_project_name: The Weights & Biases project for your run. If not specified, will use `together`
              as the project name.

          warmup_ratio: The percent of steps at the start of training to linearly increase the learning
              rate.

          weight_decay: Weight decay. Regularization parameter for the optimizer.

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
                    "from_checkpoint": from_checkpoint,
                    "from_hf_model": from_hf_model,
                    "hf_api_token": hf_api_token,
                    "hf_model_revision": hf_model_revision,
                    "hf_output_repo_name": hf_output_repo_name,
                    "learning_rate": learning_rate,
                    "lr_scheduler": lr_scheduler,
                    "max_grad_norm": max_grad_norm,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "suffix": suffix,
                    "train_on_inputs": train_on_inputs,
                    "training_method": training_method,
                    "training_type": training_type,
                    "validation_file": validation_file,
                    "wandb_api_key": wandb_api_key,
                    "wandb_base_url": wandb_base_url,
                    "wandb_name": wandb_name,
                    "wandb_project_name": wandb_project_name,
                    "warmup_ratio": warmup_ratio,
                    "weight_decay": weight_decay,
                },
                fine_tuning_create_params.FineTuningCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningCreateResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListResponse:
        """List the metadata for all fine-tuning jobs.

        Returns a list of
        FinetuneResponseTruncated objects.
        """
        return self._get(
            "/fine-tunes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        force: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningDeleteResponse:
        """
        Delete a fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/fine-tunes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"force": force}, fine_tuning_delete_params.FineTuningDeleteParams),
            ),
            cast_to=FineTuningDeleteResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningCancelResponse:
        """Cancel a currently running fine-tuning job.

        Returns a FinetuneResponseTruncated
        object.

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
            cast_to=FineTuningCancelResponse,
        )

    def download(
        self,
        *,
        ft_id: str,
        checkpoint: Literal["merged", "adapter"] | Omit = omit,
        checkpoint_step: int | Omit = omit,
        output: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningDownloadResponse:
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
                    fine_tuning_download_params.FineTuningDownloadParams,
                ),
            ),
            cast_to=FineTuningDownloadResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListEventsResponse:
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
            cast_to=FineTuningListEventsResponse,
        )

    def retrieve_checkpoints(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningRetrieveCheckpointsResponse:
        """
        List the checkpoints for a single fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/fine-tunes/{id}/checkpoints",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningRetrieveCheckpointsResponse,
        )


class AsyncFineTuningResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFineTuningResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncFineTuningResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTuningResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncFineTuningResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        training_file: str,
        batch_size: Union[int, Literal["max"]] | Omit = omit,
        from_checkpoint: str | Omit = omit,
        from_hf_model: str | Omit = omit,
        hf_api_token: str | Omit = omit,
        hf_model_revision: str | Omit = omit,
        hf_output_repo_name: str | Omit = omit,
        learning_rate: float | Omit = omit,
        lr_scheduler: LrSchedulerParam | Omit = omit,
        max_grad_norm: float | Omit = omit,
        n_checkpoints: int | Omit = omit,
        n_epochs: int | Omit = omit,
        n_evals: int | Omit = omit,
        suffix: str | Omit = omit,
        train_on_inputs: Union[bool, Literal["auto"]] | Omit = omit,
        training_method: fine_tuning_create_params.TrainingMethod | Omit = omit,
        training_type: fine_tuning_create_params.TrainingType | Omit = omit,
        validation_file: str | Omit = omit,
        wandb_api_key: str | Omit = omit,
        wandb_base_url: str | Omit = omit,
        wandb_name: str | Omit = omit,
        wandb_project_name: str | Omit = omit,
        warmup_ratio: float | Omit = omit,
        weight_decay: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningCreateResponse:
        """
        Create a fine-tuning job with the provided model and training data.

        Args:
          model: Name of the base model to run fine-tune job on

          training_file: File-ID of a training file uploaded to the Together API

          batch_size: Number of training examples processed together (larger batches use more memory
              but may train faster). Defaults to "max". We use training optimizations like
              packing, so the effective batch size may be different than the value you set.

          from_checkpoint: The checkpoint identifier to continue training from a previous fine-tuning job.
              Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
              `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
              final checkpoint will be used.

          from_hf_model: The Hugging Face Hub repo to start training from. Should be as close as possible
              to the base model (specified by the `model` argument) in terms of architecture
              and size.

          hf_api_token: The API token for the Hugging Face Hub.

          hf_model_revision: The revision of the Hugging Face Hub model to continue training from. E.g.,
              hf_model_revision=main (default, used if the argument is not provided) or
              hf_model_revision='607a30d783dfa663caf39e06633721c8d4cfcd7e' (specific commit).

          hf_output_repo_name: The name of the Hugging Face repository to upload the fine-tuned model to.

          learning_rate: Controls how quickly the model adapts to new information (too high may cause
              instability, too low may slow convergence)

          lr_scheduler: The learning rate scheduler to use. It specifies how the learning rate is
              adjusted during training.

          max_grad_norm: Max gradient norm to be used for gradient clipping. Set to 0 to disable.

          n_checkpoints: Number of intermediate model versions saved during training for evaluation

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          suffix: Suffix that will be added to your fine-tuned model name

          train_on_inputs: Whether to mask the user messages in conversational data or prompts in
              instruction data.

          training_method: The training method to use. 'sft' for Supervised Fine-Tuning or 'dpo' for Direct
              Preference Optimization.

          validation_file: File-ID of a validation file uploaded to the Together API

          wandb_api_key: Integration key for tracking experiments and model metrics on W&B platform

          wandb_base_url: The base URL of a dedicated Weights & Biases instance.

          wandb_name: The Weights & Biases name for your run.

          wandb_project_name: The Weights & Biases project for your run. If not specified, will use `together`
              as the project name.

          warmup_ratio: The percent of steps at the start of training to linearly increase the learning
              rate.

          weight_decay: Weight decay. Regularization parameter for the optimizer.

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
                    "from_checkpoint": from_checkpoint,
                    "from_hf_model": from_hf_model,
                    "hf_api_token": hf_api_token,
                    "hf_model_revision": hf_model_revision,
                    "hf_output_repo_name": hf_output_repo_name,
                    "learning_rate": learning_rate,
                    "lr_scheduler": lr_scheduler,
                    "max_grad_norm": max_grad_norm,
                    "n_checkpoints": n_checkpoints,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "suffix": suffix,
                    "train_on_inputs": train_on_inputs,
                    "training_method": training_method,
                    "training_type": training_type,
                    "validation_file": validation_file,
                    "wandb_api_key": wandb_api_key,
                    "wandb_base_url": wandb_base_url,
                    "wandb_name": wandb_name,
                    "wandb_project_name": wandb_project_name,
                    "warmup_ratio": warmup_ratio,
                    "weight_decay": weight_decay,
                },
                fine_tuning_create_params.FineTuningCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningCreateResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListResponse:
        """List the metadata for all fine-tuning jobs.

        Returns a list of
        FinetuneResponseTruncated objects.
        """
        return await self._get(
            "/fine-tunes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        force: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningDeleteResponse:
        """
        Delete a fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/fine-tunes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"force": force}, fine_tuning_delete_params.FineTuningDeleteParams),
            ),
            cast_to=FineTuningDeleteResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningCancelResponse:
        """Cancel a currently running fine-tuning job.

        Returns a FinetuneResponseTruncated
        object.

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
            cast_to=FineTuningCancelResponse,
        )

    async def download(
        self,
        *,
        ft_id: str,
        checkpoint: Literal["merged", "adapter"] | Omit = omit,
        checkpoint_step: int | Omit = omit,
        output: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningDownloadResponse:
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
                    fine_tuning_download_params.FineTuningDownloadParams,
                ),
            ),
            cast_to=FineTuningDownloadResponse,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListEventsResponse:
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
            cast_to=FineTuningListEventsResponse,
        )

    async def retrieve_checkpoints(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningRetrieveCheckpointsResponse:
        """
        List the checkpoints for a single fine-tuning job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/fine-tunes/{id}/checkpoints",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningRetrieveCheckpointsResponse,
        )


class FineTuningResourceWithRawResponse:
    def __init__(self, fine_tuning: FineTuningResource) -> None:
        self._fine_tuning = fine_tuning

        self.create = to_raw_response_wrapper(
            fine_tuning.create,
        )
        self.retrieve = to_raw_response_wrapper(
            fine_tuning.retrieve,
        )
        self.list = to_raw_response_wrapper(
            fine_tuning.list,
        )
        self.delete = to_raw_response_wrapper(
            fine_tuning.delete,
        )
        self.cancel = to_raw_response_wrapper(
            fine_tuning.cancel,
        )
        self.download = to_raw_response_wrapper(
            fine_tuning.download,
        )
        self.list_events = to_raw_response_wrapper(
            fine_tuning.list_events,
        )
        self.retrieve_checkpoints = to_raw_response_wrapper(
            fine_tuning.retrieve_checkpoints,
        )


class AsyncFineTuningResourceWithRawResponse:
    def __init__(self, fine_tuning: AsyncFineTuningResource) -> None:
        self._fine_tuning = fine_tuning

        self.create = async_to_raw_response_wrapper(
            fine_tuning.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            fine_tuning.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            fine_tuning.list,
        )
        self.delete = async_to_raw_response_wrapper(
            fine_tuning.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            fine_tuning.cancel,
        )
        self.download = async_to_raw_response_wrapper(
            fine_tuning.download,
        )
        self.list_events = async_to_raw_response_wrapper(
            fine_tuning.list_events,
        )
        self.retrieve_checkpoints = async_to_raw_response_wrapper(
            fine_tuning.retrieve_checkpoints,
        )


class FineTuningResourceWithStreamingResponse:
    def __init__(self, fine_tuning: FineTuningResource) -> None:
        self._fine_tuning = fine_tuning

        self.create = to_streamed_response_wrapper(
            fine_tuning.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            fine_tuning.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            fine_tuning.list,
        )
        self.delete = to_streamed_response_wrapper(
            fine_tuning.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            fine_tuning.cancel,
        )
        self.download = to_streamed_response_wrapper(
            fine_tuning.download,
        )
        self.list_events = to_streamed_response_wrapper(
            fine_tuning.list_events,
        )
        self.retrieve_checkpoints = to_streamed_response_wrapper(
            fine_tuning.retrieve_checkpoints,
        )


class AsyncFineTuningResourceWithStreamingResponse:
    def __init__(self, fine_tuning: AsyncFineTuningResource) -> None:
        self._fine_tuning = fine_tuning

        self.create = async_to_streamed_response_wrapper(
            fine_tuning.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            fine_tuning.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            fine_tuning.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            fine_tuning.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            fine_tuning.cancel,
        )
        self.download = async_to_streamed_response_wrapper(
            fine_tuning.download,
        )
        self.list_events = async_to_streamed_response_wrapper(
            fine_tuning.list_events,
        )
        self.retrieve_checkpoints = async_to_streamed_response_wrapper(
            fine_tuning.retrieve_checkpoints,
        )
