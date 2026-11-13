# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.post_training import rollout_estimate_params
from ...types.post_training.estimate_rollout_response import EstimateRolloutResponse

__all__ = ["RolloutsResource", "AsyncRolloutsResource"]


class RolloutsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RolloutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RolloutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RolloutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RolloutsResourceWithStreamingResponse(self)

    def estimate(
        self,
        *,
        added_tokens_per_turn: int,
        base_model: str,
        concurrency: int,
        episodes: int,
        generated_tokens_per_turn: int,
        prompt_tokens: int,
        turns: int,
        compute_config: rollout_estimate_params.ComputeConfig | Omit = omit,
        distinct_prompts_per_replica: int | Omit = omit,
        episodes_per_prompt: int | Omit = omit,
        lora_enabled: bool | Omit = omit,
        shared_prefix_tokens: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EstimateRolloutResponse:
        """
        Estimates rollout-only time, generator GPU-hours, billed GPU-hours of the whole
        model resource, and price for a supported model and GPU type. Each generator
        replica may contain several inference servers or span multiple nodes. Assumes
        identical episodes, exact reuse of generated tokens between turns, turns that
        start together within a replica, no environment delay, and no concurrent
        computation of the same initial prompt. Prompt-cache reuse and capacity misses
        are approximate, especially for multi-turn episodes. Rates are measured in the
        training mode reported by lora_enabled. Cache-transfer and request-preemption
        delays are not included, so long multi-turn rollouts with distinct prompts can
        take longer than estimated.

        Args:
          added_tokens_per_turn: Tokens added before each later turn (K), including the prior generated tokens
              followed by environment tokens. Must be at least generated_tokens_per_turn.

          base_model: Base model to estimate. The model, GPU type, and training mode must support
              rollout estimates.

          concurrency: Maximum concurrent episodes across all generator replicas (B). Must be positive.

          episodes: Total number of episodes (N). Must be between 1 and 10000000.

          generated_tokens_per_turn: Tokens generated on each turn (O). Must be positive.

          prompt_tokens: Initial prompt tokens per episode (P). Must be positive.

          turns: Assistant turns per episode (T). Must be between 1 and 1024.

          compute_config: Compute layout to estimate, as for a model resource. Omitted fields use the
              model's default GPU type and one generator replica (D); num_generator_replicas
              must be positive.

          distinct_prompts_per_replica: Number of distinct initial prompts among the concurrent episodes of one replica
              (Q). When episodes_per_prompt is given, defaults to ceil(concurrent episodes /
              G). Otherwise defaults to 1 when shared_prefix_tokens equals prompt_tokens, and
              to the concurrent episodes per replica when it does not. Must be 1 when
              shared_prefix_tokens equals prompt_tokens.

          episodes_per_prompt: Maximum sibling episodes per initial prompt (G). When
              distinct_prompts_per_replica is given, defaults to ceil(concurrent episodes /
              Q). Otherwise defaults to the concurrent episodes per replica when
              shared_prefix_tokens equals prompt_tokens, and to 1 when it does not. When
              shared_prefix_tokens equals prompt_tokens, must be at least the concurrent
              episodes per replica.

          lora_enabled: Whether to estimate a resource that hosts LoRA sessions (true, default) or a
              single full-weight session (false), as in a model resource. The model and GPU
              type must support rollout estimates in this mode.

          shared_prefix_tokens: Leading tokens shared by all distinct initial prompts (H). Defaults to 0; cannot
              exceed prompt_tokens.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/rl/rollouts/estimate",
            body=maybe_transform(
                {
                    "added_tokens_per_turn": added_tokens_per_turn,
                    "base_model": base_model,
                    "concurrency": concurrency,
                    "episodes": episodes,
                    "generated_tokens_per_turn": generated_tokens_per_turn,
                    "prompt_tokens": prompt_tokens,
                    "turns": turns,
                    "compute_config": compute_config,
                    "distinct_prompts_per_replica": distinct_prompts_per_replica,
                    "episodes_per_prompt": episodes_per_prompt,
                    "lora_enabled": lora_enabled,
                    "shared_prefix_tokens": shared_prefix_tokens,
                },
                rollout_estimate_params.RolloutEstimateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EstimateRolloutResponse,
        )


class AsyncRolloutsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRolloutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRolloutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRolloutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRolloutsResourceWithStreamingResponse(self)

    async def estimate(
        self,
        *,
        added_tokens_per_turn: int,
        base_model: str,
        concurrency: int,
        episodes: int,
        generated_tokens_per_turn: int,
        prompt_tokens: int,
        turns: int,
        compute_config: rollout_estimate_params.ComputeConfig | Omit = omit,
        distinct_prompts_per_replica: int | Omit = omit,
        episodes_per_prompt: int | Omit = omit,
        lora_enabled: bool | Omit = omit,
        shared_prefix_tokens: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EstimateRolloutResponse:
        """
        Estimates rollout-only time, generator GPU-hours, billed GPU-hours of the whole
        model resource, and price for a supported model and GPU type. Each generator
        replica may contain several inference servers or span multiple nodes. Assumes
        identical episodes, exact reuse of generated tokens between turns, turns that
        start together within a replica, no environment delay, and no concurrent
        computation of the same initial prompt. Prompt-cache reuse and capacity misses
        are approximate, especially for multi-turn episodes. Rates are measured in the
        training mode reported by lora_enabled. Cache-transfer and request-preemption
        delays are not included, so long multi-turn rollouts with distinct prompts can
        take longer than estimated.

        Args:
          added_tokens_per_turn: Tokens added before each later turn (K), including the prior generated tokens
              followed by environment tokens. Must be at least generated_tokens_per_turn.

          base_model: Base model to estimate. The model, GPU type, and training mode must support
              rollout estimates.

          concurrency: Maximum concurrent episodes across all generator replicas (B). Must be positive.

          episodes: Total number of episodes (N). Must be between 1 and 10000000.

          generated_tokens_per_turn: Tokens generated on each turn (O). Must be positive.

          prompt_tokens: Initial prompt tokens per episode (P). Must be positive.

          turns: Assistant turns per episode (T). Must be between 1 and 1024.

          compute_config: Compute layout to estimate, as for a model resource. Omitted fields use the
              model's default GPU type and one generator replica (D); num_generator_replicas
              must be positive.

          distinct_prompts_per_replica: Number of distinct initial prompts among the concurrent episodes of one replica
              (Q). When episodes_per_prompt is given, defaults to ceil(concurrent episodes /
              G). Otherwise defaults to 1 when shared_prefix_tokens equals prompt_tokens, and
              to the concurrent episodes per replica when it does not. Must be 1 when
              shared_prefix_tokens equals prompt_tokens.

          episodes_per_prompt: Maximum sibling episodes per initial prompt (G). When
              distinct_prompts_per_replica is given, defaults to ceil(concurrent episodes /
              Q). Otherwise defaults to the concurrent episodes per replica when
              shared_prefix_tokens equals prompt_tokens, and to 1 when it does not. When
              shared_prefix_tokens equals prompt_tokens, must be at least the concurrent
              episodes per replica.

          lora_enabled: Whether to estimate a resource that hosts LoRA sessions (true, default) or a
              single full-weight session (false), as in a model resource. The model and GPU
              type must support rollout estimates in this mode.

          shared_prefix_tokens: Leading tokens shared by all distinct initial prompts (H). Defaults to 0; cannot
              exceed prompt_tokens.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/rl/rollouts/estimate",
            body=await async_maybe_transform(
                {
                    "added_tokens_per_turn": added_tokens_per_turn,
                    "base_model": base_model,
                    "concurrency": concurrency,
                    "episodes": episodes,
                    "generated_tokens_per_turn": generated_tokens_per_turn,
                    "prompt_tokens": prompt_tokens,
                    "turns": turns,
                    "compute_config": compute_config,
                    "distinct_prompts_per_replica": distinct_prompts_per_replica,
                    "episodes_per_prompt": episodes_per_prompt,
                    "lora_enabled": lora_enabled,
                    "shared_prefix_tokens": shared_prefix_tokens,
                },
                rollout_estimate_params.RolloutEstimateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EstimateRolloutResponse,
        )


class RolloutsResourceWithRawResponse:
    def __init__(self, rollouts: RolloutsResource) -> None:
        self._rollouts = rollouts

        self.estimate = to_raw_response_wrapper(
            rollouts.estimate,
        )


class AsyncRolloutsResourceWithRawResponse:
    def __init__(self, rollouts: AsyncRolloutsResource) -> None:
        self._rollouts = rollouts

        self.estimate = async_to_raw_response_wrapper(
            rollouts.estimate,
        )


class RolloutsResourceWithStreamingResponse:
    def __init__(self, rollouts: RolloutsResource) -> None:
        self._rollouts = rollouts

        self.estimate = to_streamed_response_wrapper(
            rollouts.estimate,
        )


class AsyncRolloutsResourceWithStreamingResponse:
    def __init__(self, rollouts: AsyncRolloutsResource) -> None:
        self._rollouts = rollouts

        self.estimate = async_to_streamed_response_wrapper(
            rollouts.estimate,
        )
