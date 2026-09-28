from __future__ import annotations

from uuid import uuid4
from typing import Any, cast, get_args
from dataclasses import dataclass
from collections.abc import Iterable

from .._loop import LoopGate, on_client_loop
from .session import SessionClient
from .._arrays import coerce_sample, coerce_gradient
from .._losses import CUSTOM_FORWARD_BACKWARD_INPUTS, InputSpec, validate_sample, validate_loss_config
from ....._types import Omit, omit
from .._payloads import prepare_operation_body, resolve_result_payload
from .._operations import DEFAULT_OPERATION_TIMEOUT, DEFAULT_OPERATION_INTERVAL
from .._request_types import Sample, LossConfig
from .....types.beta.rl.loss_type import LossType
from .....types.beta.rl.adam_params import AdamParams
from .....types.beta.rl.muon_params import MuonParams
from .....types.beta.rl.weight_sync_type import WeightSyncType
from .....types.beta.rl.optim_step_result import OptimStepResult
from .....types.beta.rl.weights_sync_result import WeightsSyncResult
from .....types.beta.rl.forward_backward_result import ForwardBackwardResult
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


def _coerce_batch(samples: Iterable[Sample], inputs: InputSpec) -> list[Sample]:
    """Coerce every sample into its wire shape and validate it.

    Both passes walk the same tensors, so they share one ``samples[i]`` label and an error
    from either names the same sample.
    """
    batch: list[Sample] = []
    for index, sample in enumerate(samples):
        label = f"samples[{index}]"
        coerced = coerce_sample(sample, label)
        validate_sample(coerced, inputs, label=label)
        batch.append(coerced)
    return batch


async def _submit_forward_backward(
    session: SessionClient,
    *,
    samples: Iterable[Sample],
    loss: LossConfig,
    forward_only: bool | Omit = omit,
    return_loss_fn_outputs: bool | Omit = omit,
) -> ForwardBackwardOperation:
    """POST a forward_backward operation without waiting for it.

    The two flags are independent: ``forward_only`` scores the batch without accumulating
    gradients, and ``return_loss_fn_outputs`` returns the per-sample output tensors. Either
    can be used without the other.
    """
    proto_loss = _resolve_loss_type(loss)
    batch = _coerce_batch(samples, validate_loss_config(proto_loss))
    body, large_payload_id = await prepare_operation_body(
        session._client,
        session_id=session._session_id,
        body={"loss": proto_loss, "samples": batch},
        expected_type=OperationForwardBackwardParams,
    )
    extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
    return await session._client.beta.rl.operations.forward_backward(
        session._session_id,
        idempotency_key=str(uuid4()),
        loss=proto_loss,
        samples=cast("list[Any]", body["samples"]),
        forward_only=forward_only,
        return_loss_fn_outputs=return_loss_fn_outputs,
        extra_body=extra_body,
    )


async def _submit_custom_forward_backward(
    session: SessionClient,
    *,
    samples: Iterable[Sample],
    gradients: Iterable[Gradient],
) -> CustomForwardBackwardOperation:
    """POST a custom_forward_backward operation without waiting for it."""
    batch = _coerce_batch(samples, CUSTOM_FORWARD_BACKWARD_INPUTS)
    body, large_payload_id = await prepare_operation_body(
        session._client,
        session_id=session._session_id,
        body={
            "samples": batch,
            "gradients": [coerce_gradient(gradient, f"gradients[{index}]") for index, gradient in enumerate(gradients)],
        },
        expected_type=OperationCustomForwardBackwardParams,
    )
    extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
    return await session._client.beta.rl.operations.custom_forward_backward(
        session._session_id,
        idempotency_key=str(uuid4()),
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
        loss: LossConfig,
        return_loss_fn_outputs: bool = True,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        """Score a batch without accumulating gradients, reading back its per-token logprobs.

        The logprobs land in ``loss_fn_outputs[i].tensors["logprobs"]``. ``loss`` decides
        what they mean: a position the loss excludes, such as a zero-weight one, comes back
        masked to zero rather than a true log-probability.
        """
        return self._session.run(
            self.forward_async(
                samples=samples,
                loss=loss,
                return_loss_fn_outputs=return_loss_fn_outputs,
                timeout=timeout,
                interval=interval,
            )
        )

    @on_client_loop
    async def forward_async(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfig,
        return_loss_fn_outputs: bool = True,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        """See :meth:`forward`."""
        operation = await _submit_forward_backward(
            self._session,
            samples=samples,
            loss=loss,
            forward_only=True,
            return_loss_fn_outputs=return_loss_fn_outputs,
        )
        result = await self._session._submit_and_wait(operation, timeout=timeout, interval=interval)
        return await resolve_result_payload(
            self._session._client,
            session_id=self._session._session_id,
            result=cast(ForwardBackwardResult, result),
        )

    def forward_backward(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfig,
        return_loss_fn_outputs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        """Accumulate gradients over a batch, optionally reading back its per-token logprobs.

        Set ``return_loss_fn_outputs`` to receive ``loss_fn_outputs[i].tensors["logprobs"]``
        alongside the gradient update, subject to the same masking as :meth:`forward`.
        """
        return self._session.run(
            self.forward_backward_async(
                samples=samples,
                loss=loss,
                return_loss_fn_outputs=return_loss_fn_outputs,
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
        return_loss_fn_outputs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        """See :meth:`forward_backward`."""
        operation = await _submit_forward_backward(
            self._session,
            samples=samples,
            loss=loss,
            return_loss_fn_outputs=return_loss_fn_outputs if return_loss_fn_outputs is not None else omit,
        )
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return await resolve_result_payload(
            self._session._client,
            session_id=self._session._session_id,
            result=cast(ForwardBackwardResult, result),
        )

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
            idempotency_key=str(uuid4()),
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
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
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
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> WeightsSyncResult:
        operation = await self._session._client.beta.rl.operations.weights_sync(
            self._session._session_id,
            idempotency_key=str(uuid4()),
            weight_sync_type=weight_sync_type,
        )
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(WeightsSyncResult, result)
