from __future__ import annotations

from typing import Any, Optional

from ..._exceptions import TogetherError

__all__ = [
    "RealtimeError",
    "RealtimeConnectionError",
    "RealtimeSessionError",
    "RealtimeIdleTimeoutError",
    "RealtimeBufferOverflowError",
    "RealtimeInvalidStateError",
]


class RealtimeError(TogetherError):
    """Base class for all realtime transcription errors."""


class RealtimeConnectionError(RealtimeError):
    """Raised when an endpoint could not be established or kept usable — reconnect
    exhausted, handshake rejected, or the server reported it cannot serve. Either
    way the endpoint is unusable; a failover loop should rotate to another one.

    `code` carries the server-reported reason when present, e.g.
    "no_healthy_workers" — the endpoint cannot currently serve, so it is raised
    immediately without exhausting same-endpoint reconnects. Also carries the
    attempts made, the last underlying cause, and the raw server event when
    available.
    """

    def __init__(
        self,
        message: str,
        *,
        attempts: int = 0,
        cause: Optional[BaseException] = None,
        code: Optional[str] = None,
        raw: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.__cause__ = cause
        self.code = code
        self.raw = raw


class RealtimeSessionError(RealtimeError):
    """A fatal, non-retryable error reported by the server.

    Examples: invalid model, unsupported audio format, revoked access.
    """

    def __init__(
        self,
        message: str,
        *,
        error_type: Optional[str] = None,
        code: Optional[str] = None,
        raw: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.code = code
        self.raw = raw


class RealtimeIdleTimeoutError(RealtimeError):
    """The server closed the session because no audio was appended for its idle window.

    The server is healthy; the client simply went silent. Not retried by default —
    reconnect only happens automatically when un-replayed audio is pending.
    """


class RealtimeBufferOverflowError(RealtimeError):
    """The SDK-side recovery buffer exceeded its limit with overflow policy "error"."""

    def __init__(self, message: str, *, dropped_seconds: float = 0.0) -> None:
        super().__init__(message)
        self.dropped_seconds = dropped_seconds


class RealtimeInvalidStateError(RealtimeError):
    """An operation was attempted in an invalid state (e.g. append after close)."""
