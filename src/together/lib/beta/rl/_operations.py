from __future__ import annotations

import time
import asyncio
from typing import Union
from typing_extensions import TypeAlias

from ...._client import AsyncTogether
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

_COMPLETED = "TRAINING_OPERATION_STATUS_COMPLETED"
_FAILED = "TRAINING_OPERATION_STATUS_FAILED"


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


async def async_wait_for_operation(
    client: AsyncTogether,
    *,
    session_id: str,
    operation: OperationResponse,
    timeout: float | None,
    interval: float,
) -> OperationResponse:
    deadline = None if timeout is None else time.monotonic() + timeout
    current = operation

    while True:
        if current.status == _FAILED:
            raise RuntimeError(f"Operation ({current.id}) failed: {current.error}")
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
        await asyncio.sleep(interval)
