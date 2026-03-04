# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

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
from ..types.finetune_response import FinetuneResponse
from ..types.fine_tuning_list_response import FineTuningListResponse
from ..types.fine_tuning_cancel_response import FineTuningCancelResponse
from ..types.fine_tuning_delete_response import FineTuningDeleteResponse
from ..types.fine_tuning_list_events_response import FineTuningListEventsResponse
from ..types.fine_tuning_estimate_price_response import FineTuningEstimatePriceResponse
from ..types.fine_tuning_list_checkpoints_response import FineTuningListCheckpointsResponse

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
          id: The ID of the job to retrieve

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
          id: The ID of the fine-tune job to delete

          force: Deprecated and unused parameter.

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
          id: Fine-tune ID to cancel. A string that starts with `ft-`.

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
        training_type: Optional[fine_tuning_estimate_price_params.TrainingType] | Omit = omit,
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

          training_type: The training type to use. If not provided, the job will default to LoRA training
              type.

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
          id: The ID of the fine-tune job to list checkpoints for

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
          id: The ID of the fine-tune job to list events for

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
          id: The ID of the job to retrieve

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
          id: The ID of the fine-tune job to delete

          force: Deprecated and unused parameter.

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
          id: Fine-tune ID to cancel. A string that starts with `ft-`.

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
        training_type: Optional[fine_tuning_estimate_price_params.TrainingType] | Omit = omit,
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

          training_type: The training type to use. If not provided, the job will default to LoRA training
              type.

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
          id: The ID of the fine-tune job to list checkpoints for

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
          id: The ID of the fine-tune job to list events for

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
