"""Event-loop ownership for the RL clients.

:class:`_ProcessLoop` owns the one daemon loop (``together-rl``) that drives every handle's
work, whether the handle was built synchronously or awaited. It starts the loop on first use
and keeps the loop object to itself — callers hand it coroutines and get futures back, so
nobody can hold a loop that a fork or a failed start has since invalidated.

:class:`LoopGate` is one handle's door onto that loop. It tracks the futures that handle
submitted so teardown can cancel exactly those and leave the loop up for its peers.
:func:`run_untracked` is the door for callers that hold no handle yet — constructors — whose
work no teardown can cancel. Both the loop and every gate are rebuilt in a ``fork`` child,
which inherits these objects but none of the threads that use them.
"""

from __future__ import annotations

import os
import sys
import asyncio
import logging
import weakref
import functools
import threading
from typing import Any, TypeVar, Protocol
from collections.abc import Callable, Coroutine
from typing_extensions import ParamSpec, Concatenate
from concurrent.futures import Future, ThreadPoolExecutor

logger = logging.getLogger("together")

_T = TypeVar("_T")
_P = ParamSpec("_P")

# Rollout env steps reach this loop via asyncio.to_thread → default executor.
_THREAD_POOL_SIZE_ENV = "TOGETHER_RL_THREAD_POOL_SIZE"

# Jupyter / lab / qtconsole / Colab. TerminalInteractiveShell drives no loop — excluded.
_NOTEBOOK_SHELLS = frozenset({"ZMQInteractiveShell", "Shell"})

_ALREADY_STOPPED = "this handle is stopped or stopping; create or attach a new one"


def _in_notebook() -> bool:
    # Never import IPython — if it is not already loaded, nothing interactive is running.
    ipython = sys.modules.get("IPython")
    if ipython is None:
        return False
    shell = ipython.get_ipython()
    return shell is not None and type(shell).__name__ in _NOTEBOOK_SHELLS


def blocking_would_stall_caller() -> bool:
    """True when a sync block would freeze the caller's own loop (notebooks are exempt)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return not _in_notebook()


def _pool_size() -> int | None:
    """Rollout thread-pool width from the environment, None when unset."""
    value = os.environ.get(_THREAD_POOL_SIZE_ENV)
    if not value:
        return None
    # A typo here would otherwise surface as a bare int() ValueError out of create().
    invalid = ValueError(f"{_THREAD_POOL_SIZE_ENV}={value!r} is not a positive integer")
    try:
        size = int(value)
    except ValueError:
        raise invalid from None
    if size < 1:
        raise invalid
    return size


def _blocking_result(fut: Future[_T]) -> _T:
    """Wait for fut; on interrupt, cancel it so the daemon loop does not keep running the work."""
    try:
        return fut.result()
    except BaseException:
        fut.cancel()
        try:
            # Reaped so the cancellation is not logged later as a never-retrieved exception;
            # whatever it raises is dropped in favour of the interrupt on its way out.
            fut.result()
        except BaseException:
            pass
        raise


def _consume_exception(future: asyncio.Future[Any]) -> None:
    """Retrieve a shielded wait's exception even if its caller was cancelled."""
    if not future.cancelled():
        future.exception()


