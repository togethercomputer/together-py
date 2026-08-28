"""Tinker-compatible entry point for RL training.

For the RL training-loop subset described in ``RL_README.md``, a script written
against the ``tinker`` SDK runs on Together by changing only its import line::

    import together.lib.beta.rl.tinker as tinker

Types resolve to the genuine ``tinker.types`` ones (via ``__getattr__``), so
objects built by ``tinker_cookbook`` — renderer prompts, ``Datum``s — pass
through unchanged; only the service client swaps. Unsupported Tinker clients
(``RestClient``, ``resources``, …) are not exposed. ``forward_backward`` returns
a genuine ``ForwardBackwardOutput`` whose ``.metrics`` includes Together's total
loss under ``loss:sum``, but per-datum ``loss_fn_outputs`` are always empty.
"""

from __future__ import annotations

from typing import Any

from ._compat import types as types
from ._service import ServiceClient as ServiceClient
from .._futures import OperationFuture as APIFuture
from ._sampling import SamplingClient as SamplingClient
from ._training import TrainingClient as TrainingClient

__all__ = [
    "APIFuture",
    "SamplingClient",
    "ServiceClient",
    "TrainingClient",
    "types",
]


def __getattr__(name: str) -> Any:
    if hasattr(types, name):
        return getattr(types, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*__all__, *dir(types)})
