"""Widen the transformer's scalar fast path to cover unions of scalars.

``_transform_recursive`` decides per element how to handle a value. For a sequence
it first asks ``_no_transform_needed(inner_type)`` and, when that is true, returns
the list untouched -- the decision is made once for the whole sequence rather than
once per element.

Upstream that predicate accepts only bare ``float`` and ``int``::

    def _no_transform_needed(annotation: type) -> bool:
        return annotation == float or annotation == int

A union of scalars needs no transformation either, but misses the check, so every
element takes the union branch and recurses once per member. That is what
``EncodedTextChunk.tokens`` is: protobuf's JSON mapping emits ``int64`` as a string
and parsers accept either, so the generated annotation is ``Union[str, int]``.
Measured on a 59,240-token sample body: 227 ms, 150,008 ``_transform_recursive``
calls and 2,350,101 ``isinstance`` checks, to hand back the list unchanged. It is
CPU-bound on the single event loop every client handle shares, so concurrent
operations serialise behind it.

This rebinds the predicate to also accept unions made only of scalars. Bare
``str``, ``bool`` and ``None`` keep the upstream element walk, so the change is
confined to scalar-union sequences -- ``EncodedTextChunk.tokens`` and
``RoutedExperts.shape`` today. For every value but one the output is identical: the
walk returns scalars, containers and ``None`` unchanged against a scalar annotation.
The exception is a pydantic model inside such a list, which the walk ``model_dump``s
and the fast path hands on as-is, so JSON encoding raises instead of sending a dict
where the schema says ``str | int``.

Applied from ``together.lib.__init__`` because ``_utils/_transform.py`` is
generator-owned: every commit to it is from ``stainless-app[bot]``, two of them
perf changes to this exact area, so an edit there would be reverted or conflict on
the next generation. ``src/together/lib/`` is the one tree ``CONTRIBUTING.md``
guarantees the generator never touches.

Self-removing: ``apply()`` first checks whether the upstream predicate already
handles a scalar union and does nothing if so, so this becomes inert the moment
Stainless fixes it.
"""

from __future__ import annotations

from types import NoneType
from typing import Union, cast
from typing_extensions import get_args

from .._utils import _transform
from .._utils._typing import is_union_type

__all__ = ["apply"]

# Scalars that may appear as union members. Bare members of this set are left to
# upstream, which already fast-paths ``int`` and ``float``.
_SCALARS = (float, int, str, bool, NoneType)


def _no_transform_needed(annotation: type) -> bool:
    """Whether a sequence of this element type can skip the per-element walk.

    Upstream's ``float``/``int`` plus unions whose every member is a scalar.
    ``Annotated[str, PropertyInfo(format=...)]`` is not ``== str``, so formatted
    values still take the full walk, as does a union with any non-scalar member --
    a TypedDict, a model.
    """
    if annotation == float or annotation == int:
        return True
    if is_union_type(annotation):
        return all(arg in _SCALARS for arg in get_args(annotation))
    return False


def apply() -> bool:
    """Install the widened predicate. Returns whether it was needed.

    Never raises: a transformer that has moved on from this shape leaves the
    original in place and the SDK keeps working, just slower.
    """
    try:
        original = _transform._no_transform_needed  # noqa: SLF001
        # `Union[str, int]` is a special form, not a `type`; the upstream signature
        # says `type` but the runtime value it receives from `extract_type_arg` is
        # exactly this shape.
        if original(cast("type", Union[str, int])):
            return False  # upstream already covers it
        _transform._no_transform_needed = _no_transform_needed  # noqa: SLF001
    except Exception:  # pragma: no cover - never break import over a perf patch
        return False
    return True
