# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx
from rich import print as rprint

from ..types import fine_tuning_delete_params, fine_tuning_content_params, fine_tuning_estimate_price_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..lib.types.fine_tuning import (
    FinetuneResponse as FinetuneResponseLib,
    FinetuneTrainingLimits,
)
from ..types.finetune_response import FinetuneResponse
from ..lib.resources.fine_tuning import (
    get_model_limits,
    async_get_model_limits,
    create_finetune_request,
)
from ..types.fine_tuning_list_response import FineTuningListResponse
from ..types.fine_tuning_cancel_response import FineTuningCancelResponse
from ..types.fine_tuning_delete_response import FineTuningDeleteResponse
from ..types.fine_tuning_list_events_response import FineTuningListEventsResponse
from ..types.fine_tuning_estimate_price_response import FineTuningEstimatePriceResponse
from ..types.fine_tuning_list_checkpoints_response import FineTuningListCheckpointsResponse

__all__ = ["FineTuningResource", "AsyncFineTuningResource"]

_WARNING_MESSAGE_INSUFFICIENT_FUNDS = (
    "The estimated price of the fine-tuning job is {} which is significantly "
    "greater than your current credit limit and balance combined. "
    "It will likely get cancelled due to insufficient funds. "
    "Proceed at your own risk."
)


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
        training_file: str,
        model: str | None = None,
        n_epochs: int = 1,
        validation_file: str | None = "",
        n_evals: int | None = 0,
        n_checkpoints: int | None = 1,
        batch_size: int | Literal["max"] = "max",
        learning_rate: float | None = 0.00001,
        lr_scheduler_type: Literal["linear", "cosine"] = "cosine",
        min_lr_ratio: float = 0.0,
        scheduler_num_cycles: float = 0.5,
        warmup_ratio: float = 0.0,
        max_grad_norm: float = 1.0,
        weight_decay: float = 0.0,
        lora: bool = True,
        lora_r: int | None = None,
        lora_dropout: float | None = 0,
        lora_alpha: float | None = None,
        lora_trainable_modules: str | None = "all-linear",
        train_vision: bool = False,
        suffix: str | None = None,
        wandb_api_key: str | None = None,
        wandb_base_url: str | None = None,
        wandb_project_name: str | None = None,
        wandb_name: str | None = None,
        verbose: bool = False,
        model_limits: FinetuneTrainingLimits | None = None,
        train_on_inputs: bool | Literal["auto"] | None = None,
        training_method: str = "sft",
        dpo_beta: float | None = None,
        dpo_normalize_logratios_by_length: bool = False,
        rpo_alpha: float | None = None,
        simpo_gamma: float | None = None,
        from_checkpoint: str | None = None,
        from_hf_model: str | None = None,
        hf_model_revision: str | None = None,
        hf_api_token: str | None = None,
        hf_output_repo_name: str | None = None,
    ) -> FinetuneResponseLib:
        """
        Method to initiate a fine-tuning job

        Args:
            training_file (str): File-ID of a file uploaded to the Together API
            model (str, optional): Name of the base model to run fine-tune job on
            n_epochs (int, optional): Number of epochs for fine-tuning. Defaults to 1.
            validation file (str, optional): File ID of a file uploaded to the Together API for validation.
            n_evals (int, optional): Number of evaluation loops to run. Defaults to 0.
            n_checkpoints (int, optional): Number of checkpoints to save during fine-tuning.
                Defaults to 1.
            batch_size (int or "max"): Batch size for fine-tuning. Defaults to max.
            learning_rate (float, optional): Learning rate multiplier to use for training
                Defaults to 0.00001.
            lr_scheduler_type (Literal["linear", "cosine"]): Learning rate scheduler type. Defaults to "cosine".
            min_lr_ratio (float, optional): Min learning rate ratio of the initial learning rate for
                the learning rate scheduler. Defaults to 0.0.
            scheduler_num_cycles (float, optional): Number or fraction of cycles for the cosine learning rate scheduler. Defaults to 0.5.
            warmup_ratio (float, optional): Warmup ratio for the learning rate scheduler.
            max_grad_norm (float, optional): Max gradient norm. Defaults to 1.0, set to 0 to disable.
            weight_decay (float, optional): Weight decay. Defaults to 0.0.
            lora (bool, optional): Whether to use LoRA adapters. Defaults to True.
            lora_r (int, optional): Rank of LoRA adapters. Defaults to 8.
            lora_dropout (float, optional): Dropout rate for LoRA adapters. Defaults to 0.
            lora_alpha (float, optional): Alpha for LoRA adapters. Defaults to 8.
            lora_trainable_modules (str, optional): Trainable modules for LoRA adapters. Defaults to "all-linear".
            train_vision (bool, optional): Whether to train the vision encoder (Only for multimodal models). Defaults to False.
            suffix (str, optional): Up to 40 character suffix that will be added to your fine-tuned model name.
                Defaults to None.
            wandb_api_key (str, optional): API key for Weights & Biases integration.
                Defaults to None.
            wandb_base_url (str, optional): Base URL for Weights & Biases integration.
                Defaults to None.
            wandb_project_name (str, optional): Project name for Weights & Biases integration.
                Defaults to None.
            wandb_name (str, optional): Run name for Weights & Biases integration.
                Defaults to None.
            verbose (bool, optional): whether to print the job parameters before submitting a request.
                Defaults to False.
            model_limits (FinetuneTrainingLimits, optional): Limits for the hyperparameters the model in Fine-tuning.
                Defaults to None.
            train_on_inputs (bool or "auto", optional): Whether to mask the user messages in conversational data or prompts in instruction data.
                "auto" will automatically determine whether to mask the inputs based on the data format.
                For datasets with the "text" field (general format), inputs will not be masked.
                For datasets with the "messages" field (conversational format) or "prompt" and "completion" fields
                (Instruction format), inputs will be masked.
                Defaults to None, or "auto" if training_method is "sft" (set in create_finetune_request).
            training_method (str, optional): Training method. Defaults to "sft".
                Supported methods: "sft", "dpo".
            dpo_beta (float, optional): DPO beta parameter. Defaults to None.
            dpo_normalize_logratios_by_length (bool): Whether or not normalize logratios by sample length. Defaults to False,
            rpo_alpha (float, optional): RPO alpha parameter of DPO training to include NLL in the loss. Defaults to None.
            simpo_gamma: (float, optional): SimPO gamma parameter. Defaults to None.
            from_checkpoint (str, optional): The checkpoint identifier to continue training from a previous fine-tuning job.
                The format: {$JOB_ID/$OUTPUT_MODEL_NAME}:{$STEP}.
                The step value is optional, without it the final checkpoint will be used.
            from_hf_model (str, optional): The Hugging Face Hub repo to start training from.
                Should be as close as possible to the base model (specified by the `model` argument) in terms of architecture and size.
            hf_model_revision (str, optional): The revision of the Hugging Face Hub model to continue training from. Defaults to None.
                Example: hf_model_revision=None (defaults to the latest revision in `main`) or
                hf_model_revision="607a30d783dfa663caf39e06633721c8d4cfcd7e" (specific commit).
            hf_api_token (str, optional): API key for the Hugging Face Hub. Defaults to None.
            hf_output_repo_name (str, optional): HF repo to upload the fine-tuned model to. Defaults to None.

        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        if model_limits is None:
            model_name = None
            # mypy doesn't understand that model or from_checkpoint is not None
            if model is not None:
                model_name = model
            elif from_checkpoint is not None:
                model_name = from_checkpoint.split(":")[0]
            else:
                # this branch is unreachable, but mypy doesn't know that
                pass
            model_limits = get_model_limits(self._client, str(model_name))

        finetune_request, training_type_cls, training_method_cls = create_finetune_request(
            model_limits=model_limits,
            training_file=training_file,
            model=model,
            n_epochs=n_epochs,
            validation_file=validation_file,
            n_evals=n_evals,
            n_checkpoints=n_checkpoints,
            batch_size=batch_size,
            learning_rate=learning_rate,
            lr_scheduler_type=lr_scheduler_type,
            min_lr_ratio=min_lr_ratio,
            scheduler_num_cycles=scheduler_num_cycles,
            warmup_ratio=warmup_ratio,
            max_grad_norm=max_grad_norm,
            weight_decay=weight_decay,
            lora=lora,
            lora_r=lora_r,
            lora_dropout=lora_dropout,
            lora_alpha=lora_alpha,
            lora_trainable_modules=lora_trainable_modules,
            train_vision=train_vision,
            suffix=suffix,
            wandb_api_key=wandb_api_key,
            wandb_base_url=wandb_base_url,
            wandb_project_name=wandb_project_name,
            wandb_name=wandb_name,
            train_on_inputs=train_on_inputs,
            training_method=training_method,
            dpo_beta=dpo_beta,
            dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length,
            rpo_alpha=rpo_alpha,
            simpo_gamma=simpo_gamma,
            from_checkpoint=from_checkpoint,
            from_hf_model=from_hf_model,
            hf_model_revision=hf_model_revision,
            hf_api_token=hf_api_token,
            hf_output_repo_name=hf_output_repo_name,
        )

        if not model_limits.supports_vision:
            price_estimation_result = self.estimate_price(
                training_file=training_file,
                from_checkpoint=from_checkpoint or Omit(),
                validation_file=validation_file or Omit(),
                model=model or "",
                n_epochs=finetune_request.n_epochs,
                n_evals=finetune_request.n_evals or 0,
                training_type=training_type_cls,
                training_method=training_method_cls,
            )
            price_limit_passed = price_estimation_result.allowed_to_proceed
        else:
            # unsupported case
            price_limit_passed = True

        if verbose:
            rprint(
                "Submitting a fine-tuning job with the following parameters:",
                finetune_request,
            )
            if not price_limit_passed:
                rprint(
                    "[red]"
                    + _WARNING_MESSAGE_INSUFFICIENT_FUNDS.format(
                        price_estimation_result.estimated_total_price  # pyright: ignore[reportPossiblyUnboundVariable]
                    )
                    + "[/red]",
                )
        parameter_payload = finetune_request.model_dump(exclude_none=True)

        return self._client.post(
            "/fine-tunes",
            body=parameter_payload,
            cast_to=FinetuneResponseLib,
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
    ) -> FinetuneResponse:
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
            cast_to=FinetuneResponse,
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
        force: bool | Omit = omit,
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

    def content(
        self,
        *,
        ft_id: str,
        checkpoint: Literal["merged", "adapter", "model_output_path"] | Omit = omit,
        checkpoint_step: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Receive a compressed fine-tuned model or checkpoint.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint: Specifies checkpoint type to download - `merged` vs `adapter`. This field is
              required if the checkpoint_step is not set.

          checkpoint_step: Specifies step number for checkpoint to download. Ignores `checkpoint` value if
              set.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
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
                    },
                    fine_tuning_content_params.FineTuningContentParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def estimate_price(
        self,
        *,
        training_file: str,
        from_checkpoint: str | Omit = omit,
        model: str | Omit = omit,
        n_epochs: int | Omit = omit,
        n_evals: int | Omit = omit,
        training_method: fine_tuning_estimate_price_params.TrainingMethod | Omit = omit,
        training_type: fine_tuning_estimate_price_params.TrainingType | Omit = omit,
        validation_file: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningEstimatePriceResponse:
        """
        Estimate the price of a fine-tuning job.

        Args:
          training_file: File-ID of a training file uploaded to the Together API

          from_checkpoint: The checkpoint identifier to continue training from a previous fine-tuning job.
              Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
              `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
              final checkpoint will be used.

          model: Name of the base model to run fine-tune job on

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          training_method: The training method to use. 'sft' for Supervised Fine-Tuning or 'dpo' for Direct
              Preference Optimization.

          validation_file: File-ID of a validation file uploaded to the Together API

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/fine-tunes/estimate-price",
            body=maybe_transform(
                {
                    "training_file": training_file,
                    "from_checkpoint": from_checkpoint,
                    "model": model,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "training_method": training_method,
                    "training_type": training_type,
                    "validation_file": validation_file,
                },
                fine_tuning_estimate_price_params.FineTuningEstimatePriceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningEstimatePriceResponse,
        )

    def list_checkpoints(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListCheckpointsResponse:
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
            cast_to=FineTuningListCheckpointsResponse,
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
        training_file: str,
        model: str | None = None,
        n_epochs: int = 1,
        validation_file: str | None = "",
        n_evals: int | None = 0,
        n_checkpoints: int | None = 1,
        batch_size: int | Literal["max"] = "max",
        learning_rate: float | None = 0.00001,
        lr_scheduler_type: Literal["linear", "cosine"] = "cosine",
        min_lr_ratio: float = 0.0,
        scheduler_num_cycles: float = 0.5,
        warmup_ratio: float = 0.0,
        max_grad_norm: float = 1.0,
        weight_decay: float = 0.0,
        lora: bool = True,
        lora_r: int | None = None,
        lora_dropout: float | None = 0,
        lora_alpha: float | None = None,
        lora_trainable_modules: str | None = "all-linear",
        train_vision: bool = False,
        suffix: str | None = None,
        wandb_api_key: str | None = None,
        wandb_base_url: str | None = None,
        wandb_project_name: str | None = None,
        wandb_name: str | None = None,
        verbose: bool = False,
        model_limits: FinetuneTrainingLimits | None = None,
        train_on_inputs: bool | Literal["auto"] | None = None,
        training_method: str = "sft",
        dpo_beta: float | None = None,
        dpo_normalize_logratios_by_length: bool = False,
        rpo_alpha: float | None = None,
        simpo_gamma: float | None = None,
        from_checkpoint: str | None = None,
        from_hf_model: str | None = None,
        hf_model_revision: str | None = None,
        hf_api_token: str | None = None,
        hf_output_repo_name: str | None = None,
    ) -> FinetuneResponse:
        """
        Method to initiate a fine-tuning job

        Args:
            training_file (str): File-ID of a file uploaded to the Together API
            model (str, optional): Name of the base model to run fine-tune job on
            n_epochs (int, optional): Number of epochs for fine-tuning. Defaults to 1.
            validation file (str, optional): File ID of a file uploaded to the Together API for validation.
            n_evals (int, optional): Number of evaluation loops to run. Defaults to 0.
            n_checkpoints (int, optional): Number of checkpoints to save during fine-tuning.
                Defaults to 1.
            batch_size (int or "max"): Batch size for fine-tuning. Defaults to max.
            learning_rate (float, optional): Learning rate multiplier to use for training
                Defaults to 0.00001.
            lr_scheduler_type (Literal["linear", "cosine"]): Learning rate scheduler type. Defaults to "cosine".
            min_lr_ratio (float, optional): Min learning rate ratio of the initial learning rate for
                the learning rate scheduler. Defaults to 0.0.
            scheduler_num_cycles (float, optional): Number or fraction of cycles for the cosine learning rate scheduler. Defaults to 0.5.
            warmup_ratio (float, optional): Warmup ratio for the learning rate scheduler.
            max_grad_norm (float, optional): Max gradient norm. Defaults to 1.0, set to 0 to disable.
            weight_decay (float, optional): Weight decay. Defaults to 0.0.
            lora (bool, optional): Whether to use LoRA adapters. Defaults to True.
            lora_r (int, optional): Rank of LoRA adapters. Defaults to 8.
            lora_dropout (float, optional): Dropout rate for LoRA adapters. Defaults to 0.
            lora_alpha (float, optional): Alpha for LoRA adapters. Defaults to 8.
            lora_trainable_modules (str, optional): Trainable modules for LoRA adapters. Defaults to "all-linear".
            train_vision (bool, optional): Whether to train the vision encoder (Only for multimodal models). Defaults to False.
            suffix (str, optional): Up to 40 character suffix that will be added to your fine-tuned model name.
                Defaults to None.
            wandb_api_key (str, optional): API key for Weights & Biases integration.
                Defaults to None.
            wandb_base_url (str, optional): Base URL for Weights & Biases integration.
                Defaults to None.
            wandb_project_name (str, optional): Project name for Weights & Biases integration.
                Defaults to None.
            wandb_name (str, optional): Run name for Weights & Biases integration.
                Defaults to None.
            verbose (bool, optional): whether to print the job parameters before submitting a request.
                Defaults to False.
            model_limits (FinetuneTrainingLimits, optional): Limits for the hyperparameters the model in Fine-tuning.
                Defaults to None.
            train_on_inputs (bool or "auto", optional): Whether to mask the user messages in conversational data or prompts in instruction data.
                "auto" will automatically determine whether to mask the inputs based on the data format.
                For datasets with the "text" field (general format), inputs will not be masked.
                For datasets with the "messages" field (conversational format) or "prompt" and "completion" fields
                (Instruction format), inputs will be masked.
                Defaults to None, or "auto" if training_method is "sft" (set in create_finetune_request).
            training_method (str, optional): Training method. Defaults to "sft".
                Supported methods: "sft", "dpo".
            dpo_beta (float, optional): DPO beta parameter. Defaults to None.
            dpo_normalize_logratios_by_length (bool): Whether or not normalize logratios by sample length. Defaults to False,
            rpo_alpha (float, optional): RPO alpha parameter of DPO training to include NLL in the loss. Defaults to None.
            simpo_gamma: (float, optional): SimPO gamma parameter. Defaults to None.
            from_checkpoint (str, optional): The checkpoint identifier to continue training from a previous fine-tuning job.
                The format: {$JOB_ID/$OUTPUT_MODEL_NAME}:{$STEP}.
                The step value is optional, without it the final checkpoint will be used.
            from_hf_model (str, optional): The Hugging Face Hub repo to start training from.
                Should be as close as possible to the base model (specified by the `model` argument) in terms of architecture and size.
            hf_model_revision (str, optional): The revision of the Hugging Face Hub model to continue training from. Defaults to None.
                Example: hf_model_revision=None (defaults to the latest revision in `main`) or
                hf_model_revision="607a30d783dfa663caf39e06633721c8d4cfcd7e" (specific commit).
            hf_api_token (str, optional): API key for the Hugging Face Hub. Defaults to None.
            hf_output_repo_name (str, optional): HF repo to upload the fine-tuned model to. Defaults to None.

        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        if model_limits is None:
            model_name = None
            # mypy doesn't understand that model or from_checkpoint is not None
            if model is not None:
                model_name = model
            elif from_checkpoint is not None:
                model_name = from_checkpoint.split(":")[0]
            else:
                # this branch is unreachable, but mypy doesn't know that
                pass
            model_limits = await async_get_model_limits(self._client, str(model_name))

        finetune_request, training_type_cls, training_method_cls = create_finetune_request(
            model_limits=model_limits,
            training_file=training_file,
            model=model,
            n_epochs=n_epochs,
            validation_file=validation_file,
            n_evals=n_evals,
            n_checkpoints=n_checkpoints,
            batch_size=batch_size,
            learning_rate=learning_rate,
            lr_scheduler_type=lr_scheduler_type,
            min_lr_ratio=min_lr_ratio,
            scheduler_num_cycles=scheduler_num_cycles,
            warmup_ratio=warmup_ratio,
            max_grad_norm=max_grad_norm,
            weight_decay=weight_decay,
            lora=lora,
            lora_r=lora_r,
            lora_dropout=lora_dropout,
            lora_alpha=lora_alpha,
            lora_trainable_modules=lora_trainable_modules,
            train_vision=train_vision,
            suffix=suffix,
            wandb_api_key=wandb_api_key,
            wandb_base_url=wandb_base_url,
            wandb_project_name=wandb_project_name,
            wandb_name=wandb_name,
            train_on_inputs=train_on_inputs,
            training_method=training_method,
            dpo_beta=dpo_beta,
            dpo_normalize_logratios_by_length=dpo_normalize_logratios_by_length,
            rpo_alpha=rpo_alpha,
            simpo_gamma=simpo_gamma,
            from_checkpoint=from_checkpoint,
            from_hf_model=from_hf_model,
            hf_model_revision=hf_model_revision,
            hf_api_token=hf_api_token,
            hf_output_repo_name=hf_output_repo_name,
        )

        price_estimation_result = await self.estimate_price(
            training_file=training_file,
            from_checkpoint=from_checkpoint or Omit(),
            validation_file=validation_file or Omit(),
            model=model or "",
            n_epochs=finetune_request.n_epochs,
            n_evals=finetune_request.n_evals or 0,
            training_type=training_type_cls,
            training_method=training_method_cls,
        )

        if verbose:
            rprint(
                "Submitting a fine-tuning job with the following parameters:",
                finetune_request,
            )
            if not price_estimation_result.allowed_to_proceed:
                rprint(
                    "[red]"
                    + _WARNING_MESSAGE_INSUFFICIENT_FUNDS.format(
                        price_estimation_result.estimated_total_price  # pyright: ignore[reportPossiblyUnboundVariable]
                    )
                    + "[/red]",
                )
        parameter_payload = finetune_request.model_dump(exclude_none=True)

        return await self._client.post(
            "/fine-tunes",
            body=parameter_payload,
            cast_to=FinetuneResponse,
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
    ) -> FinetuneResponse:
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
            cast_to=FinetuneResponse,
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
        force: bool | Omit = omit,
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

    async def content(
        self,
        *,
        ft_id: str,
        checkpoint: Literal["merged", "adapter", "model_output_path"] | Omit = omit,
        checkpoint_step: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Receive a compressed fine-tuned model or checkpoint.

        Args:
          ft_id: Fine-tune ID to download. A string that starts with `ft-`.

          checkpoint: Specifies checkpoint type to download - `merged` vs `adapter`. This field is
              required if the checkpoint_step is not set.

          checkpoint_step: Specifies step number for checkpoint to download. Ignores `checkpoint` value if
              set.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
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
                    },
                    fine_tuning_content_params.FineTuningContentParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def estimate_price(
        self,
        *,
        training_file: str,
        from_checkpoint: str | Omit = omit,
        model: str | Omit = omit,
        n_epochs: int | Omit = omit,
        n_evals: int | Omit = omit,
        training_method: fine_tuning_estimate_price_params.TrainingMethod | Omit = omit,
        training_type: fine_tuning_estimate_price_params.TrainingType | Omit = omit,
        validation_file: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningEstimatePriceResponse:
        """
        Estimate the price of a fine-tuning job.

        Args:
          training_file: File-ID of a training file uploaded to the Together API

          from_checkpoint: The checkpoint identifier to continue training from a previous fine-tuning job.
              Format is `{$JOB_ID}` or `{$OUTPUT_MODEL_NAME}` or `{$JOB_ID}:{$STEP}` or
              `{$OUTPUT_MODEL_NAME}:{$STEP}`. The step value is optional; without it, the
              final checkpoint will be used.

          model: Name of the base model to run fine-tune job on

          n_epochs: Number of complete passes through the training dataset (higher values may
              improve results but increase cost and risk of overfitting)

          n_evals: Number of evaluations to be run on a given validation set during training

          training_method: The training method to use. 'sft' for Supervised Fine-Tuning or 'dpo' for Direct
              Preference Optimization.

          validation_file: File-ID of a validation file uploaded to the Together API

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/fine-tunes/estimate-price",
            body=await async_maybe_transform(
                {
                    "training_file": training_file,
                    "from_checkpoint": from_checkpoint,
                    "model": model,
                    "n_epochs": n_epochs,
                    "n_evals": n_evals,
                    "training_method": training_method,
                    "training_type": training_type,
                    "validation_file": validation_file,
                },
                fine_tuning_estimate_price_params.FineTuningEstimatePriceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuningEstimatePriceResponse,
        )

    async def list_checkpoints(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FineTuningListCheckpointsResponse:
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
            cast_to=FineTuningListCheckpointsResponse,
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


class FineTuningResourceWithRawResponse:
    def __init__(self, fine_tuning: FineTuningResource) -> None:
        self._fine_tuning = fine_tuning

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
        self.content = to_custom_raw_response_wrapper(
            fine_tuning.content,
            BinaryAPIResponse,
        )
        self.estimate_price = to_raw_response_wrapper(
            fine_tuning.estimate_price,
        )
        self.list_checkpoints = to_raw_response_wrapper(
            fine_tuning.list_checkpoints,
        )
        self.list_events = to_raw_response_wrapper(
            fine_tuning.list_events,
        )


class AsyncFineTuningResourceWithRawResponse:
    def __init__(self, fine_tuning: AsyncFineTuningResource) -> None:
        self._fine_tuning = fine_tuning

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
        self.content = async_to_custom_raw_response_wrapper(
            fine_tuning.content,
            AsyncBinaryAPIResponse,
        )
        self.estimate_price = async_to_raw_response_wrapper(
            fine_tuning.estimate_price,
        )
        self.list_checkpoints = async_to_raw_response_wrapper(
            fine_tuning.list_checkpoints,
        )
        self.list_events = async_to_raw_response_wrapper(
            fine_tuning.list_events,
        )


class FineTuningResourceWithStreamingResponse:
    def __init__(self, fine_tuning: FineTuningResource) -> None:
        self._fine_tuning = fine_tuning

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
        self.content = to_custom_streamed_response_wrapper(
            fine_tuning.content,
            StreamedBinaryAPIResponse,
        )
        self.estimate_price = to_streamed_response_wrapper(
            fine_tuning.estimate_price,
        )
        self.list_checkpoints = to_streamed_response_wrapper(
            fine_tuning.list_checkpoints,
        )
        self.list_events = to_streamed_response_wrapper(
            fine_tuning.list_events,
        )


class AsyncFineTuningResourceWithStreamingResponse:
    def __init__(self, fine_tuning: AsyncFineTuningResource) -> None:
        self._fine_tuning = fine_tuning

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
        self.content = async_to_custom_streamed_response_wrapper(
            fine_tuning.content,
            AsyncStreamedBinaryAPIResponse,
        )
        self.estimate_price = async_to_streamed_response_wrapper(
            fine_tuning.estimate_price,
        )
        self.list_checkpoints = async_to_streamed_response_wrapper(
            fine_tuning.list_checkpoints,
        )
        self.list_events = async_to_streamed_response_wrapper(
            fine_tuning.list_events,
        )
