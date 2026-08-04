"""Tinker-shaped clients backed by a Together RL session."""

from __future__ import annotations

import sys
import atexit
import signal
import warnings
from typing import Any, Sequence
from dataclasses import dataclass

from .. import ModelResourcesClient, ForwardBackwardResult
from ._compat import types
from ._futures import _Pending
from .._payloads import resolve_result_payload
from ._converters import (
    _to_sample,
    _to_adam_params,
    _to_model_input,
    _loss_inputs_key,
    _to_sample_response,
    _to_sampling_params,
)
from ..clients.session import DEFAULT_OPERATION_INTERVAL, SessionClient
from ..clients.sampling import submit_sample_batch
from ..clients.training import _resolve_loss_type, submit_forward_backward


async def _wait(session: SessionClient, operation: Any) -> Any:
    # timeout=None: tinker futures wait indefinitely, and a long rollout easily
    # outlives the SDK's default 300 s operation deadline.
    return await session._submit_and_wait(operation, timeout=None, interval=DEFAULT_OPERATION_INTERVAL)


async def _resolve_sample(session: SessionClient, operation: Any) -> types.SampleResponse:
    output = await _wait(session, operation)
    resolved = await resolve_result_payload(session._client, session_id=session.session_id, result=output)
    return _to_sample_response(resolved.results[0])


async def _resolve_optim_step(session: SessionClient, operation: Any) -> types.OptimStepResponse:
    await _wait(session, operation)
    # The wire result carries only the step number; tinker's response carries only
    # optional metrics, which are empty on both backends.
    return types.OptimStepResponse()


@dataclass(frozen=True)
class SamplingClient:
    _session: SessionClient

    def sample(
        self,
        prompt: types.ModelInput,
        num_samples: int,
        sampling_params: types.SamplingParams,
    ) -> _Pending[types.SampleResponse]:
        session = self._session
        operation = session.run(
            submit_sample_batch(
                session,
                model_inputs=[_to_model_input(prompt)],
                num_samples=num_samples,
                sampling_params=_to_sampling_params(sampling_params),
            )
        )
        return _Pending(session, operation, _resolve_sample)


@dataclass(frozen=True)
class TrainingClient:
    _session: SessionClient

    def forward_backward(self, data: Sequence[types.Datum], loss_fn: str) -> _Pending[ForwardBackwardResult]:
        session = self._session
        loss = _resolve_loss_type({"type": loss_fn})  # accepts tinker's short names, e.g. "importance_sampling"
        samples = [_to_sample(datum, _loss_inputs_key(loss["type"])) for datum in data]
        operation = session.run(submit_forward_backward(session, samples=samples, loss=loss))
        return _Pending(session, operation, _wait)

    def optim_step(self, adam_params: types.AdamParams) -> _Pending[types.OptimStepResponse]:
        session = self._session
        operation = session.run(
            session._client.beta.rl.operations.optim_step(
                session.session_id,
                # SYNCHRONOUS publishes the updated weights before the operation completes,
                # which is what makes save_weights_and_get_sampling_client a pure handle.
                # BACKGROUND_PUBLISH would silently turn the loop off-policy.
                weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
                adam_params=_to_adam_params(adam_params),
            )
        )
        return _Pending(session, operation, _resolve_optim_step)

    def save_weights_and_get_sampling_client(self, name: str | None = None) -> SamplingClient:
        # Weights were already published by optim_step's SYNCHRONOUS sync; tinker's
        # `name` is deprecated on their side too.
        del name
        return SamplingClient(self._session)


class ServiceClient:
    """Mirrors ``tinker.ServiceClient``; tinker-only kwargs like ``user_metadata`` are ignored."""

    def __init__(self, *, base_url: str | None = None, api_key: str | None = None, **_: Any) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def create_lora_training_client(self, base_model: str, rank: int = 32, **kwargs: Any) -> TrainingClient:
        ignored = {"seed", "train_mlp", "train_attn", "train_unembed"} & kwargs.keys()
        if ignored:
            warnings.warn(
                f"Together ignores {sorted(ignored)}: seeding and per-module training selection"
                " are not configurable, so runs will not reproduce tinker behavior exactly",
                stacklevel=2,
            )
        _exit_on_sigterm()
        model_resources = ModelResourcesClient.create(
            base_model=base_model,
            api_key=self._api_key,
            base_url=self._base_url,
        )
        session = model_resources.create_session(lora_config={"rank": rank})
        _stop_on_exit(session, model_resources)
        return TrainingClient(session)


_sigterm_translated = False


def _exit_on_sigterm() -> None:
    """Translate SIGTERM into SystemExit so cleanup actually runs.

    The default disposition kills the process without running atexit hooks or letting an
    in-flight wait unwind into its cleanup; SystemExit does both. Installed before
    provisioning starts, because the hour-long READY wait is the likeliest window for a
    scheduler's SIGTERM — dying there leaks a half-provisioned GPU resource. A handler
    the host application already installed still runs first; an explicit SIG_IGN wins.
    """
    global _sigterm_translated
    if _sigterm_translated:
        return
    _sigterm_translated = True
    previous = signal.getsignal(signal.SIGTERM)
    if previous is signal.SIG_IGN:
        return

    def handler(signum: int, frame: Any) -> None:
        if callable(previous):
            previous(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, handler)


def _stop_on_exit(session: SessionClient, model_resources: ModelResourcesClient) -> None:
    """Release the GPUs at interpreter exit — the tinker loop never stops anything itself."""

    def stop() -> None:
        try:
            session.stop()
        finally:
            model_resources.stop()

    atexit.register(stop)
