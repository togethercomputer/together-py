"""Guarded import of the genuine ``tinker`` package, and the error for tinker methods we leave out.

The wrapper re-exports tinker's own types rather than reimplementing them, so
the package must be present; fail at import time with an actionable message.
"""

from __future__ import annotations

try:
    import tinker
    from tinker import types
    from tinker.types.optimizer import OptimParamsBase
except ModuleNotFoundError as exc:  # pragma: no cover - exercised only without tinker installed
    if exc.name != "tinker":
        raise
    raise ModuleNotFoundError(
        "Together's Tinker compatibility layer requires the optional "
        "'tinker' package and Python 3.11 or newer. "
        "Install it with `pip install 'together[tinker]'`."
    ) from exc

__all__ = ["types", "tinker", "OptimParamsBase"]


def _missing_attribute_error(ours: type, theirs: type, name: str) -> AttributeError:
    """Return the error for an attribute ``ours`` lacks, naming a method of tinker's ``theirs`` as unsupported.

    A script ported from tinker may call a method Together has no equivalent for; a bare
    AttributeError would read as a typo rather than a known gap. It stays an AttributeError
    so that ``hasattr`` and ``getattr`` with a default still report the method as absent.
    """
    if not name.startswith("_") and callable(getattr(theirs, name, None)):
        return AttributeError(f"Together's Tinker-compatible {ours.__name__} does not support {name}()")
    return AttributeError(f"{ours.__name__!r} object has no attribute {name!r}")
