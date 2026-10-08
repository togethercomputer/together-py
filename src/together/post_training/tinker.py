"""Public Tinker-compatible entry point.

    import together.post_training.tinker as tinker

The implementation lives in ``together.lib.post_training.tinker``.
"""

from __future__ import annotations

from typing import Any

from ..lib.post_training.tinker import (
    APIFuture as APIFuture,
    ServiceClient as ServiceClient,
    SamplingClient as SamplingClient,
    TrainingClient as TrainingClient,
    types as types,
    __all__ as __all__,
)


def __getattr__(name: str) -> Any:
    from ..lib.post_training import tinker as _tinker

    return getattr(_tinker, name)


def __dir__() -> list[str]:
    from ..lib.post_training import tinker as _tinker

    return dir(_tinker)
