"""The scalar-union fast path in ``together.lib._transform_patch``.

Importing ``together.lib`` (below) runs ``together/__init__``, which applies the patch.

``apply()`` never raises, so a regenerated transformer that renames or moves the
predicate would switch the patch off without a trace. These tests are the tripwire:
the first one fails the moment the patch stops being installed.
"""

from __future__ import annotations

from typing import Any, List, Union, Optional
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

import pytest

from together.lib import _transform_patch
from together._types import SequenceNotStr
from together._utils import PropertyInfo, transform, _transform, async_transform
from together._models import BaseModel

parametrize = pytest.mark.parametrize("use_async", [False, True], ids=["sync", "async"])


async def run(data: Any, expected_type: object, use_async: bool) -> Any:
    if use_async:
        return await async_transform(data, expected_type=expected_type)
    return transform(data, expected_type=expected_type)


def _upstream_predicate(annotation: type) -> bool:
    return annotation == float or annotation == int


class Chunk(TypedDict, total=False):
    tokens: Required[SequenceNotStr[Union[str, int]]]


class Stops(TypedDict, total=False):
    stops: List[str]


class Inner(TypedDict, total=False):
    my_field: Annotated[str, PropertyInfo(alias="myField")]


class Mixed(TypedDict, total=False):
    items: List[Union[str, Inner]]


class Dated(TypedDict, total=False):
    days: Annotated[List[date], PropertyInfo(format="iso8601")]


class Model(BaseModel):
    a: int = 1


def test_patch_is_installed() -> None:
    assert _transform._no_transform_needed is _transform_patch._no_transform_needed


@parametrize
async def test_scalar_union_list_takes_fast_path(use_async: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    if use_async:
        async_recurse = _transform._async_transform_recursive

        async def counting(*args: Any, **kwargs: Any) -> Any:
            nonlocal calls
            calls += 1
            return await async_recurse(*args, **kwargs)

        monkeypatch.setattr(_transform, "_async_transform_recursive", counting)
    else:
        recurse = _transform._transform_recursive

        def counting_sync(*args: Any, **kwargs: Any) -> Any:
            nonlocal calls
            calls += 1
            return recurse(*args, **kwargs)

        monkeypatch.setattr(_transform, "_transform_recursive", counting_sync)

    tokens: List[Union[str, int]] = list(range(50_000))
    result = await run({"tokens": tokens}, Chunk, use_async)

    assert result["tokens"] is tokens
    # One call for the mapping and one for its field, instead of one per element.
    assert calls < 10


VALID_TOKENS = [
    [],
    [1, 2, 3],
    ["1", "2"],
    [1, "2", 3],
    (4, 5, 6),
]


@parametrize
@pytest.mark.parametrize("tokens", VALID_TOKENS, ids=["empty", "ints", "strings", "mixed", "tuple"])
async def test_valid_tokens_match_upstream(use_async: bool, tokens: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    patched = await run({"tokens": tokens}, Chunk, use_async)
    monkeypatch.setattr(_transform, "_no_transform_needed", _upstream_predicate)
    assert patched == await run({"tokens": tokens}, Chunk, use_async)


@parametrize
async def test_union_with_non_scalar_member_keeps_full_walk(use_async: bool) -> None:
    result = await run({"items": ["a", {"my_field": "b"}]}, Mixed, use_async)
    assert result == {"items": ["a", {"myField": "b"}]}


@parametrize
async def test_formatted_scalars_keep_full_walk(use_async: bool) -> None:
    result = await run({"days": [date(2026, 1, 2)]}, Dated, use_async)
    assert result == {"days": ["2026-01-02"]}


@parametrize
async def test_bare_str_list_matches_upstream(use_async: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    patched = await run({"stops": ["x", Model(a=2)]}, Stops, use_async)
    assert patched == {"stops": ["x", {"a": 2}]}
    monkeypatch.setattr(_transform, "_no_transform_needed", _upstream_predicate)
    assert patched == await run({"stops": ["x", Model(a=2)]}, Stops, use_async)


@parametrize
async def test_model_inside_scalar_union_list_passes_through(use_async: bool) -> None:
    # The one documented difference from upstream, which would model_dump it into a
    # slot typed `str | int`.
    model = Model(a=5)
    result = await run({"tokens": [1, model]}, Chunk, use_async)
    assert result["tokens"][1] is model


def test_predicate() -> None:
    predicate = _transform_patch._no_transform_needed
    assert predicate(int) and predicate(float)
    assert predicate(Union[str, int])  # type: ignore[arg-type]
    assert predicate(Optional[int])  # type: ignore[arg-type]
    assert not predicate(str)
    assert not predicate(bool)
    assert not predicate(Union[str, Inner])  # type: ignore[arg-type]


def test_apply_is_inert_when_upstream_covers_unions(monkeypatch: pytest.MonkeyPatch) -> None:
    def covers(_annotation: type) -> bool:
        return True

    monkeypatch.setattr(_transform, "_no_transform_needed", covers)
    assert _transform_patch.apply() is False
    assert _transform._no_transform_needed is covers


def test_apply_never_raises_when_predicate_is_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delattr(_transform, "_no_transform_needed")
    assert _transform_patch.apply() is False
