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
    LossConfig,
    MuonParams,
    SamplingParams,
    WeightSyncType,
    operation_sample_params,
    operation_optim_step_params,
    operation_weights_sync_params,
    operation_forward_backward_params,
    operation_custom_forward_backward_params,
)
from ....types.beta.rl.adam_params import AdamParams
from ....types.beta.rl.muon_params import MuonParams
from ....types.beta.rl.sampling_params import SamplingParams
from ....types.beta.rl.sample_operation import SampleOperation
from ....types.beta.rl.weight_sync_type import WeightSyncType
from ....types.beta.rl.loss_config_param import LossConfig
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.optim_step_operation import OptimStepOperation
from ....types.beta.rl.weights_sync_operation import WeightsSyncOperation
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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

    def forward_backward(
        self,
        session_id: str,
        *,
        loss: LossConfig,
        samples: Iterable[operation_forward_backward_params.Sample],
        idempotency_key: str,
        forward_only: bool | Omit = omit,
        return_loss_fn_outputs: bool | Omit = omit,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          forward_only: Run the forward pass only: report the loss and metrics, and the per-sample
              outputs when requested, without accumulating gradients. Defaults to false. Pair
              it with `return_loss_fn_outputs` to score a batch and read back its per-token
              log-probabilities.

          return_loss_fn_outputs: Return the loss function's per-sample output tensors alongside the loss and
              metrics. Defaults to false. Enabling it increases the response size
              substantially for large batches and reduces step throughput, so leave it unset
              for ordinary training steps.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward-backward", session_id=session_id),
            body=maybe_transform(
                {
                    "loss": loss,
                    "samples": samples,
                    "forward_only": forward_only,
                    "return_loss_fn_outputs": return_loss_fn_outputs,
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
        idempotency_key: str,
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
        gradients to update model parameters. Does not make the updated parameters
        available for sampling; call `weights-sync` afterwards when you want subsequent
        samples to use the updated policy.

        Args:
          session_id: Training session ID

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          adam_params: Adam optimizer overrides for this step.

          muon_params: Muon optimizer overrides for this step.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/optim-step", session_id=session_id),
            body=maybe_transform(
                {
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

    def retrieve_weights_sync(
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
    ) -> WeightsSyncOperation:
        """
        Retrieves the current status and result of a weights-sync operation.

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
                "/rl/training-sessions/{session_id}/operations/weights-sync/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WeightsSyncOperation,
        )

    def sample(
        self,
        session_id: str,
        *,
        model_inputs: Iterable[ModelInput],
        idempotency_key: str,
        num_samples: int | Omit = omit,
        prompt_logprobs: bool | Omit = omit,
        return_routed_experts: bool | Omit = omit,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          num_samples: Number of completions to generate per prompt

          prompt_logprobs: When true, also compute teacher-forced log-probabilities for the model input
              tokens and return them in `SampleResult.prompt_logprobs`.

          return_routed_experts: When true, enable reuse of the expert selections from sampled sequences during
              training. Only supported for mixture-of-experts models; ignored for other
              models.

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
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/sample", session_id=session_id),
            body=maybe_transform(
                {
                    "model_inputs": model_inputs,
                    "num_samples": num_samples,
                    "prompt_logprobs": prompt_logprobs,
                    "return_routed_experts": return_routed_experts,
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

    def weights_sync(
        self,
        session_id: str,
        *,
        weight_sync_type: WeightSyncType,
        idempotency_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WeightsSyncOperation:
        """
        Submits a weights-sync operation that makes the session's current trained
        parameters available for sampling. Call this after `optim-step` when you want
        subsequent samples to use the updated policy.

        Args:
          session_id: Training session ID

          weight_sync_type: How updated parameters are made available for sampling. See `WeightSyncType` for
              accepted values.

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return self._post(
            path_template("/rl/training-sessions/{session_id}/operations/weights-sync", session_id=session_id),
            body=maybe_transform(
                {"weight_sync_type": weight_sync_type}, operation_weights_sync_params.OperationWeightsSyncParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WeightsSyncOperation,
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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
        idempotency_key: str,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
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

    async def forward_backward(
        self,
        session_id: str,
        *,
        loss: LossConfig,
        samples: Iterable[operation_forward_backward_params.Sample],
        idempotency_key: str,
        forward_only: bool | Omit = omit,
        return_loss_fn_outputs: bool | Omit = omit,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          forward_only: Run the forward pass only: report the loss and metrics, and the per-sample
              outputs when requested, without accumulating gradients. Defaults to false. Pair
              it with `return_loss_fn_outputs` to score a batch and read back its per-token
              log-probabilities.

          return_loss_fn_outputs: Return the loss function's per-sample output tensors alongside the loss and
              metrics. Defaults to false. Enabling it increases the response size
              substantially for large batches and reduces step throughput, so leave it unset
              for ordinary training steps.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/forward-backward", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "loss": loss,
                    "samples": samples,
                    "forward_only": forward_only,
                    "return_loss_fn_outputs": return_loss_fn_outputs,
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
        idempotency_key: str,
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
        gradients to update model parameters. Does not make the updated parameters
        available for sampling; call `weights-sync` afterwards when you want subsequent
        samples to use the updated policy.

        Args:
          session_id: Training session ID

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          adam_params: Adam optimizer overrides for this step.

          muon_params: Muon optimizer overrides for this step.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/optim-step", session_id=session_id),
            body=await async_maybe_transform(
                {
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

    async def retrieve_weights_sync(
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
    ) -> WeightsSyncOperation:
        """
        Retrieves the current status and result of a weights-sync operation.

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
                "/rl/training-sessions/{session_id}/operations/weights-sync/{operation_id}",
                session_id=session_id,
                operation_id=operation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WeightsSyncOperation,
        )

    async def sample(
        self,
        session_id: str,
        *,
        model_inputs: Iterable[ModelInput],
        idempotency_key: str,
        num_samples: int | Omit = omit,
        prompt_logprobs: bool | Omit = omit,
        return_routed_experts: bool | Omit = omit,
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

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          num_samples: Number of completions to generate per prompt

          prompt_logprobs: When true, also compute teacher-forced log-probabilities for the model input
              tokens and return them in `SampleResult.prompt_logprobs`.

          return_routed_experts: When true, enable reuse of the expert selections from sampled sequences during
              training. Only supported for mixture-of-experts models; ignored for other
              models.

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
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/sample", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "model_inputs": model_inputs,
                    "num_samples": num_samples,
                    "prompt_logprobs": prompt_logprobs,
                    "return_routed_experts": return_routed_experts,
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

    async def weights_sync(
        self,
        session_id: str,
        *,
        weight_sync_type: WeightSyncType,
        idempotency_key: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WeightsSyncOperation:
        """
        Submits a weights-sync operation that makes the session's current trained
        parameters available for sampling. Call this after `optim-step` when you want
        subsequent samples to use the updated policy.

        Args:
          session_id: Training session ID

          weight_sync_type: How updated parameters are made available for sampling. See `WeightSyncType` for
              accepted values.

          idempotency_key: Required key that makes retries return the original operation; use a new key for
              changed request bodies.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Idempotency-Key": idempotency_key, **(extra_headers or {})}
        return await self._post(
            path_template("/rl/training-sessions/{session_id}/operations/weights-sync", session_id=session_id),
            body=await async_maybe_transform(
                {"weight_sync_type": weight_sync_type}, operation_weights_sync_params.OperationWeightsSyncParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WeightsSyncOperation,
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
        self.forward_backward = to_raw_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = to_raw_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = to_raw_response_wrapper(
            operations.retrieve_custom_forward_backward,
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
        self.retrieve_weights_sync = to_raw_response_wrapper(
            operations.retrieve_weights_sync,
        )
        self.sample = to_raw_response_wrapper(
            operations.sample,
        )
        self.weights_sync = to_raw_response_wrapper(
            operations.weights_sync,
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
        self.forward_backward = async_to_raw_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = async_to_raw_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = async_to_raw_response_wrapper(
            operations.retrieve_custom_forward_backward,
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
        self.retrieve_weights_sync = async_to_raw_response_wrapper(
            operations.retrieve_weights_sync,
        )
        self.sample = async_to_raw_response_wrapper(
            operations.sample,
        )
        self.weights_sync = async_to_raw_response_wrapper(
            operations.weights_sync,
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
        self.forward_backward = to_streamed_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = to_streamed_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = to_streamed_response_wrapper(
            operations.retrieve_custom_forward_backward,
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
        self.retrieve_weights_sync = to_streamed_response_wrapper(
            operations.retrieve_weights_sync,
        )
        self.sample = to_streamed_response_wrapper(
            operations.sample,
        )
        self.weights_sync = to_streamed_response_wrapper(
            operations.weights_sync,
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
        self.forward_backward = async_to_streamed_response_wrapper(
            operations.forward_backward,
        )
        self.optim_step = async_to_streamed_response_wrapper(
            operations.optim_step,
        )
        self.retrieve_custom_forward_backward = async_to_streamed_response_wrapper(
            operations.retrieve_custom_forward_backward,
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
        self.retrieve_weights_sync = async_to_streamed_response_wrapper(
            operations.retrieve_weights_sync,
        )
        self.sample = async_to_streamed_response_wrapper(
            operations.sample,
        )
        self.weights_sync = async_to_streamed_response_wrapper(
            operations.weights_sync,
        )
