from __future__ import annotations

from typing import Any, cast

import pytest

from together.lib.beta.rl._payloads import _shrink_for_validation


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
        # Short strings elsewhere must survive so the body still validates.
        pytest.param({"dtype": "float32"}, 8, {"dtype": "float32"}, id="short_strings_kept"),
        # A tensor's shape/CSR indices describe the full array, so keeping them beside a
        # truncated `data` would ship a self-contradicting pair.
        pytest.param(
            {"target_tokens": {"data": [1, 2, 3, 4], "dtype": "int64", "shape": [4], "sparse_col_indices": [0, 1]}},
            2,
            {"target_tokens": {"data": [1, 2], "dtype": "int64"}},
            id="tensor_metadata_dropped",
        ),
    ],
)
def test_shrink_for_validation(data: Any, max_len: int, expected: Any) -> None:
    assert _shrink_for_validation(data, max_len) == expected


def test_validation_body_shares_budget_across_model_input_chunks() -> None:
    body = {
        "samples": [
            {
                "model_input": {
                    "chunks": [
                        {"encoded_text": {"tokens": [1, 2, 3, 4, 5]}},
                        {"encoded_text": {"tokens": [6, 7, 8, 9, 10]}},
                    ]
                }
            }
        ]
    }

    validation_body = cast("dict[str, Any]", _shrink_for_validation(dict(body)))

    assert validation_body["samples"][0]["model_input"]["chunks"] == [
        {"encoded_text": {"tokens": [1, 2, 3, 4, 5]}},
        {"encoded_text": {"tokens": [6, 7, 8]}},
    ]


def test_validation_body_keeps_model_input_and_loss_tensors_aligned() -> None:
    body = {
        "samples": [
            {
                "model_input": {
                    "chunks": [
                        {"encoded_text": {"tokens": [1, 2, 3]}},
                        {"encoded_text": {"tokens": [4, 5, 6, 7, 8]}},
                        {"encoded_text": {"tokens": [9, 10]}},
                    ]
                },
                "loss_fn_inputs": {
                    "target_tokens": {
                        "data": list(range(10)),
                        "dtype": "int64",
                        "shape": [10],
                    },
                    "weights": {
                        "data": [1.0] * 10,
                        "dtype": "float32",
                    },
                },
            }
        ]
    }

    validation_body = cast("dict[str, Any]", _shrink_for_validation(dict(body)))
    sample = validation_body["samples"][0]

    assert [chunk["encoded_text"]["tokens"] for chunk in sample["model_input"]["chunks"]] == [
        [1, 2, 3],
        [4, 5, 6, 7, 8],
    ]
    assert len(sample["loss_fn_inputs"]["target_tokens"]["data"]) == 8
    assert len(sample["loss_fn_inputs"]["weights"]["data"]) == 8
    assert "shape" not in sample["loss_fn_inputs"]["target_tokens"]
