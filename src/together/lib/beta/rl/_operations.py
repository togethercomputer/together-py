from __future__ import annotations

import time
import random
import asyncio
import logging
from typing import Union, Iterator
from typing_extensions import TypeAlias

from ...._client import AsyncTogether
from ...._exceptions import APIStatusError, APIConnectionError
from ....types.beta.rl.sample_operation import SampleOperation
from ....types.beta.rl.forward_operation import ForwardOperation
from ....types.beta.rl.optim_step_operation import OptimStepOperation
from ....types.beta.rl.forward_backward_operation import ForwardBackwardOperation
from ....types.beta.rl.training_checkpoint_operation import TrainingCheckpointOperation
from ....types.beta.rl.inference_checkpoint_operation import InferenceCheckpointOperation
from ....types.beta.rl.custom_forward_backward_operation import CustomForwardBackwardOperation

OperationResponse: TypeAlias = Union[
    ForwardOperation,
    ForwardBackwardOperation,
    CustomForwardBackwardOperation,
    OptimStepOperation,
    SampleOperation,
    InferenceCheckpointOperation,
    TrainingCheckpointOperation,
]

logger = logging.getLogger("together")

_COMPLETED = "TRAINING_OPERATION_STATUS_COMPLETED"
_FAILED = "TRAINING_OPERATION_STATUS_FAILED"

_BACKOFF_FACTOR = 2.0
_MAX_POLL_INTERVAL = 2.0
_TRANSIENT_STATUS_CODES = frozenset({408, 409, 429})


async def async_retrieve_operation(
    client: AsyncTogether,
    *,
    session_id: str,
    operation: OperationResponse,
) -> OperationResponse:
    if isinstance(operation, ForwardOperation):
        return await client.beta.rl.operations.retrieve_forward(
            operation_id=operation.id,
            session_id=session_id,
        )
    if isinstance(operation, ForwardBackwardOperation):
        return await client.beta.rl.operations.retrieve_forward_backward(
            operation_id=operation.id,
            session_id=session_id,
        )
    if isinstance(operation, CustomForwardBackwardOperation):
        return await client.beta.rl.operations.retrieve_custom_forward_backward(
            operation_id=operation.id,
            session_id=session_id,
        )
    if isinstance(operation, OptimStepOperation):
        return await client.beta.rl.operations.retrieve_optim_step(
            operation_id=operation.id,
            session_id=session_id,
        )
    if isinstance(operation, SampleOperation):
        return await client.beta.rl.operations.retrieve_sample(
            operation_id=operation.id,
            session_id=session_id,
        )
    if isinstance(operation, InferenceCheckpointOperation):
        return await client.beta.rl.operations.retrieve_inference_checkpoint(
            operation_id=operation.id,
            session_id=session_id,
        )
    return await client.beta.rl.operations.retrieve_training_checkpoint(
        operation_id=operation.id,
        session_id=session_id,
    )


def _poll_delays(initial: float) -> Iterator[float]:
    """Sleep durations between polls: exponential growth up to `_MAX_POLL_INTERVAL`,
    jittered so operations dispatched together don't poll in lockstep."""
    interval = initial
    while True:
        yield random.uniform(interval / 2, interval)
        interval = min(interval * _BACKOFF_FACTOR, _MAX_POLL_INTERVAL)


def _is_transient(exc: Exception) -> bool:
    """Whether a failed poll means "not ready yet" rather than "the operation failed"."""
    if isinstance(exc, APIStatusError):
        return exc.status_code in _TRANSIENT_STATUS_CODES or exc.status_code >= 500
    return isinstance(exc, APIConnectionError)


async def async_wait_for_operation(
    client: AsyncTogether,
    *,
    session_id: str,
    operation: OperationResponse,
    timeout: float | None,
    interval: float,
) -> OperationResponse:
    """Poll until the operation completes, `timeout` elapses, or it genuinely fails."""
    deadline = None if timeout is None else time.monotonic() + timeout
    delays = _poll_delays(interval)
    current = operation
    last_transient: Exception | None = None

    while True:
        if current.status == _FAILED:
            raise RuntimeError(f"Operation ({current.id}) failed: {current.error}")
        if current.status == _COMPLETED:
            return current
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("Timed out waiting for operation to complete") from last_transient

        await asyncio.sleep(next(delays))

        try:
            current = await async_retrieve_operation(
                client,
                session_id=session_id,
                operation=current,
            )
        except Exception as exc:
            if not _is_transient(exc):
                raise
            last_transient = exc
            logger.debug("Transient error polling operation (%s), retrying: %s", current.id, exc)
