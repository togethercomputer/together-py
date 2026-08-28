from __future__ import annotations

from typing import Any, cast, get_args
from dataclasses import dataclass
from collections.abc import Iterable

from .._loop import LoopGate, on_client_loop
from .session import SessionClient
from .._losses import FORWARD_INPUTS, validate_sample, validate_loss_config
from ....._types import omit
from .._payloads import prepare_operation_body, resolve_result_payload
from .._operations import DEFAULT_OPERATION_TIMEOUT, DEFAULT_OPERATION_INTERVAL
from .._request_types import Sample, LossConfig
from .....types.beta.rl.loss_type import LossType
from .....types.beta.rl.adam_params import AdamParams
from .....types.beta.rl.muon_params import MuonParams
from .....types.beta.rl.forward_result import ForwardResult
from .....types.beta.rl.weight_sync_type import WeightSyncType
from .....types.beta.rl.forward_operation import ForwardOperation
from .....types.beta.rl.optim_step_result import OptimStepResult
from .....types.beta.rl.weights_sync_result import WeightsSyncResult
from .....types.beta.rl.forward_backward_result import ForwardBackwardResult
from .....types.beta.rl.operation_forward_params import OperationForwardParams
from .....types.beta.rl.forward_backward_operation import ForwardBackwardOperation
from .....types.beta.rl.custom_forward_backward_result import CustomForwardBackwardResult
from .....types.beta.rl.custom_forward_backward_operation import CustomForwardBackwardOperation
from .....types.beta.rl.operation_forward_backward_params import OperationForwardBackwardParams
from .....types.beta.rl.operation_custom_forward_backward_params import Gradient, OperationCustomForwardBackwardParams

_PROTO_LOSS_TYPE_BY_SHORT_NAME: dict[str, LossType] = {
    proto.removeprefix("LOSS_TYPE_").lower(): proto for proto in get_args(LossType)
}


def _resolve_loss_type(loss: LossConfig) -> LossConfig:
    """Expand a short loss name (``"ppo"``) into its proto spelling, if it is one.

    An unrecognized name is returned untouched so that `validate_loss_config` raises the
    one error naming the one accepted vocabulary.
    """
    given = cast("str | None", loss.get("type"))
    proto = _PROTO_LOSS_TYPE_BY_SHORT_NAME.get(given) if given is not None else None
    return {**loss, "type": proto} if proto is not None else loss


async def _submit_forward_backward(
    session: SessionClient,
    *,
    samples: Iterable[Sample],
    loss: LossConfig,
) -> ForwardBackwardOperation:
    """POST a forward_backward operation without waiting for it."""
    batch = list(samples)
    proto_loss = _resolve_loss_type(loss)
    spec = validate_loss_config(proto_loss)
    for index, sample in enumerate(batch):
        validate_sample(sample, spec, label=f"samples[{index}]")
    body, large_payload_id = await prepare_operation_body(
        session._client,
        session_id=session._session_id,
        body={"loss": proto_loss, "samples": batch},
        expected_type=OperationForwardBackwardParams,
    )
    extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
    return await session._client.beta.rl.operations.forward_backward(
        session._session_id,
        loss=proto_loss,
        samples=cast("list[Any]", body["samples"]),
        extra_body=extra_body,
    )


async def _submit_forward(
    session: SessionClient,
    *,
    samples: Iterable[Sample],
) -> ForwardOperation:
    """POST a forward operation without waiting for it."""
    batch = list(samples)
    for index, sample in enumerate(batch):
        validate_sample(sample, FORWARD_INPUTS, label=f"samples[{index}]")
    body, large_payload_id = await prepare_operation_body(
        session._client,
        session_id=session._session_id,
        body={"samples": batch},
        expected_type=OperationForwardParams,
    )
    extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
    return await session._client.beta.rl.operations.forward(
        session._session_id,
        samples=cast("list[Any]", body["samples"]),
        extra_body=extra_body,
    )


