"""Lifecycle ownership for Together-backed Tinker training clients."""

from __future__ import annotations

import sys
import signal
import logging
import warnings
import threading
from typing import Any
from functools import partial
from dataclasses import dataclass
from collections.abc import Callable, Awaitable

from .. import ModelResourcesClient
from .._loop import blocking_would_stall_caller
from ..clients.session import SessionClient

logger = logging.getLogger("together")

_sigterm_translated = False


@dataclass(frozen=True)
class _Handle:
    """One remote resource, with the two ways to give it back and how to report a refusal."""

    stop: Callable[[], Any]
    stop_async: Callable[[], Awaitable[Any]]
    report: Callable[[BaseException], None]


def _build_session_handle(session: SessionClient) -> _Handle:
    def report(exc: BaseException) -> None:
        logger.error("[session:%s] stop failed: %r", session.session_id, exc)

    return _Handle(session.stop, session.stop_async, report)


def _build_model_resources_handle(model_resources: ModelResourcesClient, *, owned: bool) -> _Handle:
    """Build the handle for model resources.

    Borrowed resources are only detached: the tenant that lent them keeps their GPUs.
    """

    def report(exc: BaseException) -> None:
        if owned:
            logger.error(
                "[model-resources:%s] teardown failed (%r); the GPUs are still allocated. "
                "Release them with ModelResourcesClient.attach(model_resources_id=%r).stop()",
                model_resources.model_resources_id,
                exc,
                model_resources.model_resources_id,
            )
        else:
            logger.error(
                "[model-resources:%s] failed to detach the local client: %r",
                model_resources.model_resources_id,
                exc,
            )

    if owned:
        return _Handle(model_resources.stop, model_resources.stop_async, report)
    return _Handle(model_resources.detach, model_resources.detach_async, report)


class _Lifecycle:
    """Owns releasing the remote resources behind a training client.

    Handles are released in order and dropped as each one's teardown succeeds, so a
    partial failure leaves exactly the resources still allocated. Nothing counts as
    closed until every handle is gone — otherwise a failed explicit ``close()`` would
    no-op retries and disable the interpreter-exit fallback while GPUs run on.
    """

    def __init__(
        self,
        session: SessionClient | None,
        model_resources: ModelResourcesClient | None = None,
        *,
        owns_model_resources: bool = False,
    ) -> None:
        self._pending: list[_Handle] = []
        if session is not None:
            self._pending.append(_build_session_handle(session))
        if model_resources is not None:
            self._pending.append(_build_model_resources_handle(model_resources, owned=owns_model_resources))

    @property
    def closed(self) -> bool:
        return not self._pending

    def close(self, *, automatic: bool = False) -> None:
        """Release every handle, blocking; inside a running loop use :meth:`aclose`.

        A notebook cell is logically synchronous, so it may block here exactly as it may
        block on the session's own methods. ``automatic`` makes the release best-effort —
        never refused for a running loop, and failures logged rather than raised — which is
        what both the interpreter-exit fallback and a failed provisioning rollback need.
        """
        if not automatic and blocking_would_stall_caller():
            raise RuntimeError(
                "close() cannot block inside a running event loop; use "
                "`async with training_client` or `await training_client.close_async()`"
            )
        failures: list[BaseException] = []
        survivors: list[_Handle] = []
        for handle in self._pending:
            # BaseException: a Ctrl-C during a hung stop() must not skip the GPUs behind it.
            try:
                handle.stop()
            except BaseException as exc:
                handle.report(exc)
                failures.append(exc)
                survivors.append(handle)
        self._pending = survivors
        if failures and not automatic:
            raise failures[0]

    async def aclose(self, *, automatic: bool = False) -> None:
        """Release every handle asynchronously through the shared process loop."""
        failures: list[BaseException] = []
        survivors: list[_Handle] = []
        for handle in self._pending:
            try:
                await handle.stop_async()
            except BaseException as exc:
                handle.report(exc)
                failures.append(exc)
                survivors.append(handle)
        self._pending = survivors
        if failures and not automatic:
            raise failures[0]


def _stop_on_exit(lifecycle: _Lifecycle) -> None:
    """Register best-effort cleanup before concurrent-futures and logging shutdown."""

    # This private hook is necessary because ordinary atexit callbacks run after
    # concurrent.futures has shut down the executor used by the async HTTP client.
    threading._register_atexit(partial(lifecycle.close, automatic=True))  # type: ignore[attr-defined]


def _exit_on_sigterm() -> None:
    """Translate SIGTERM into SystemExit so interpreter cleanup runs."""
    global _sigterm_translated
    if _sigterm_translated:
        return
    if threading.current_thread() is not threading.main_thread():
        warnings.warn("not on the main thread, so SIGTERM will not trigger GPU teardown", stacklevel=2)
        return
    previous = signal.getsignal(signal.SIGTERM)
    if previous is signal.SIG_IGN:
        return

    def handler(signum: int, frame: Any) -> None:
        if callable(previous):
            previous(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, handler)
    _sigterm_translated = True
