"""Tinker-compatible entry point for RL training.

For the supported RL training-loop subset, a script written against the
``tinker`` SDK runs on Together by changing only its import line::

    import together.post_training.tinker as tinker

Types resolve to the genuine ``tinker.types`` ones (via ``__getattr__``), so
objects built by ``tinker_cookbook`` — renderer prompts, ``Datum``s — pass
through unchanged; only the service client swaps. Unsupported Tinker clients
(``RestClient``, ``resources``, …) are not exposed; ``ServiceClient.create_rest_client``
and ``ServiceClient.create_custom_loss`` raise ``tinker.TinkerError``; any other tinker
method called on a client instance that leaves it out (``save_weights_external``, …)
raises an ``AttributeError`` that names it as unsupported. ``save_state`` returns a bare
checkpoint UUID; resume describes that id and starts a new session.
``save_weights_for_sampler`` creates an inference checkpoint and returns its UUID
(Tinker ``name`` / TTL are ignored). ``forward`` and ``forward_backward`` fill per-datum
``loss_fn_outputs`` with real logprobs, as tinker's do; a position the loss excludes comes
back masked to zero. ``return_loss_fn_outputs=False`` skips them, an argument Tinker itself
has no equivalent for. Both publish the total loss under ``metrics["loss:sum"]``.

Every call follows tinker 0.39's two call styles. Synchronous code gets the client, or an
``APIFuture`` to call ``.result()`` on. Inside a running event loop the same plain calls do
not block: they return an awaitable at once, so
``await service_client.create_lora_training_client(...)``, ``await sampling_client.sample(...)``
and ``fwd = training_client.forward_backward(...); step = training_client.optim_step(...)``,
then awaiting both, all work. A training or sampling call has already sent or queued its
request when it returns; a create starts when first awaited. In a notebook the calls block,
because the kernel's loop is logically synchronous. A training client's requests reach the
server in the order they were called, whichever style made them; a failed
``forward_backward_custom`` makes the client reject every later training request, as in
tinker, and, stricter than tinker, so does one the server fails. A request is not withdrawn
once the call is made, even if the call or the caller's wait is interrupted; a create,
which is only sent once awaited, is cancelled with an interrupted wait. The deprecated
``*_async`` methods remain. ``APIFuture.future()`` gives a ``concurrent.futures.Future``.
``with ServiceClient(...) as service_client:`` and ``service_client.close(status)`` close
every training client that service client created.
"""

from __future__ import annotations

from typing import Any

from ._compat import types as types
from ._service import ServiceClient as ServiceClient
from .._futures import OperationFuture as APIFuture
from ._sampling import SamplingClient as SamplingClient
from ._training import TrainingClient as TrainingClient
from .._transform_patch import apply as _apply_transform_patch

# Widens the transformer's scalar fast path to cover unions of scalars, which is
# what protobuf int64 arrays (token ids) become. Inert once upstream covers it.
# See _transform_patch for the measurement and why it cannot live in _utils.
_apply_transform_patch()

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
