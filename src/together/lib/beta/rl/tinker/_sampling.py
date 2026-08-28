"""Tinker sampling interface backed by a Together RL session."""

from __future__ import annotations

from functools import partial
from dataclasses import field, dataclass

from .. import SamplingParams as WireSamplingParams
from ._compat import types
from .._futures import OperationFuture
from .._payloads import resolve_result_payload
from ._converters import _to_model_input, _to_sample_response, _to_sampling_params
from .._operations import OperationResponse, require_output
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
    resolved = await resolve_result_payload(
        session._client,
        session_id=session.session_id,
        result=require_output(completed.output, operation=completed),
    )
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


@dataclass(frozen=True)
class SamplingClient:
    _session: SessionClient
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)
    _version: int = 0

    def _check_fresh(self) -> None:
        if self._version != self._published_weights.version:
            raise RuntimeError(
                "This sampling client is stale because newer weights were published. "
                "Together's sampler serves the most recently published weights and snapshot "
                "checkpoints are not supported yet. Re-create the sampling client after each publish."
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
