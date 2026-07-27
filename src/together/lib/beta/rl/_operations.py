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

_MAX_POLL_INTERVAL = 5.0


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
    """Waits between successive polls, doubling up to `_MAX_POLL_INTERVAL`.

    The jitter matters as much as the growth: a batch of operations dispatched together
    would otherwise poll in lockstep and reach the API as a synchronized spike.
    """
    interval = initial
    while True:
        yield random.uniform(interval / 2, interval)
        interval = min(interval * 2, _MAX_POLL_INTERVAL)


def _means_not_ready(client: AsyncTogether, exc: Exception) -> bool:
    """Whether a failed poll describes the API rather than the operation."""
    return (isinstance(exc, APIStatusError) and client._should_retry(exc.response)) or isinstance(exc, APIConnectionError)


async def async_wait_for_operation(
    client: AsyncTogether,
    *,
    session_id: str,
    operation: OperationResponse,
    timeout: float | None,
    interval: float,
) -> OperationResponse:
    """Poll until the operation completes, fails, or `timeout` elapses."""
    deadline = None if timeout is None else time.monotonic() + timeout
    delays = _poll_delays(interval)
    current = operation
    last_poll_failure: Exception | None = None

    while True:
        if current.status == _FAILED:
            raise RuntimeError(f"Operation ({current.id}) failed: {current.error}")
        if current.status == _COMPLETED:
            return current

        delay = next(delays)
        if deadline is not None:
            delay = min(delay, deadline - time.monotonic())
            if delay <= 0:
                raise TimeoutError(f"Timed out waiting for operation ({current.id}) to complete") from last_poll_failure
        await asyncio.sleep(delay)

        try:
            current = await async_retrieve_operation(
                client,
                session_id=session_id,
                operation=current,
            )
        except Exception as exc:
            if not _means_not_ready(client, exc):
                raise
            last_poll_failure = exc
            logger.debug("Poll for operation (%s) failed, still waiting: %s", current.id, exc)
