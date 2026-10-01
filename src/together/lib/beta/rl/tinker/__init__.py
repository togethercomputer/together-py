"""Tinker-compatible entry point for RL training.

For the supported RL training-loop subset, a script written against the
``tinker`` SDK runs on Together by changing only its import line::

    import together.lib.beta.rl.tinker as tinker

Types resolve to the genuine ``tinker.types`` ones (via ``__getattr__``), so
objects built by ``tinker_cookbook`` — renderer prompts, ``Datum``s — pass
through unchanged; only the service client swaps. Unsupported Tinker clients
(``RestClient``, ``resources``, …) are not exposed; ``ServiceClient.create_rest_client``
raises ``tinker.TinkerError``. ``save_state`` returns a bare checkpoint UUID; resume
describes that id and starts a new session. ``save_weights_for_sampler`` creates an
inference checkpoint and returns the registered ``model_name`` (Tinker ``name`` /
TTL are ignored). ``forward`` fills per-datum ``loss_fn_outputs`` with real logprobs,
and ``forward_backward`` does too when asked via ``return_loss_fn_outputs`` — an
argument Tinker itself has no equivalent for, since on Together the two operations
are one. Both publish the total loss under ``metrics["loss:sum"]``.
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
