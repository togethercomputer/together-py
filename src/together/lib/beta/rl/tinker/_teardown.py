"""Lifecycle ownership for Together-backed Tinker training clients."""

from __future__ import annotations

import sys
import signal
import logging
import warnings
import threading
from typing import Any

from .. import ModelResourcesClient
from ..clients.session import SessionClient

logger = logging.getLogger("together")

_sigterm_translated = False


class _Lifecycle:
    def __init__(
        self,
        session: SessionClient,
        model_resources: ModelResourcesClient | None = None,
        *,
        owns_model_resources: bool = False,
    ) -> None:
        self.session: SessionClient | None = session
        self.model_resources = model_resources
        self.owns_model_resources = owns_model_resources
        self.closed = False

    def close(self, *, automatic: bool = False) -> None:
        if self.closed:
            return
        failures: list[BaseException] = []
        # Only clear a handle after its stop/detach succeeds, and only mark closed once
        # everything is gone — otherwise a failed explicit close() would no-op retries
        # and disable the atexit fallback while GPUs are still allocated.
        if self.session is not None:
            try:
                self.session.stop()
            except BaseException as exc:
                failures.append(exc)
                logger.error(
                    "[session:%s] %s stop failed: %r",
                    self.session.session_id,
                    "automatic" if automatic else "explicit",
                    exc,
                )
            else:
                self.session = None

        if self.model_resources is not None:
            try:
                if self.owns_model_resources:
                    self.model_resources.stop()
                else:
                    self.model_resources.detach()
            except BaseException as exc:
                failures.append(exc)
                if self.owns_model_resources:
                    _log_release_hint(self.model_resources)
                else:
                    logger.error(
                        "[model-resources:%s] failed to detach the local client: %r",
                        self.model_resources.model_resources_id,
                        exc,
                    )
            else:
                self.model_resources = None

        self.closed = self.session is None and self.model_resources is None
        if failures and not automatic:
            raise failures[0]


def _stop_on_exit(lifecycle: _Lifecycle) -> None:
    """Register cleanup before concurrent-futures and logging atexit shutdown."""

    def stop() -> None:
        lifecycle.close(automatic=True)

    # This private hook is necessary because ordinary atexit callbacks run after
    # concurrent.futures has shut down the executor used by the async HTTP client.
    threading._register_atexit(stop)  # type: ignore[attr-defined]


def _log_release_hint(model_resources: ModelResourcesClient) -> None:
    logger.error(
        "[model-resources:%s] teardown failed; the GPUs are still allocated. "
        "Release them with ModelResourcesClient.attach(model_resources_id=%r).stop()",
        model_resources.model_resources_id,
        model_resources.model_resources_id,
    )


def _exit_on_sigterm() -> None:
    """Translate SIGTERM into SystemExit so interpreter cleanup runs."""
    global _sigterm_translated
    if _sigterm_translated:
        return
    if threading.current_thread() is not threading.main_thread():
        warnings.warn("not on the main thread, so SIGTERM will not trigger GPU teardown", stacklevel=3)
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
