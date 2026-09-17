"""Tinker sampling interface backed by a Together RL session."""

from __future__ import annotations

from functools import partial
from dataclasses import field, dataclass

from .. import SamplingParams as WireSamplingParams
from ._compat import types
from .._futures import OperationFuture
from .._payloads import resolve_operation_payload
from ._converters import (
    _to_model_input,
    _to_sample_response,
    _to_sampling_params,
    _to_compute_logprobs,
)
from .._operations import OperationResponse
from ..clients.session import SessionClient
from ..clients.generator import _submit_sample_batch
from .....types.beta.rl.model_input_param import ModelInput as WireModelInput

_MAX_TOPK_PROMPT_LOGPROBS = 20


@dataclass
class _PublishedWeights:
    version: int = 0


async def _resolve_sample(
    completed: OperationResponse,
    *,
    session: SessionClient,
    topk_prompt_logprobs: int,
) -> types.SampleResponse:
    resolved = await resolve_operation_payload(completed, session=session)
    return _to_sample_response(resolved.results[0], topk_prompt_logprobs)


def _to_sample_request(
    prompt: types.ModelInput,
    sampling_params: types.SamplingParams,
    topk_prompt_logprobs: int,
) -> tuple[WireModelInput, WireSamplingParams]:
    """Render one sample call's wire payload, rejecting an out-of-range top-k.

    Kept out of the submission coroutine so the error raises on the caller's own frame,
    where a pinned or stopped session cannot mask it with its own error, and so the
    dropped-token-stop warning is emitted under the caller's warning filters rather than
    on the shared process-loop thread.
    """
    if not 0 <= topk_prompt_logprobs <= _MAX_TOPK_PROMPT_LOGPROBS:
        raise ValueError(f"topk_prompt_logprobs must be between 0 and {_MAX_TOPK_PROMPT_LOGPROBS}")
    return _to_model_input(prompt), _to_sampling_params(sampling_params)


async def _resolve_compute_logprobs(completed: OperationResponse, *, session: SessionClient) -> list[float | None]:
    resolved = await resolve_operation_payload(completed, session=session)
    result = resolved.results[0] if resolved.results else None
    if result is None or result.prompt_logprobs is None:
        raise RuntimeError("Sample result did not include prompt logprobs; the generator may not support them")
    return _to_compute_logprobs(result.prompt_logprobs)


@dataclass(frozen=True)
class SamplingClient:
    _session: SessionClient
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)
    _version: int = 0
    _allow_stale: bool = True

    def _check_fresh(self) -> None:
        """Reject a client whose weights have been superseded, unless the caller opted out."""
        if self._allow_stale:
            return
        if self._version != self._published_weights.version:
            raise RuntimeError(
                "This sampling client is stale because newer weights were published. "
                "Together's sampler serves the most recently published weights and snapshot "
                "checkpoints are not supported yet. Re-create the sampling client after each "
                "publish, or pass allow_stale=True to save_weights_and_get_sampling_client to "
                "sample from whatever weights are live."
            )

    def sample(
        self,
        prompt: types.ModelInput,
        num_samples: int,
        sampling_params: types.SamplingParams,
        include_prompt_logprobs: bool = False,
        topk_prompt_logprobs: int = 0,
    ) -> OperationFuture[types.SampleResponse]:
        self._check_fresh()
        model_input, params = _to_sample_request(prompt, sampling_params, topk_prompt_logprobs)
        return self._session.run(
            self._submit_sample_async(
                model_input,
                params,
                num_samples=num_samples,
                include_prompt_logprobs=include_prompt_logprobs,
                topk_prompt_logprobs=topk_prompt_logprobs,
            )
        )

    async def sample_async(
        self,
        prompt: types.ModelInput,
        num_samples: int,
        sampling_params: types.SamplingParams,
        include_prompt_logprobs: bool = False,
        topk_prompt_logprobs: int = 0,
    ) -> types.SampleResponse:
        self._check_fresh()
        model_input, params = _to_sample_request(prompt, sampling_params, topk_prompt_logprobs)
        future = await self._submit_sample_async(
            model_input,
            params,
            num_samples=num_samples,
            include_prompt_logprobs=include_prompt_logprobs,
            topk_prompt_logprobs=topk_prompt_logprobs,
        )
        return await future

    async def _submit_sample_async(
        self,
        model_input: WireModelInput,
        sampling_params: WireSamplingParams,
        *,
        num_samples: int,
        include_prompt_logprobs: bool,
        topk_prompt_logprobs: int,
    ) -> OperationFuture[types.SampleResponse]:
        session = self._session
        operation = await session.run_async(
            _submit_sample_batch(
                session,
                model_inputs=[model_input],
                num_samples=num_samples,
                sampling_params=sampling_params,
                prompt_logprobs=include_prompt_logprobs,
                topk_prompt_logprobs=topk_prompt_logprobs,
            )
        )
        resolve = partial(_resolve_sample, session=session, topk_prompt_logprobs=topk_prompt_logprobs)
        return OperationFuture(session, operation, resolve)

    def compute_logprobs(self, prompt: types.ModelInput) -> OperationFuture[list[float | None]]:
        self._check_fresh()
        return self._session.run(self._submit_compute_logprobs_async(prompt))

    async def compute_logprobs_async(self, prompt: types.ModelInput) -> list[float | None]:
        self._check_fresh()
        future = await self._submit_compute_logprobs_async(prompt)
        return await future

    async def _submit_compute_logprobs_async(self, prompt: types.ModelInput) -> OperationFuture[list[float | None]]:
        session = self._session
        # Same mechanism as native SamplingClient.compute_logprobs: sample with
        # max_tokens=1 and prompt_logprobs=True, then reshape the first token to None.
        operation = await session.run_async(
            _submit_sample_batch(
                session,
                model_inputs=[_to_model_input(prompt)],
                num_samples=1,
                sampling_params=WireSamplingParams(max_tokens=1),
                prompt_logprobs=True,
            )
        )
        resolve = partial(_resolve_compute_logprobs, session=session)
        return OperationFuture(session, operation, resolve)
