"""Tinker sampling interface backed by a Together RL session."""

from __future__ import annotations

from typing import Any
from functools import partial
from dataclasses import field, dataclass

from ._compat import types
from ._futures import _Pending
from .._payloads import resolve_result_payload
from ._converters import _to_model_input, _to_sample_response, _to_sampling_params
from .._operations import DEFAULT_OPERATION_INTERVAL
from ..clients.session import SessionClient
from ..clients.generator import _submit_sample_batch


@dataclass
class _PublishedWeights:
    version: int = 0


async def _resolve_sample(
    session: SessionClient,
    operation: Any,
    timeout: float | None,
    *,
    topk_prompt_logprobs: int,
) -> types.SampleResponse:
    output = await session._submit_and_wait(operation, timeout=timeout, interval=DEFAULT_OPERATION_INTERVAL)
    resolved = await resolve_result_payload(session._client, session_id=session.session_id, result=output)
    return _to_sample_response(resolved.results[0], topk_prompt_logprobs)


@dataclass(frozen=True)
class SamplingClient:
    _session: SessionClient
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)
    _version: int = 0

    def sample(
        self,
        prompt: types.ModelInput,
        num_samples: int,
        sampling_params: types.SamplingParams,
        include_prompt_logprobs: bool = False,
        topk_prompt_logprobs: int = 0,
    ) -> _Pending[types.SampleResponse]:
        if self._version != self._published_weights.version:
            raise RuntimeError(
                "This sampling client is stale because newer weights were published. "
                "Together's sampler serves the most recently published weights and snapshot "
                "checkpoints are not supported yet. Re-create the sampling client after each publish."
            )
        if not 0 <= topk_prompt_logprobs <= 20:
            raise ValueError("topk_prompt_logprobs must be between 0 and 20")

        session = self._session
        operation = session.run(
            _submit_sample_batch(
                session,
                model_inputs=[_to_model_input(prompt)],
                num_samples=num_samples,
                sampling_params=_to_sampling_params(sampling_params),
                prompt_logprobs=include_prompt_logprobs,
                topk_prompt_logprobs=topk_prompt_logprobs,
            )
        )
        resolve = partial(_resolve_sample, topk_prompt_logprobs=topk_prompt_logprobs)
        return _Pending(session, operation, resolve)