class _ProcessLoop:
    """The one daemon loop, and the only way onto it.

    Started lazily, never closed during normal use. Submission methods keep the loop
    private; everything else names work instead, by handing over a coroutine. The two
    predicates are part of that interface — a caller deciding whether it may block, or whether
    it is already on this loop, must ask rather than compare loops itself.
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._lock = threading.Lock()

    def submit(self, coro: Coroutine[Any, Any, _T]) -> Future[_T]:
        """Schedule coro on the process loop, closing it if the loop fails to start."""
        try:
            loop = self._start()
        except BaseException:
            coro.close()
            raise
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def submit_teardown(
        self,
        coro: Coroutine[Any, Any, Any],
        on_done: Callable[[asyncio.Task[Any]], None],
    ) -> Callable[[], None]:
        """Start teardown and return a cancellation request, independent of completion.

        Register the completion callback before the task can start, so cancellation
        before its first step still settles the gate. Only this callback releases the
        claim; cancelling a caller's wait cannot stand in for task completion.
        """
        try:
            loop = self._start()
        except BaseException:
            coro.close()
            raise
        started: Future[asyncio.Task[Any]] = Future()

        def start() -> None:
            task = loop.create_task(coro)
            task.add_done_callback(on_done)
            started.set_result(task)

        def cancel_task(future: Future[asyncio.Task[Any]]) -> None:
            loop.call_soon_threadsafe(future.result().cancel)

        def cancel() -> None:
            started.add_done_callback(cancel_task)

        loop.call_soon_threadsafe(start)
        return cancel

    def owns_running_loop(self) -> bool:
        """True when the calling thread is running on the process loop itself.

        Read without the lock, which is safe in the only direction that matters: a loop that
        has not been published yet cannot be the one running this thread.
        """
        try:
            return asyncio.get_running_loop() is self._loop
        except RuntimeError:
            return False

    def refuse_nested_blocking(self, coro: Coroutine[Any, Any, Any]) -> None:
        """Refuse to block the calling thread wherever blocking would deadlock or stall it.

        Closes coro before raising, as every refusal path here does, so a refused call never
        leaves an un-awaited coroutine behind.

        Blocking while running *on* the process loop always deadlocks: the thread that would
        have to complete the work is the one being blocked. Blocking a foreign loop stalls the
        caller's own loop instead — refused too, except in a notebook, where the cell is
        logically sync and the kernel loop is not ours to restructure.
        """
        try:
            running = asyncio.get_running_loop()
        except RuntimeError:
            return
        if running is not self._loop and _in_notebook():
            return
        coro.close()
        raise RuntimeError("blocking calls cannot be used from a running event loop; use the *_async variant instead")

    def _start(self) -> asyncio.AbstractEventLoop:
        with self._lock:
            if self._loop is None:
                # Parse first, publish last: a malformed pool size must raise without leaving a
                # loop nothing drives behind, which every later submit would block on forever.
                workers = _pool_size()
                loop = asyncio.new_event_loop()
                if workers is not None:
                    loop.set_default_executor(
                        ThreadPoolExecutor(max_workers=workers, thread_name_prefix="together-rl-env")
                    )
                    logger.info("RL rollout thread pool widened to %s workers", workers)
                threading.Thread(target=loop.run_forever, name="together-rl", daemon=True).start()
                self._loop = loop
            return self._loop


_process_loop = _ProcessLoop()
_live_gates: weakref.WeakSet[LoopGate] = weakref.WeakSet()


def run_untracked(coro: Coroutine[Any, Any, _T]) -> _T:
    """Drive coro to completion on the process loop, blocking the calling thread.

    Untracked: no handle owns this work, so no teardown cancels it and an interrupt is the only
    cancellation there is. For callers that hold no gate yet — the constructors.
    """
    _process_loop.refuse_nested_blocking(coro)
    return _blocking_result(_process_loop.submit(coro))


async def run_untracked_async(coro: Coroutine[Any, Any, _T]) -> _T:
    """Await coro on the process loop, hopping from a foreign loop when needed. Untracked."""
    if _process_loop.owns_running_loop():
        return await coro
    return await asyncio.wrap_future(_process_loop.submit(coro))


class LoopGate:
    """Per-handle gate onto the process-wide background loop.

    Every handle — sync- or async-created — submits work to the same ``together-rl``
    thread. The gate is what makes teardown handle-scoped: it tracks this handle's
    in-flight futures so ``_close()`` can cancel exactly those, refuses new work once
    teardown has begun, and makes teardown itself run at most once. The process loop
    stays up for other handles.
    """

    def __init__(self) -> None:
        self._closed = False
        self._tearing_down = False
        self._teardown_stops_remote = False
        self._teardown_done: Future[Any] | None = None
        self._futures: set[Future[Any]] = set()
        self._state_lock = threading.Lock()
        _live_gates.add(self)

    @property
    def closed(self) -> bool:
        """True once a teardown has completed. A failed one leaves this False, so it can retry."""
        with self._state_lock:
            return self._closed

    def run(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Drive coro to completion on the process loop, blocking the calling thread.

        Tracked, so this handle's teardown cancels it — and refused from the moment that
        teardown begins. Ordinary work can never ask for teardown's exemption from that.
        """
        return self._drive(coro)

    async def run_async(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Await coro on the process loop, hopping from a foreign loop when needed. Tracked."""
        return await self._drive_async(coro)

    def run_teardown(self, coro: Coroutine[Any, Any, _T], *, stops_remote: bool = True) -> _T | None:
        """Run coro then close. Runs at most once; on failure leaves the gate retryable.

        Callers that race lose the claim and wait for the winner, seeing the same result or
        the same exception. None means teardown had already finished before this call.

        ``stops_remote`` is False for a teardown that releases the handle but leaves the
        remote resource running, so a later teardown can report what it can no longer do.
        """
        _process_loop.refuse_nested_blocking(coro)
        in_flight, cancel = self._start_teardown(coro, stops_remote)
        try:
            return None if in_flight is None else in_flight.result()
        except BaseException:
            if cancel is not None:
                cancel()
            raise

    async def run_teardown_async(self, coro: Coroutine[Any, Any, _T], *, stops_remote: bool = True) -> _T | None:
        """Async twin of :meth:`run_teardown`."""
        in_flight, cancel = self._start_teardown(coro, stops_remote)
        if in_flight is None:
            return None
        waiter = asyncio.wrap_future(in_flight)
        waiter.add_done_callback(_consume_exception)
        try:
            # A cancelled caller may request task cancellation, but the shared outcome
            # remains pending until the actual task completes its cleanup.
            return await asyncio.shield(waiter)
        except BaseException:
            if cancel is not None:
                cancel()
            raise

    def _start_teardown(
        self, coro: Coroutine[Any, Any, _T], stops_remote: bool
    ) -> tuple[Future[Any] | None, Callable[[], None] | None]:
        claimed, in_flight = self._claim_teardown(stops_remote)
        if not claimed:
            coro.close()
            return in_flight, None
        try:
            cancel = _process_loop.submit_teardown(coro, self._finish_teardown)
        except BaseException as exc:
            self._abort_teardown(exc)
            raise
        return in_flight, cancel

    def _finish_teardown(self, task: asyncio.Task[Any]) -> None:
        try:
            output = task.result()
        except BaseException as exc:
            self._abort_teardown(exc)
        else:
            self._close(output)

    def _drive(self, coro: Coroutine[Any, Any, _T]) -> _T:
        _process_loop.refuse_nested_blocking(coro)
        return _blocking_result(self._submit_and_track(coro))

    async def _drive_async(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Await coro on the process loop, hopping from a foreign loop when needed.

        A caller already on the process loop awaits coro in place, which leaves that work
        untracked — it is the caller's own coroutine, cancelled with the caller. It is still
        gated, so teardown refuses it like any other.
        """
        if _process_loop.owns_running_loop():
            self._refuse_if_stopped(coro)
            return await coro
        return await asyncio.wrap_future(self._submit_and_track(coro))

    def _refusing(self) -> bool:
        """True when ordinary work must be refused.

        The one copy of the rule. Callers hold ``_state_lock``, which is not reentrant.
        """
        return self._closed or self._tearing_down

    def _refuse_if_stopped(self, coro: Coroutine[Any, Any, Any]) -> None:
        """Reject ordinary work from the moment teardown begins, not once it finishes."""
        with self._state_lock:
            refused = self._refusing()
        if refused:
            coro.close()
            raise RuntimeError(_ALREADY_STOPPED)

    def _claim_teardown(self, stops_remote: bool) -> tuple[bool, Future[Any] | None]:
        """Claim exclusive teardown, or say what a caller that lost the race should wait for.

        ``(True, future)`` — the caller drives teardown; the gate settles the outcome for
        everyone else. ``(False, future)`` — a teardown is in flight, and that future carries
        its outcome. ``(False, None)`` — teardown already finished, so there is nothing left
        to observe. The in-flight future is captured under the same lock as the claim, so a
        loser never has to re-read state the winner may have changed in between.
        """
        with self._state_lock:
            if not (self._closed or self._tearing_down):
                self._tearing_down = True
                self._teardown_stops_remote = stops_remote
                self._teardown_done = Future()
                return True, self._teardown_done
            # Cleared by both endings, so this is set only while a teardown is in flight.
            joinable = self._teardown_done
            stranded = stops_remote and not self._teardown_stops_remote
        if stranded:
            logger.warning("this handle was detached, so it can no longer stop the remote resource; it keeps running")
        return False, joinable

    def _abort_teardown(self, failure: BaseException) -> None:
        """Fail the waiters and release the claim, so a retry can call _claim_teardown again.

        Both under one lock: releasing the claim drops the gate's only reference to that
        future, so a waiter must never be woken by a retry it cannot see the outcome of.
        """
        with self._state_lock:
            done, self._teardown_done = self._teardown_done, None
            self._tearing_down = False
            if done is not None:
                done.set_exception(failure)

    def _close(self, output: Any) -> None:
        """Hand the teardown's outcome to its waiters, refuse further work, cancel futures.

        Only futures this handle submitted from another thread are cancelled: work awaited in
        place by :meth:`_drive_async` — the caller was already on the process loop — is the
        caller's own coroutine and is not tracked here.
        """
        with self._state_lock:
            self._closed = True
            done, self._teardown_done = self._teardown_done, None
            pending = list(self._futures)
            self._futures.clear()
            if done is not None:
                done.set_result(output)
        for fut in pending:
            fut.cancel()

    def _submit_and_track(self, coro: Coroutine[Any, Any, _T]) -> Future[_T]:
        self._refuse_if_stopped(coro)
        fut = _process_loop.submit(coro)
        with self._state_lock:
            # Load-bearing: _close() may have drained _futures since the check above, and a
            # future added after that drain would never be cancelled.
            self._futures.add(fut)
            refused = self._refusing()
        fut.add_done_callback(self._forget)
        if refused:
            # Work already reached the loop: cancel it and let the waiter see that,
            # rather than RuntimeError as if the call had never started.
            fut.cancel()
        return fut

    def _forget(self, fut: Future[Any]) -> None:
        with self._state_lock:
            self._futures.discard(fut)


def _reset_after_fork() -> None:
    # A child inherits these objects but none of the threads that use them: the loop has
    # nothing driving it, and a lock inherited while held is held by a thread that does not
    # exist here. Either one deadlocks silently on first use. Every field that needs resetting
    # is listed here, adjacently, so a forgotten one is visible.
    _process_loop._loop = None
    _process_loop._lock = threading.Lock()
    for gate in _live_gates:
        gate._state_lock = threading.Lock()
        gate._futures.clear()  # they belong to the parent's loop, which nothing here drives
        # Nothing here can settle a teardown the parent was driving, so a waiter would wait
        # forever. The gate stays tearing-down and therefore refusing, which is the right end
        # state for an inherited handle: its socket did not survive the fork either.
        gate._teardown_done = None


if hasattr(os, "register_at_fork"):  # Unix only; the SDK also imports on Windows.
    os.register_at_fork(after_in_child=_reset_after_fork)


class _LoopBound(Protocol):
    @property
    def _loop(self) -> LoopGate: ...


_ClientT = TypeVar("_ClientT", bound=_LoopBound)


def on_client_loop(
    method: Callable[Concatenate[_ClientT, _P], Coroutine[Any, Any, _T]],
) -> Callable[Concatenate[_ClientT, _P], Coroutine[Any, Any, _T]]:
    """Await a public *_async method on the process loop, whichever loop the caller is on.

    The hop is a no-op when the caller is already on that loop, so sync methods may call
    their *_async twin without a double bounce.
    """

    @functools.wraps(method)
    async def hopped(self: _ClientT, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        return await self._loop.run_async(method(self, *args, **kwargs))

    # Marked rather than detected via __wrapped__, which any functools.wraps decorator sets.
    hopped.on_client_loop = True  # type: ignore[attr-defined]
    return hopped
