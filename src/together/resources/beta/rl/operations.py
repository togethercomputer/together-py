# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....types.beta.rl import (
    AdamParams,
    MuonParams,
    SamplingParams,
    WeightSyncType,
    operation_sample_params,
    operation_forward_params,
    operation_optim_step_params,
    operation_forward_backward_params,
    operation_custom_forward_backward_params,
)
from ....types.beta.rl.adam_params import AdamParams
from ....types.beta.rl.muon_params import MuonParams
from ....types.beta.rl.sampling_params import SamplingParams
from ....types.beta.rl.sample_operation import SampleOperation
from ....types.beta.rl.weight_sync_type import WeightSyncType
from ....types.beta.rl.forward_operation import ForwardOperation
from ....types.beta.rl.loss_config_param import LossConfigParam
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.optim_step_operation import OptimStepOperation
from ....types.beta.rl.forward_backward_operation import ForwardBackwardOperation
from ....types.beta.rl.training_checkpoint_operation import TrainingCheckpointOperation
from ....types.beta.rl.inference_checkpoint_operation import InferenceCheckpointOperation
from ....types.beta.rl.custom_forward_backward_operation import CustomForwardBackwardOperation

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

    def create_inference_checkpoint(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceCheckpointOperation:
        """
        Submits an operation that will asynchronously save the current LoRA adapter as
        an inference checkpoint and upload it to object storage.

        Args:
          session_id: Training session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/inference-checkpoint", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceCheckpointOperation,
        )

    def create_training_checkpoint(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingCheckpointOperation:
        """
        Submits an operation that will asynchronously save the full training state
        (adapter + optimizer + step).

        Args:
          session_id: Training session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/training-checkpoint", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCheckpointOperation,
        )

    def custom_forward_backward(
        self,
        session_id: str,
        *,
        gradients: Iterable[operation_custom_forward_backward_params.Gradient],
        samples: Iterable[operation_custom_forward_backward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomForwardBackwardOperation:
        """
        Submits a forward-backward pass driven by externally computed gradients of the
        loss with respect to per-token log-probabilities.

        Args:
          session_id: Training session ID

          gradients: Per-sample per-token gradients of the loss with respect to log-probabilities

          samples: Batch of training samples

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template(
                "/rl/training-sessions/{session_id}/operations/custom-forward-backward", session_id=session_id
            ),
            body=maybe_transform(
                {
                    "gradients": gradients,
                    "samples": samples,
                },
                operation_custom_forward_backward_params.OperationCustomForwardBackwardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomForwardBackwardOperation,
        )

    def forward(
        self,
        session_id: str,
        *,
        samples: Iterable[operation_forward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardOperation:
        """
        Submits a forward operation that will asynchronously run a no-grad forward pass
        and return per-token log-probabilities for each sample.

        Args:
          session_id: Training session ID

          samples: Batch of training samples for which to compute per-token log-probabilities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward", session_id=session_id),
            body=maybe_transform({"samples": samples}, operation_forward_params.OperationForwardParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardOperation,
        )

    def forward_backward(
        self,
        session_id: str,
        *,
        loss: LossConfigParam,
        samples: Iterable[operation_forward_backward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardBackwardOperation:
        """
        Submits a forward-backward pass operation that will asynchronously compute
        gradients via backpropagation.

        Args:
          session_id: Training session ID

          loss: Loss function configuration

          samples: Batch of training samples to process

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward-backward", session_id=session_id),
            body=maybe_transform(
                {
                    "loss": loss,
                    "samples": samples,
                },
                operation_forward_backward_params.OperationForwardBackwardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardBackwardOperation,
        )

    def optim_step(
        self,
        session_id: str,
        *,
        weight_sync_type: WeightSyncType,
        adam_params: AdamParams | Omit = omit,
        muon_params: MuonParams | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OptimStepOperation:
        """
        Submits an optimizer step operation that will asynchronously apply accumulated
        gradients to update model parameters.

        Args:
          session_id: Training session ID

          weight_sync_type: How the trainer's updated weights are propagated to the generator after this
              optimizer step. See `WeightSyncType` for accepted values.

          adam_params: Adam optimizer overrides for this step.

          muon_params: Muon optimizer overrides for this step.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/optim-step", session_id=session_id),
            body=maybe_transform(
                {
                    "weight_sync_type": weight_sync_type,
                    "adam_params": adam_params,
                    "muon_params": muon_params,
                },
                operation_optim_step_params.OperationOptimStepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OptimStepOperation,
        )

    def retrieve_custom_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomForwardBackwardOperation:
        """
        Retrieves the current status and result of a custom forward-backward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/custom-forward-backward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomForwardBackwardOperation,
        )

    def retrieve_forward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardOperation:
        """
        Retrieves the current status and result of a forward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/forward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardOperation,
        )

    def retrieve_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardBackwardOperation:
        """
        Retrieves the current status and result of a forward-backward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/forward-backward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardBackwardOperation,
        )

    def retrieve_inference_checkpoint(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceCheckpointOperation:
        """
        Retrieves the current status and result of an inference checkpoint operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/inference-checkpoint/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceCheckpointOperation,
        )

    def retrieve_optim_step(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OptimStepOperation:
        """
        Retrieves the current status and result of an optim-step operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/optim-step/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OptimStepOperation,
        )

    def retrieve_sample(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SampleOperation:
        """
        Retrieves the current status and result of a sample operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/sample/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SampleOperation,
        )

    def retrieve_training_checkpoint(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingCheckpointOperation:
        """
        Retrieves the current status and result of a save training checkpoint operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/training-checkpoint/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCheckpointOperation,
        )

    def sample(
        self,
        session_id: str,
        *,
        model_inputs: Iterable[ModelInput],
        num_samples: int | Omit = omit,
        prompt_logprobs: bool | Omit = omit,
        sampling_params: SamplingParams | Omit = omit,
        topk_prompt_logprobs: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SampleOperation:
        """
        Submits a sample operation that will asynchronously generate text completions
        with logprobs.

        Args:
          session_id: Training session ID

          model_inputs: Model inputs to sample from

          num_samples: Number of completions to generate per prompt

          prompt_logprobs: When true, also compute teacher-forced log-probabilities for the model input
              tokens and return them in `SampleResult.prompt_logprobs`.

          sampling_params: Optional sampling parameters

          topk_prompt_logprobs: Number of most likely alternative tokens to return per model input token in
              `SampleResult.topk_prompt_logprobs`. 0 disables top-k prompt log-probabilities.
              Maximum 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/sample", session_id=session_id),
            body=maybe_transform(
                {
                    "model_inputs": model_inputs,
                    "num_samples": num_samples,
                    "prompt_logprobs": prompt_logprobs,
                    "sampling_params": sampling_params,
                    "topk_prompt_logprobs": topk_prompt_logprobs,
                },
                operation_sample_params.OperationSampleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SampleOperation,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

    async def create_inference_checkpoint(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceCheckpointOperation:
        """
        Submits an operation that will asynchronously save the current LoRA adapter as
        an inference checkpoint and upload it to object storage.

        Args:
          session_id: Training session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/inference-checkpoint", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceCheckpointOperation,
        )

    async def create_training_checkpoint(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingCheckpointOperation:
        """
        Submits an operation that will asynchronously save the full training state
        (adapter + optimizer + step).

        Args:
          session_id: Training session ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/training-checkpoint", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCheckpointOperation,
        )

    async def custom_forward_backward(
        self,
        session_id: str,
        *,
        gradients: Iterable[operation_custom_forward_backward_params.Gradient],
        samples: Iterable[operation_custom_forward_backward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomForwardBackwardOperation:
        """
        Submits a forward-backward pass driven by externally computed gradients of the
        loss with respect to per-token log-probabilities.

        Args:
          session_id: Training session ID

          gradients: Per-sample per-token gradients of the loss with respect to log-probabilities

          samples: Batch of training samples

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template(
                "/rl/training-sessions/{session_id}/operations/custom-forward-backward", session_id=session_id
            ),
            body=await async_maybe_transform(
                {
                    "gradients": gradients,
                    "samples": samples,
                },
                operation_custom_forward_backward_params.OperationCustomForwardBackwardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomForwardBackwardOperation,
        )

    async def forward(
        self,
        session_id: str,
        *,
        samples: Iterable[operation_forward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardOperation:
        """
        Submits a forward operation that will asynchronously run a no-grad forward pass
        and return per-token log-probabilities for each sample.

        Args:
          session_id: Training session ID

          samples: Batch of training samples for which to compute per-token log-probabilities

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward", session_id=session_id),
            body=await async_maybe_transform({"samples": samples}, operation_forward_params.OperationForwardParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardOperation,
        )

    async def forward_backward(
        self,
        session_id: str,
        *,
        loss: LossConfigParam,
        samples: Iterable[operation_forward_backward_params.Sample],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardBackwardOperation:
        """
        Submits a forward-backward pass operation that will asynchronously compute
        gradients via backpropagation.

        Args:
          session_id: Training session ID

          loss: Loss function configuration

          samples: Batch of training samples to process

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward-backward", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "loss": loss,
                    "samples": samples,
                },
                operation_forward_backward_params.OperationForwardBackwardParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardBackwardOperation,
        )

    async def optim_step(
        self,
        session_id: str,
        *,
        weight_sync_type: WeightSyncType,
        adam_params: AdamParams | Omit = omit,
        muon_params: MuonParams | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OptimStepOperation:
        """
        Submits an optimizer step operation that will asynchronously apply accumulated
        gradients to update model parameters.

        Args:
          session_id: Training session ID

          weight_sync_type: How the trainer's updated weights are propagated to the generator after this
              optimizer step. See `WeightSyncType` for accepted values.

          adam_params: Adam optimizer overrides for this step.

          muon_params: Muon optimizer overrides for this step.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/optim-step", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "weight_sync_type": weight_sync_type,
                    "adam_params": adam_params,
                    "muon_params": muon_params,
                },
                operation_optim_step_params.OperationOptimStepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OptimStepOperation,
        )

    async def retrieve_custom_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomForwardBackwardOperation:
        """
        Retrieves the current status and result of a custom forward-backward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/custom-forward-backward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomForwardBackwardOperation,
        )

    async def retrieve_forward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardOperation:
        """
        Retrieves the current status and result of a forward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/forward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardOperation,
        )

    async def retrieve_forward_backward(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ForwardBackwardOperation:
        """
        Retrieves the current status and result of a forward-backward operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/forward-backward/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForwardBackwardOperation,
        )

    async def retrieve_inference_checkpoint(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InferenceCheckpointOperation:
        """
        Retrieves the current status and result of an inference checkpoint operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/inference-checkpoint/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceCheckpointOperation,
        )

    async def retrieve_optim_step(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OptimStepOperation:
        """
        Retrieves the current status and result of an optim-step operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/optim-step/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OptimStepOperation,
        )

    async def retrieve_sample(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SampleOperation:
        """
        Retrieves the current status and result of a sample operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/sample/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SampleOperation,
        )

    async def retrieve_training_checkpoint(
        self,
        operation_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TrainingCheckpointOperation:
        """
        Retrieves the current status and result of a save training checkpoint operation.

        Args:
          session_id: Training session ID

          operation_id: Operation ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not operation_id:
            raise ValueError(f"Expected a non-empty value for `operation_id` but received {operation_id!r}")
        return await self._get(
            path_template(
                "/rl/training-sessions/{session_id}/operations/training-checkpoint/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TrainingCheckpointOperation,
        )

    async def sample(
        self,
        session_id: str,
        *,
        model_inputs: Iterable[ModelInput],
        num_samples: int | Omit = omit,
        prompt_logprobs: bool | Omit = omit,
        sampling_params: SamplingParams | Omit = omit,
        topk_prompt_logprobs: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SampleOperation:
        """
        Submits a sample operation that will asynchronously generate text completions
        with logprobs.

        Args:
          session_id: Training session ID

          model_inputs: Model inputs to sample from

          num_samples: Number of completions to generate per prompt

          prompt_logprobs: When true, also compute teacher-forced log-probabilities for the model input
              tokens and return them in `SampleResult.prompt_logprobs`.

          sampling_params: Optional sampling parameters

          topk_prompt_logprobs: Number of most likely alternative tokens to return per model input token in
              `SampleResult.topk_prompt_logprobs`. 0 disables top-k prompt log-probabilities.
              Maximum 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/sample", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "model_inputs": model_inputs,
                    "num_samples": num_samples,
                    "prompt_logprobs": prompt_logprobs,
                    "sampling_params": sampling_params,
                    "topk_prompt_logprobs": topk_prompt_logprobs,
                },
                operation_sample_params.OperationSampleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SampleOperation,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.create_inference_checkpoint = to_raw_response_wrapper(
            operations.create_inference_checkpoint,
        )
        self.create_training_checkpoint = to_raw_response_wrapper(
            operations.create_training_checkpoint,
        )
        self.custom_forward_backward = to_raw_response_wrapper(
            operations.custom_forward_backward,
        )
        self.forward = to_raw_response_wrapper(
            operations.forward,
        )
        self.forward_backward = to_raw_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = to_raw_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = to_raw_response_wrapper(
            operations.retrieve_custom_forward_backward,
        )
        self.retrieve_forward = to_raw_response_wrapper(
            operations.retrieve_forward,
        )
        self.retrieve_forward_backward = to_raw_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_inference_checkpoint = to_raw_response_wrapper(
            operations.retrieve_inference_checkpoint,
        )
        self.retrieve_optim_step = to_raw_response_wrapper(
            operations.retrieve_optim_step,
        )
        self.retrieve_sample = to_raw_response_wrapper(
            operations.retrieve_sample,
        )
        self.retrieve_training_checkpoint = to_raw_response_wrapper(
            operations.retrieve_training_checkpoint,
        )
        self.sample = to_raw_response_wrapper(
            operations.sample,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.create_inference_checkpoint = async_to_raw_response_wrapper(
            operations.create_inference_checkpoint,
        )
        self.create_training_checkpoint = async_to_raw_response_wrapper(
            operations.create_training_checkpoint,
        )
        self.custom_forward_backward = async_to_raw_response_wrapper(
            operations.custom_forward_backward,
        )
        self.forward = async_to_raw_response_wrapper(
            operations.forward,
        )
        self.forward_backward = async_to_raw_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = async_to_raw_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = async_to_raw_response_wrapper(
            operations.retrieve_custom_forward_backward,
        )
        self.retrieve_forward = async_to_raw_response_wrapper(
            operations.retrieve_forward,
        )
        self.retrieve_forward_backward = async_to_raw_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_inference_checkpoint = async_to_raw_response_wrapper(
            operations.retrieve_inference_checkpoint,
        )
        self.retrieve_optim_step = async_to_raw_response_wrapper(
            operations.retrieve_optim_step,
        )
        self.retrieve_sample = async_to_raw_response_wrapper(
            operations.retrieve_sample,
        )
        self.retrieve_training_checkpoint = async_to_raw_response_wrapper(
            operations.retrieve_training_checkpoint,
        )
        self.sample = async_to_raw_response_wrapper(
            operations.sample,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.create_inference_checkpoint = to_streamed_response_wrapper(
            operations.create_inference_checkpoint,
        )
        self.create_training_checkpoint = to_streamed_response_wrapper(
            operations.create_training_checkpoint,
        )
        self.custom_forward_backward = to_streamed_response_wrapper(
            operations.custom_forward_backward,
        )
        self.forward = to_streamed_response_wrapper(
            operations.forward,
        )
        self.forward_backward = to_streamed_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = to_streamed_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = to_streamed_response_wrapper(
            operations.retrieve_custom_forward_backward,
        )
        self.retrieve_forward = to_streamed_response_wrapper(
            operations.retrieve_forward,
        )
        self.retrieve_forward_backward = to_streamed_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_inference_checkpoint = to_streamed_response_wrapper(
            operations.retrieve_inference_checkpoint,
        )
        self.retrieve_optim_step = to_streamed_response_wrapper(
            operations.retrieve_optim_step,
        )
        self.retrieve_sample = to_streamed_response_wrapper(
            operations.retrieve_sample,
        )
        self.retrieve_training_checkpoint = to_streamed_response_wrapper(
            operations.retrieve_training_checkpoint,
        )
        self.sample = to_streamed_response_wrapper(
            operations.sample,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.create_inference_checkpoint = async_to_streamed_response_wrapper(
            operations.create_inference_checkpoint,
        )
        self.create_training_checkpoint = async_to_streamed_response_wrapper(
            operations.create_training_checkpoint,
        )
        self.custom_forward_backward = async_to_streamed_response_wrapper(
            operations.custom_forward_backward,
        )
        self.forward = async_to_streamed_response_wrapper(
            operations.forward,
        )
        self.forward_backward = async_to_streamed_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = async_to_streamed_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = async_to_streamed_response_wrapper(
            operations.retrieve_custom_forward_backward,
        )
        self.retrieve_forward = async_to_streamed_response_wrapper(
            operations.retrieve_forward,
        )
        self.retrieve_forward_backward = async_to_streamed_response_wrapper(
            operations.retrieve_forward_backward,
        )
        self.retrieve_inference_checkpoint = async_to_streamed_response_wrapper(
            operations.retrieve_inference_checkpoint,
        )
        self.retrieve_optim_step = async_to_streamed_response_wrapper(
            operations.retrieve_optim_step,
        )
        self.retrieve_sample = async_to_streamed_response_wrapper(
            operations.retrieve_sample,
        )
        self.retrieve_training_checkpoint = async_to_streamed_response_wrapper(
            operations.retrieve_training_checkpoint,
        )
        self.sample = async_to_streamed_response_wrapper(
            operations.sample,
        )
