"""Tinker-compatible entry point for RL training.

A training script written against the ``tinker`` SDK runs on Together by changing
only its import line::

    import together.lib.beta.rl.tinker as tinker

Types are the genuine ``tinker`` ones (re-exported below), so objects built by
``tinker_cookbook`` — renderer prompts, ``Datum``s — pass through unchanged; only
the service client swaps. One exception: ``forward_backward`` resolves to
Together's result model — its ``.metrics`` mapping is what tinker scripts read,
but tinker's per-datum ``loss_fn_outputs`` are not available.
"""

from __future__ import annotations

from typing import Any

from ._compat import types as types, tinker as _tinker
from ._clients import ServiceClient as ServiceClient, SamplingClient as SamplingClient, TrainingClient as TrainingClient

__all__ = ["SamplingClient", "ServiceClient", "TrainingClient", "types"]


def __getattr__(name: str) -> Any:
    """Delegate anything we don't define (``Datum``, ``ModelInput``, ...) to genuine tinker."""
    return getattr(_tinker, name)
