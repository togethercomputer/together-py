from __future__ import annotations

from typing import Any, Generic, TypeVar, Callable, Coroutine
from dataclasses import dataclass

from ..clients.session import SessionClient

T = TypeVar("T")


@dataclass(frozen=True)
class _Pending(Generic[T]):
    """An operation already submitted to the service; ``result()`` polls it to completion.

    Deliberately minimal — the tinker loop only ever calls ``.result()``. If this needs
    ``__await__``, result caching, or a poll policy, adopt MOSH-3628's ``OperationFuture``
    instead of growing it.
    """

    _session: SessionClient
    _operation: Any
    _resolve: Callable[[SessionClient, Any], Coroutine[Any, Any, T]]

    def result(self) -> T:
        return self._session.run(self._resolve(self._session, self._operation))
