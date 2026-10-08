"""Guarded import of the genuine ``tinker`` package.

The wrapper re-exports tinker's own types rather than reimplementing them, so
the package must be present; fail at import time with an actionable message.
"""

from __future__ import annotations

try:
    import tinker
    from tinker import types
except ModuleNotFoundError as exc:  # pragma: no cover - exercised only without tinker installed
    if exc.name != "tinker":
        raise
    raise ModuleNotFoundError(
        "Together's Tinker compatibility layer requires the optional "
        "'tinker' package and Python 3.11 or newer. "
        "Install it with `pip install 'together[tinker]'`."
    ) from exc

__all__ = ["types", "tinker"]
