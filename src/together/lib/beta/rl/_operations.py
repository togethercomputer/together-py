from __future__ import annotations

import time
import asyncio
from typing import Union, TypeVar
from collections.abc import Callable, Awaitable
from typing_extensions import TypeAlias

from ...._client import AsyncTogether
from ....types.beta.rl.sample_operation import SampleOperation
from ....types.beta.rl.forward_operation import ForwardOperation
from ....types.beta.rl.optim_step_operation import OptimStepOperation
from ....types.beta.rl.weights_sync_operation import WeightsSyncOperation
from ....types.beta.rl.forward_backward_operation import ForwardBackwardOperation
from ....types.beta.rl.training_checkpoint_operation import TrainingCheckpointOperation
from ....types.beta.rl.inference_checkpoint_operation import InferenceCheckpointOperation
from ....types.beta.rl.custom_forward_backward_operation import CustomForwardBackwardOperation

OperationResponse: TypeAlias = Union[
    ForwardOperation,
    ForwardBackwardOperation,
    CustomForwardBackwardOperation,
    OptimStepOperation,
    WeightsSyncOperation,
    SampleOperation,
    InferenceCheckpointOperation,
    TrainingCheckpointOperation,
]

_COMPLETED = "TRAINING_OPERATION_STATUS_COMPLETED"
_FAILED = "TRAINING_OPERATION_STATUS_FAILED"

DEFAULT_OPERATION_TIMEOUT: float | None = 300.0
DEFAULT_OPERATION_INTERVAL: float = 0.5

_T = TypeVar("_T")


class OperationFailedError(RuntimeError):
    """The server reported the operation as failed — a terminal, non-retryable verdict."""


def require_output(output: _T | None, *, operation: OperationResponse) -> _T:
    """Raise when a completed operation that is expected to carry a payload has empty output.

    Skip for ops whose resolve tolerates a missing payload (optim_step,
    custom_forward_backward).
    """
    if output is None:
        raise RuntimeError(f"Operation completed with empty output: {operation}")
    return output


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
    if isinstance(operation, WeightsSyncOperation):
        return await client.beta.rl.operations.retrieve_weights_sync(
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


async def async_wait_for_operation(
    client: AsyncTogether,
    *,
    session_id: str,
    operation: OperationResponse,
    timeout: float | None,
    interval: float,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> OperationResponse:
    deadline = None if timeout is None else time.monotonic() + timeout
    current = operation

    while True:
        if current.status == _FAILED:
            raise OperationFailedError(f"Operation ({current.id}) failed: {current.error}")
        if current.status == _COMPLETED:
            return current
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("Timed out waiting for operation to complete")

        current = await async_retrieve_operation(
            client,
            session_id=session_id,
            operation=current,
        )
        if current.status in (_COMPLETED, _FAILED):
            continue
        await sleep(interval)
