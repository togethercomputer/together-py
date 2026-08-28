"""Tinker training interface backed by a Together RL session."""

from __future__ import annotations

import warnings
from types import TracebackType
from typing import Any
from dataclasses import field, dataclass

from .. import Sample as WireSample, LossConfig as WireLossConfig
from ._compat import types
from .._futures import OperationFuture
from ._sampling import SamplingClient, _PublishedWeights
from ._teardown import _Lifecycle
from ._converters import (
    _to_sample,
    _to_adam_params,
    _to_loss_config,
    _warn_on_binarized_weights,
    _to_forward_backward_output,
)
from .._operations import OperationResponse, require_output
from ..clients.session import SessionClient
from ..clients.trainer import _submit_forward_backward
from .....types.beta.rl.forward_backward_result import ForwardBackwardResult


def _to_forward_backward_request(
    data: list[types.Datum],
    loss_fn: types.LossFnType,
    loss_fn_config: dict[str, float] | None,
) -> tuple[list[WireSample], WireLossConfig]:
    """Render one forward_backward call's wire payload, rejecting caller mistakes.

    Kept out of the submission coroutine so a bad ``loss_fn`` or ``Datum`` raises on the
    caller's own frame; deferred, it would surface through the shared process loop, where a
    pinned or stopped session masks it with its own error.
    """
    loss = _to_loss_config(loss_fn, loss_fn_config)
    samples = [_to_sample(datum, loss_fn) for datum in data]
    _warn_on_binarized_weights(samples, loss_fn)
    return samples, loss


def _warn_ignored_publish_args(name: str | None, retry_config: Any) -> None:
    ignored = [arg for arg, value in (("name", name), ("retry_config", retry_config)) if value is not None]
    if ignored:
        warnings.warn(
            f"Together ignores {ignored}: weight publish is a synchronous sync with "
            "no named checkpoints or caller-controlled retries",
            stacklevel=2,
        )


async def _resolve_forward_backward(completed: OperationResponse) -> types.ForwardBackwardOutput:
    output = require_output(completed.output, operation=completed)
    return _to_forward_backward_output(ForwardBackwardResult.model_validate(output))


async def _resolve_optim_step(completed: OperationResponse) -> types.OptimStepResponse:
    # optim_step legitimately completes with no output; there is nothing to read back.
    del completed
    return types.OptimStepResponse()


@dataclass
class TrainingClient:
    _session: SessionClient
    _lifecycle: _Lifecycle | None = None
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)

    def __post_init__(self) -> None:
        if self._lifecycle is None:
            self._lifecycle = _Lifecycle(self._session)

    def __enter__(self) -> TrainingClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    async def __aenter__(self) -> TrainingClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close_async()

    def close(self) -> None:
        assert self._lifecycle is not None
        self._lifecycle.close()

    async def close_async(self) -> None:
        assert self._lifecycle is not None
        await self._lifecycle.aclose()

    def forward_backward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return self._session.run(self._submit_forward_backward_async(samples, loss))

    async def forward_backward_async(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return await self._submit_forward_backward_async(samples, loss)

    async def _submit_forward_backward_async(
        self, samples: list[WireSample], loss: WireLossConfig
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        session = self._session
        operation = await session.run_async(_submit_forward_backward(session, samples=samples, loss=loss))
        return OperationFuture(session, operation, _resolve_forward_backward)

    def optim_step(self, adam_params: types.AdamParams) -> OperationFuture[types.OptimStepResponse]:
        # Drives its own twin, unlike the pairs above: there is nothing to validate on the
        # caller's frame first, so there is no shared submit helper to split out.
        return self._session.run(self.optim_step_async(adam_params))

    async def optim_step_async(self, adam_params: types.AdamParams) -> OperationFuture[types.OptimStepResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.beta.rl.operations.optim_step(
                session.session_id,
                adam_params=_to_adam_params(adam_params),
            )
        )
        return OperationFuture(session, operation, _resolve_optim_step)

    def save_weights_and_get_sampling_client(
        self,
        name: str | None = None,
        retry_config: Any = None,
    ) -> SamplingClient:
        _warn_ignored_publish_args(name, retry_config)
        return self._session.run(self._publish_weights_async())

    async def save_weights_and_get_sampling_client_async(
        self,
        name: str | None = None,
        retry_config: Any = None,
    ) -> SamplingClient:
        _warn_ignored_publish_args(name, retry_config)
        return await self._publish_weights_async()

    async def _publish_weights_async(self) -> SamplingClient:
        session = self._session
        # timeout=None: publish waits as long as the sync takes, unlike Trainer's 300s default.
        await session.trainer.weights_sync_async(weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS", timeout=None)
        self._published_weights.version += 1
        return SamplingClient(session, self._published_weights, self._published_weights.version)
