"""What tinker-style calls return when they cannot block the caller."""

from __future__ import annotations

import asyncio
from typing import Any, Generic, TypeVar, NoReturn, cast
from collections.abc import Callable, Coroutine, Generator
from concurrent.futures import Future

from .._loop import _consume_exception, blocking_would_stall_caller
from .._futures import OperationFuture
from ..clients.session import SessionClient

_T = TypeVar("_T")


async def _wait_shielded(future: Future[_T]) -> _T:
    """Wait for ``future`` without cancelling it when the waiter is cancelled.

    The request it carries was sent, or queued to be sent in call order, when the call
    returned; a cancelled waiter must not withdraw it from under the requests behind it.
    """
    waiter = asyncio.wrap_future(future)
    waiter.add_done_callback(_consume_exception)  # nobody may be left to see a failure
    return await asyncio.shield(waiter)


def _deliver(session: SessionClient, sent: Future[OperationFuture[_T]]) -> OperationFuture[_T]:
    """Return a sent request's future in the form the calling context can collect.

    Inside a running event loop the call cannot block, so, as in tinker, it returns a
    future to await at once; the request is already on its way. Elsewhere it waits until
    the server has accepted the request. Neither withdraws the request when the caller is
    interrupted.
    """
    if blocking_would_stall_caller():
        # Not an OperationFuture, but it offers the same collection methods as tinker's APIFuture.
        return cast("OperationFuture[_T]", _PendingOperation(session, sent))
    return session.run(_wait_shielded(sent))


class _PendingOperation(Generic[_T]):
    """The future a training or sampling call returns inside a running event loop.

    As in tinker, the call has already sent its request when it returns; awaiting this only
    waits for the result, and cancelling a wait does not withdraw the request. A training
    call's request is queued behind the requests called before it on the same training
    client; a sampling call's request is sent at once.
    """

    def __init__(self, session: SessionClient, sent: Future[OperationFuture[_T]]) -> None:
        self._session = session
        self._sent = sent

    def __await__(self) -> Generator[Any, None, _T]:
        return self._collect().__await__()

    async def result_async(self, timeout: float | None = None) -> _T:
        """Await the result, giving up after ``timeout`` seconds when it is set."""
        if timeout is None:
            return await self._collect()
        try:
            return await asyncio.wait_for(self._collect(), timeout)
        except asyncio.TimeoutError as exc:
            # Same error and message as OperationFuture's timeout.
            raise TimeoutError(str(exc) or "Timed out waiting for operation to complete") from exc

    def result(self, timeout: float | None = None) -> _T:
        """Block until the result is ready; inside a running event loop, await it instead."""
        if blocking_would_stall_caller():
            raise RuntimeError(
                "blocking calls cannot be used from a running event loop; await this future instead "
                "(its request is already sent, so do not call the method again)"
            )
        return self._session.run(self.result_async(timeout))

    async def coroutine(self) -> _T:
        """This future as a coroutine, for APIs that take one rather than an awaitable (``asyncio.create_task``)."""
        return await self

    def future(self) -> Future[_T]:
        """This result as a ``concurrent.futures.Future``, for blocking or threaded code.

        Cancelling it stops waiting for the result; the request itself keeps running.
        """
        return self._session._loop.submit(self._collect())

    async def _collect(self) -> _T:
        operation = await _wait_shielded(self._sent)
        return await operation

    def __repr__(self) -> str:
        state = "sent" if self._sent.done() else "sending"
        return f"<pending tinker future ({state}); await it for the result>"


class _PendingClient(Generic[_T]):
    """A client that a synchronous create or publish call produces once awaited.

    Inside a running event loop those calls cannot block, so, as in tinker, they return
    this and the caller awaits it for the client. Every await shares one task.

    A publish has already requested its weights sync when the call returns; awaiting only
    waits for it, so a wait that times out or is cancelled stops only that wait, and a later
    await still collects the client. A create starts on the first await, so one that is
    never awaited provisions nothing; as in tinker and the other create paths, a wait that
    times out or is cancelled cancels the create too, releasing what it provisioned, and
    every other await of it then raises ``CancelledError``.
    """

    def __init__(self, start: Callable[[], Coroutine[Any, Any, _T]], *, already_sent: bool) -> None:
        self._start = start
        self._already_sent = already_sent
        self._task: asyncio.Future[_T] | None = None

    def __await__(self) -> Generator[Any, None, _T]:
        return self._waitable().__await__()

    async def result_async(self, timeout: float | None = None) -> _T:
        """Await the client, giving up after ``timeout`` seconds when it is set."""
        if timeout is None:
            return await self
        return await asyncio.wait_for(self._waitable(), timeout)

    def _waitable(self) -> asyncio.Future[_T]:
        task = self._ensure_started()
        # Every await shares this task. A sent publish cannot be withdrawn, so a waiter giving
        # up must not cancel it for the others; a create is cancelled with it, freeing its GPUs.
        return asyncio.shield(task) if self._already_sent else task

    def result(self, timeout: float | None = None) -> NoReturn:
        """Refuse: this handle only exists because the call was made in a running event loop.

        Await it instead. Unlike tinker, it does not block from another thread either.
        """
        del timeout
        raise RuntimeError(
            "this call was made inside a running event loop, so its client cannot be collected by "
            "blocking; await the client instead (if this was a publish, it is already requested, "
            "so do not call it again)"
        )

    def _ensure_started(self) -> asyncio.Future[_T]:
        if self._task is None:
            self._task = asyncio.ensure_future(self._start())
        return self._task

    def __repr__(self) -> str:
        state = "pending" if self._task is None or not self._task.done() else "done"
        return f"<pending tinker client ({state}); await it for the client>"

    def __getattr__(self, name: str) -> NoReturn:
        raise AttributeError(
            f"{name!r} is not available yet: inside a running event loop this call returns an awaitable; "
            "await it for the client (if this was a publish, it is already requested, so do not call it again)"
        )


class _Closing:
    """The in-flight close a ``ServiceClient.close`` call starts, awaitable or blocking like tinker's."""

    def __init__(self, future: Future[None]) -> None:
        self._future = future

    def __await__(self) -> Generator[Any, None, None]:
        return self._shielded().__await__()

    async def result_async(self, timeout: float | None = None) -> None:
        """Wait for the close, giving up after ``timeout`` seconds when it is set."""
        await asyncio.wait_for(self._shielded(), timeout)

    def _shielded(self) -> asyncio.Future[None]:
        # Shielded: a cancelled waiter must not abort the release of GPUs. The failure is
        # still retrieved, so a close nobody waits for anymore is not logged as never retrieved.
        waiter = asyncio.wrap_future(self._future)
        waiter.add_done_callback(_consume_exception)
        return asyncio.shield(waiter)

    async def coroutine(self) -> None:
        """This close as a coroutine, for APIs that take one rather than an awaitable."""
        await self

    def future(self) -> Future[None]:
        """This close as a ``concurrent.futures.Future``, as in tinker.

        Unlike awaiting the close, cancelling this future cancels the close itself, which can
        leave GPUs allocated; to stop waiting without that, use ``result(timeout)`` or await
        the close with a timeout.
        """
        return self._future

    def __repr__(self) -> str:
        state = "done" if self._future.done() else "closing"
        return f"<tinker service client close ({state}); await it or call result()>"

    def result(self, timeout: float | None = None) -> None:
        """Block until the close finishes; inside a running event loop, await it instead."""
        if blocking_would_stall_caller():
            raise RuntimeError("blocking calls cannot be used from a running event loop; await the close instead")
        self._future.result(timeout)