async def _submit_custom_forward_backward(
    session: SessionClient,
    *,
    samples: Iterable[Sample],
    gradients: Iterable[Gradient],
) -> CustomForwardBackwardOperation:
    """POST a custom_forward_backward operation without waiting for it."""
    batch = list(samples)
    for index, sample in enumerate(batch):
        validate_sample(sample, FORWARD_INPUTS, label=f"samples[{index}]")
    body, large_payload_id = await prepare_operation_body(
        session._client,
        session_id=session._session_id,
        body={"samples": batch, "gradients": list(gradients)},
        expected_type=OperationCustomForwardBackwardParams,
    )
    extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
    return await session._client.beta.rl.operations.custom_forward_backward(
        session._session_id,
        samples=cast("list[Any]", body["samples"]),
        gradients=cast("list[Any]", body["gradients"]),
        extra_body=extra_body,
    )


@dataclass(frozen=True)
class Trainer:
    _session: SessionClient

    @property
    def session_id(self) -> str:
        return self._session.session_id

    @property
    def _loop(self) -> LoopGate:
        return self._session._loop

    def forward(
        self,
        *,
        samples: Iterable[Sample],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardResult:
        return self._session.run(self.forward_async(samples=samples, timeout=timeout, interval=interval))

    @on_client_loop
    async def forward_async(
        self,
        *,
        samples: Iterable[Sample],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardResult:
        operation = await _submit_forward(self._session, samples=samples)
        result = await self._session._submit_and_wait(operation, timeout=timeout, interval=interval)
        return await resolve_result_payload(
            self._session._client,
            session_id=self._session._session_id,
            result=cast(ForwardResult, result),
        )

    def forward_backward(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfig,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        return self._session.run(
            self.forward_backward_async(
                samples=samples,
                loss=loss,
                timeout=timeout,
                interval=interval,
            )
        )

    @on_client_loop
    async def forward_backward_async(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfig,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        operation = await _submit_forward_backward(self._session, samples=samples, loss=loss)
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(ForwardBackwardResult, result)

    def custom_forward_backward(
        self,
        *,
        samples: Iterable[Sample],
        gradients: Iterable[Gradient],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> CustomForwardBackwardResult:
        return self._session.run(
            self.custom_forward_backward_async(
                samples=samples,
                gradients=gradients,
                timeout=timeout,
                interval=interval,
            )
        )

    @on_client_loop
    async def custom_forward_backward_async(
        self,
        *,
        samples: Iterable[Sample],
        gradients: Iterable[Gradient],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> CustomForwardBackwardResult:
        operation = await _submit_custom_forward_backward(self._session, samples=samples, gradients=gradients)
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(CustomForwardBackwardResult, result)

    def optim_step(
        self,
        *,
        adam_params: AdamParams | None = None,
        muon_params: MuonParams | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> OptimStepResult:
        return self._session.run(
            self.optim_step_async(
                adam_params=adam_params,
                muon_params=muon_params,
                timeout=timeout,
                interval=interval,
            )
        )

    @on_client_loop
    async def optim_step_async(
        self,
        *,
        adam_params: AdamParams | None = None,
        muon_params: MuonParams | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> OptimStepResult:
        operation = await self._session._client.beta.rl.operations.optim_step(
            self._session._session_id,
            adam_params=adam_params if adam_params is not None else omit,
            muon_params=muon_params if muon_params is not None else omit,
        )
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(OptimStepResult, result)

    def weights_sync(
        self,
        *,
        weight_sync_type: WeightSyncType,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> WeightsSyncResult:
        return self._session.run(
            self.weights_sync_async(
                weight_sync_type=weight_sync_type,
                timeout=timeout,
                interval=interval,
            )
        )

    @on_client_loop
    async def weights_sync_async(
        self,
        *,
        weight_sync_type: WeightSyncType,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> WeightsSyncResult:
        operation = await self._session._client.beta.rl.operations.weights_sync(
            self._session._session_id,
            weight_sync_type=weight_sync_type,
        )
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(WeightsSyncResult, result)
