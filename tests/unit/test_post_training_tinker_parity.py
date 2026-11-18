"""The Tinker-compatible clients keep tinker's call signatures.

A script written against the pinned tinker must call our clients exactly as it calls
tinker's. Each method both define must take tinker's parameters in the same order, with the
same kinds and defaults; ours may only add optional ones. The tinker methods we do not
implement are listed, so a tinker upgrade that adds one fails here until someone decides.
The future a plain call returns inside a running event loop is held to tinker's
``APIFuture`` too, since that is what tinker 0.39-style code receives.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest

pytest.importorskip("tinker")

import tinker

from together.post_training import tinker as tinker_compat
from together.post_training.tinker._pending import _PendingOperation

_EMPTY = inspect.Parameter.empty
_POSITIONAL = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
_VARIADIC = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)

# tinker methods the Tinker-compatible clients deliberately leave out, as of tinker 0.39.0.
_NOT_IMPLEMENTED: dict[str, set[str]] = {
    "ServiceClient": {
        "copy_weights",
        "create_sampling_client",
        "create_sampling_client_async",
        "get_console_url",
        "get_server_capabilities",
        "get_server_capabilities_async",
        "get_telemetry",
    },
    "TrainingClient": {
        "create_sampling_client",
        "create_sampling_client_async",
        "get_console_url",
        "get_info",
        "get_info_async",
        "get_telemetry",
        "get_tokenizer",
        "load_state",
        "load_state_async",
        "load_state_with_optimizer",
        "load_state_with_optimizer_async",
        "save_weights_external",
        "save_weights_external_async",
    },
    "SamplingClient": {
        "create",
        "from_sampler_handle",
        "get_base_model",
        "get_base_model_async",
        "get_sampler_handle",
        "get_telemetry",
        "get_tokenizer",
        "on_queue_state_change",
    },
    "APIFuture": set(),
}

# Each tinker class, the class that stands in for it, and the tinker methods it leaves out.
_COUNTERPARTS: list[tuple[str, type, type, set[str]]] = [
    *(
        (name, getattr(tinker, name), getattr(tinker_compat, name), missing)
        for name, missing in _NOT_IMPLEMENTED.items()
    ),
    ("APIFuture (inside a running loop)", tinker.APIFuture, _PendingOperation, set()),
]


def _public_methods(cls: type) -> set[str]:
    return {name for name in dir(cls) if not name.startswith("_") and callable(getattr(cls, name, None))}


def _shared_methods() -> list[Any]:
    return [
        pytest.param(theirs, ours, method, id=f"{label}.{method}")
        for label, theirs, ours, _ in _COUNTERPARTS
        for method in sorted(_public_methods(theirs) & _public_methods(ours))
    ]


@pytest.mark.parametrize("theirs,ours,not_implemented", [pytest.param(*c[1:], id=c[0]) for c in _COUNTERPARTS])
def test_unimplemented_tinker_methods_are_the_known_ones(theirs: type, ours: type, not_implemented: set[str]) -> None:
    assert _public_methods(theirs) - _public_methods(ours) == not_implemented


@pytest.mark.parametrize("theirs,ours,method", _shared_methods())
def test_shared_methods_take_tinker_arguments(theirs: type, ours: type, method: str) -> None:
    their_params = inspect.signature(getattr(theirs, method)).parameters
    our_params = inspect.signature(getattr(ours, method)).parameters

    their_positional = [name for name, param in their_params.items() if param.kind in _POSITIONAL]
    our_positional = [name for name, param in our_params.items() if param.kind in _POSITIONAL]
    assert our_positional[: len(their_positional)] == their_positional

    for name, their_param in their_params.items():
        assert name in our_params, f"{method} lacks tinker's {name!r}"
        our_param = our_params[name]
        assert our_param.kind == their_param.kind, f"{method}({name}) kind"
        assert our_param.default == their_param.default, (
            f"{method}({name}) default: tinker {their_param.default!r}, ours {our_param.default!r}"
        )

    extra_required = [
        name
        for name, param in our_params.items()
        if name not in their_params and param.default is _EMPTY and param.kind not in _VARIADIC
    ]
    assert not extra_required, f"{method} requires {extra_required}, which tinker does not"


@pytest.mark.parametrize("ours,not_implemented", [pytest.param(*c[2:], id=c[0]) for c in _COUNTERPARTS if c[3]])
def test_unsupported_methods_are_named(ours: type, not_implemented: set[str]) -> None:
    """A ported script calling one on a client instance is told it is unsupported, not handed a bare missing attribute."""
    client = object.__new__(ours)  # the error depends on the class alone
    for method in sorted(not_implemented):
        with pytest.raises(AttributeError, match=rf"{ours.__name__} does not support {method}\(\)"):
            getattr(client, method)
        assert not hasattr(client, method)
    with pytest.raises(AttributeError, match="has no attribute 'no_such_method'"):
        _ = client.no_such_method
