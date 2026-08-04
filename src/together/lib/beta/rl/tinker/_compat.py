"""Guarded import of the genuine ``tinker`` package.

The wrapper re-exports tinker's own types rather than reimplementing them, so
the package must be present; fail at import time with an actionable message.
"""

from __future__ import annotations

try:
    import tinker
    from tinker import types
except ImportError as exc:  # pragma: no cover - exercised only without tinker installed
    msg = (
        "together.lib.beta.rl.tinker re-exports tinker's types; install the 'tinker' package (requires Python >= 3.11)"
    )
    raise ImportError(msg) from exc

__all__ = ["types", "tinker"]
