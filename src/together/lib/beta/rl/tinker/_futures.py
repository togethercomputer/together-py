from __future__ import annotations

from typing import Any, Generic, TypeVar, Callable, Coroutine
from dataclasses import dataclass

from ..clients.session import SessionClient

T = TypeVar("T")


@dataclass(frozen=True)
class _Pending(Generic[T]):
    """An operation already submitted to the service; ``result()`` polls it to completion.

    Together's Tinker layer is synchronous: unlike genuine ``tinker.APIFuture``, this
    compatibility future deliberately does not expose ``result_async`` or ``__await__``.
    """

    _session: SessionClient
    _operation: Any
    _resolve: Callable[[SessionClient, Any, float | None], Coroutine[Any, Any, T]]

    def result(self, timeout: float | None = None) -> T:
        return self._session.run(self._resolve(self._session, self._operation, timeout))
