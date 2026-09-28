from __future__ import annotations

import time
import asyncio
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast
from collections.abc import Callable, Awaitable, Generator

from . import _operations

if TYPE_CHECKING:
    from .clients.session import SessionClient

T = TypeVar("T")


class OperationFuture(Generic[T]):
    """Lazy handle for a submitted RL operation.

    Polling starts only when the caller collects via ``result()``,
    ``result_async()``, or ``await``. ``resolve`` receives the completed operation and
    returns the value callers see; it gets the whole operation, not just ``output``, so
    that a resolver rejecting an empty output can name the operation that produced it.
    A resolved value is cached, as is a failed operation status; transport and resolver
    errors are not, so the caller may collect again. Collection waits indefinitely
    unless the caller passes ``timeout``.
    """

    def __init__(
        self,
        session: SessionClient,
        operation: _operations.OperationResponse,
        resolve: Callable[[_operations.OperationResponse], Awaitable[T]],
    ) -> None:
        self._session = session
        self._operation = operation
        self._resolve = resolve
        self._value: T | None = None
        self._error: _operations.OperationFailedError | None = None
        self._resolved = False
        self._lock = asyncio.Lock()

    @property
    def id(self) -> str:
        return self._operation.id

    def result(self, timeout: float | None = None) -> T:
        """Block until the operation finishes.

        Whether this handle may block at all is the session's call: it refuses from the
        process loop, where blocking deadlocks, and from a foreign loop it would stall — a
        notebook cell, being logically sync, excepted.
        """
        return self._session.run(self._collect(timeout=timeout))

    async def result_async(self, timeout: float | None = None) -> T:
        """Await the result from inside a running event loop."""
        return await self._session.run_async(self._collect(timeout=timeout))

    async def _collect(self, timeout: float | None = None) -> T:
        if timeout is None:
            return await self._collect_result(deadline=None)
        try:
            return await asyncio.wait_for(self._collect_result(deadline=time.monotonic() + timeout), timeout=timeout)
        except asyncio.TimeoutError as exc:
            # asyncio.TimeoutError is distinct from TimeoutError on Python 3.10.
            raise TimeoutError(str(exc) or "Timed out waiting for operation to complete") from exc

    async def _collect_result(self, *, deadline: float | None) -> T:
        async with self._lock:
            if self._resolved:
                if self._error is not None:
                    raise self._error
                return cast(T, self._value)

            # Cancel/timeout/transport errors say nothing about the operation itself, so
            # they stay uncached. Only a failed status is terminal.
            try:
                completed = await _operations.async_wait_for_operation(
                    client=self._session._client,
                    session_id=self._session._session_id,
                    operation=self._operation,
                    timeout=None if deadline is None else max(0.0, deadline - time.monotonic()),
                    interval=_operations.DEFAULT_OPERATION_INTERVAL,
                )
            except _operations.OperationFailedError as exc:
                self._error = exc
                self._resolved = True
                raise

            # Resolver bugs are local and may be transient; do not make them sticky.
            value = await self._resolve(completed)
            self._value = value
            self._resolved = True
            return value

    def __await__(self) -> Generator[Any, None, T]:
        return self.result_async().__await__()
