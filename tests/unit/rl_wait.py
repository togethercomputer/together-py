"""Shared stub for RL operation polling.

Every RL test that drives an operation to completion has to replace
``_operations.async_wait_for_operation``; this keeps the one stub in one place.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from together.lib.beta.rl import _operations as rl_ops


def patch_wait(
    monkeypatch: pytest.MonkeyPatch,
    result: Any = None,
) -> list[float | None]:
    """Complete every polled operation immediately.

    ``result`` is returned as the output of every operation. Returns the list of
    timeouts the stub was called with, so tests can assert on what the caller asked for.
    """
    timeouts: list[float | None] = []

    async def fake(
        *,
        client: Any,  # noqa: ARG001
        session_id: str,  # noqa: ARG001
        operation: Any,
        timeout: float | None,
        interval: float,  # noqa: ARG001
    ) -> Any:
        timeouts.append(timeout)
        return SimpleNamespace(
            id=getattr(operation, "id", "op"),
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output=result,
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake)
    return timeouts
