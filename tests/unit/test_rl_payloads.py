from __future__ import annotations

import json
from typing import Any, cast

import pytest

from together._compat import model_parse
from together._models import BaseModel, construct_type_unchecked
from together.lib.beta.rl import _payloads
from together.types.beta.rl.sample_operation import Output as SampleOutput
from together.types.beta.rl.forward_backward_result import ForwardBackwardResult


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
    assert _payloads._shrink_for_validation(data, max_len) == expected


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

    validation_body = cast("dict[str, Any]", _payloads._shrink_for_validation(dict(body)))

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

    validation_body = cast("dict[str, Any]", _payloads._shrink_for_validation(dict(body)))
    sample = validation_body["samples"][0]

    assert [chunk["encoded_text"]["tokens"] for chunk in sample["model_input"]["chunks"]] == [
        [1, 2, 3],
        [4, 5, 6, 7, 8],
    ]
    assert len(sample["loss_fn_inputs"]["target_tokens"]["data"]) == 8
    assert len(sample["loss_fn_inputs"]["weights"]["data"]) == 8
    assert "shape" not in sample["loss_fn_inputs"]["target_tokens"]


_LOSS_FN_OUTPUTS = [{"tensors": {"logprobs": {"data": [-0.5, -0.25], "dtype": "float32", "shape": [2]}}}]
_SAMPLE_RESULTS = [
    {
        "policy_segments": [{"start_token": 0, "version": 0}],
        "sequences": [{"prompt_cache_hit_tokens": 0, "stop_reason": "STOP_REASON_STOP", "tokens": [1, 2]}],
    }
]


def _inline_result(result_type: type[_payloads.ResultModel], body: dict[str, Any]) -> _payloads.ResultModel:
    """Build the inline result the way the response path does, keeping `payload_id` as an extra."""
    return construct_type_unchecked(value=body, type_=result_type)


def _fake_download(monkeypatch: pytest.MonkeyPatch, payload: bytes) -> dict[str, str]:
    """Serve `payload` in place of the R2 download and return the recorded request arguments."""
    seen: dict[str, str] = {}

    async def fake_download(_client: Any, *, session_id: str, payload_id: str) -> bytes:
        seen.update(session_id=session_id, payload_id=payload_id)
        return payload

    monkeypatch.setattr(_payloads, "_download_payload", fake_download)
    return seen


@pytest.mark.parametrize(
    "result_type, inline, offloaded",
    [
        pytest.param(
            ForwardBackwardResult,
            {"loss": 1.5, "metrics": {"loss/ratio/mean": 1.0}},
            {"loss_fn_outputs": _LOSS_FN_OUTPUTS},
            id="forward_backward",
        ),
        # A sample result has no small members, so its inline body is `payload_id` alone.
        pytest.param(SampleOutput, {}, {"results": _SAMPLE_RESULTS}, id="sample"),
    ],
)
async def test_resolve_payload_merges_inline(
    result_type: type[BaseModel],
    inline: dict[str, Any],
    offloaded: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = _fake_download(monkeypatch, json.dumps(offloaded).encode())
    result = _inline_result(result_type, {**inline, "payload_id": "pay-1"})

    resolved = await _payloads.resolve_result_payload(cast(Any, object()), session_id="sess-1", result=result)

    assert seen == {"session_id": "sess-1", "payload_id": "pay-1"}
    assert isinstance(resolved, result_type)
    assert getattr(resolved, "payload_id", None) is None
    assert resolved == model_parse(result_type, {**inline, **offloaded})


async def test_resolve_payload_prefers_payload_member(monkeypatch: pytest.MonkeyPatch) -> None:
    """A member present both inline and in the payload takes the payload's value."""
    _fake_download(monkeypatch, json.dumps({"loss_fn_outputs": _LOSS_FN_OUTPUTS}).encode())
    result = _inline_result(ForwardBackwardResult, {"loss": 1.5, "loss_fn_outputs": [], "payload_id": "pay-1"})

    resolved = await _payloads.resolve_result_payload(cast(Any, object()), session_id="sess-1", result=result)

    assert resolved.loss == pytest.approx(1.5)  # pyright: ignore[reportUnknownMemberType]
    assert resolved.loss_fn_outputs is not None
    assert len(resolved.loss_fn_outputs) == 1
    logprobs = resolved.loss_fn_outputs[0].tensors["logprobs"]
    assert logprobs.data == pytest.approx([-0.5, -0.25])  # pyright: ignore[reportUnknownMemberType]


async def test_resolve_payload_rejects_non_object(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_download(monkeypatch, b"[1]")
    result = _inline_result(ForwardBackwardResult, {"loss": 1.5, "payload_id": "pay-1"})

    with pytest.raises(ValueError, match="must be a JSON object"):
        await _payloads.resolve_result_payload(cast(Any, object()), session_id="sess-1", result=result)


async def test_resolve_payload_passthrough() -> None:
    result = _inline_result(ForwardBackwardResult, {"loss": 1.5})
    assert await _payloads.resolve_result_payload(cast(Any, object()), session_id="s", result=result) is result
