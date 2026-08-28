"""Tinker training interface backed by a Together RL session."""

from __future__ import annotations

import warnings
from types import TracebackType
from typing import Any
from dataclasses import field, dataclass

from ._compat import types
from ._futures import _Pending
from ._sampling import SamplingClient, _PublishedWeights
from ._teardown import _Lifecycle
from ._converters import (
    _to_sample,
    _to_adam_params,
    _to_loss_config,
    _warn_on_binarized_weights,
    _to_forward_backward_output,
)
from .._operations import DEFAULT_OPERATION_INTERVAL
from ..clients.session import SessionClient
from ..clients.trainer import _submit_forward_backward
from .....types.beta.rl.forward_backward_result import ForwardBackwardResult


async def _wait(session: SessionClient, operation: Any, timeout: float | None) -> Any:
    return await session._submit_and_wait(operation, timeout=timeout, interval=DEFAULT_OPERATION_INTERVAL)


async def _resolve_forward_backward(
    session: SessionClient, operation: Any, timeout: float | None
) -> types.ForwardBackwardOutput:
    result = await _wait(session, operation, timeout)
    return _to_forward_backward_output(ForwardBackwardResult.model_validate(result))


async def _resolve_optim_step(session: SessionClient, operation: Any, timeout: float | None) -> types.OptimStepResponse:
    await _wait(session, operation, timeout)
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

    def close(self) -> None:
        assert self._lifecycle is not None
        self._lifecycle.close()

    def forward_backward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
    ) -> _Pending[types.ForwardBackwardOutput]:
        session = self._session
        # Config first: it is O(1) and rejects a misspelled key before the batch-sized
        # conversion below runs. The converters re-check keys and dtypes that
        # `_submit_forward_backward` checks again for native callers; the pass is
        # deliberate, so tinker users get Datum-worded errors rather than `samples[i]`.
        loss = _to_loss_config(loss_fn, loss_fn_config)
        samples = [_to_sample(datum, loss_fn) for datum in data]
        _warn_on_binarized_weights(samples, loss_fn)
        operation = session.run(_submit_forward_backward(session, samples=samples, loss=loss))
        return _Pending(session, operation, _resolve_forward_backward)

    def optim_step(self, adam_params: types.AdamParams) -> _Pending[types.OptimStepResponse]:
        session = self._session
        operation = session.run(
            session._client.beta.rl.operations.optim_step(
                session.session_id,
                adam_params=_to_adam_params(adam_params),
            )
        )
        return _Pending(session, operation, _resolve_optim_step)

    def save_weights_and_get_sampling_client(
        self,
        name: str | None = None,
        retry_config: Any = None,
    ) -> SamplingClient:
        ignored: list[str] = []
        if name is not None:
            ignored.append("name")
        if retry_config is not None:
            ignored.append("retry_config")
        if ignored:
            warnings.warn(
                f"Together ignores {ignored}: weight publish is a synchronous sync with "
                "no named checkpoints or caller-controlled retries",
                stacklevel=2,
            )
        session = self._session
        operation = session.run(
            session._client.beta.rl.operations.weights_sync(
                session.session_id,
                weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            )
        )
        session.run(_wait(session, operation, None))
        self._published_weights.version += 1
        return SamplingClient(session, self._published_weights, self._published_weights.version)
