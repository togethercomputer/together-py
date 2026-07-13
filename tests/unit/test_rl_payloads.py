from __future__ import annotations

from typing import Any

import pytest

from together.lib.beta.rl._payloads import _truncate_sequences


@pytest.mark.parametrize(
    "data, max_len, expected",
    [
        pytest.param([1, 2, 3, 4, 5], 3, [1, 2, 3], id="int_list"),
        pytest.param([0.1, 0.2, 0.3, 0.4], 2, [0.1, 0.2], id="float_list"),
        pytest.param([1, 2], 8, [1, 2], id="short_unchanged"),
        pytest.param(
            {"a": {"b": [10, 20, 30, 40]}, "c": "keep"},
            2,
            {"a": {"b": [10, 20]}, "c": "keep"},
            id="nested_dict",
        ),
        pytest.param(
            [{"tokens": [1, 2, 3, 4, 5]}, {"tokens": [6, 7, 8, 9]}],
            3,
            [{"tokens": [1, 2, 3]}, {"tokens": [6, 7, 8]}],
            id="list_of_dicts",
        ),
    ],
)
def test_truncate_sequences(data: Any, max_len: int, expected: Any) -> None:
    assert _truncate_sequences(data, max_len) == expected
