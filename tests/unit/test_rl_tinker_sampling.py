from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from tests.unit.rl_wait import patch_wait
from together.lib.beta.rl import tinker as tinker_compat, _payloads
from tests.unit._rl_tinker import (
    _OPERATION,
    _WEIGHTS_SYNC_OUTPUT,
    _close,
    _training_client,
    _session_with_operations,
)
from together.lib.beta.rl.tinker import _sampling
from together.lib.beta.rl.clients.session import SessionClient
from together.types.beta.rl.sample_result import SampleResult
from together.types.beta.rl.sampled_sequence import SampledSequence


def test_sample_forwards_prompt_logprob_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Distillation requests must reach both wire flags instead of returning empty compatibility fields."""
    submitted: list[dict[str, Any]] = []

    async def submit(_session: SessionClient, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    monkeypatch.setattr(_sampling, "_submit_sample_batch", submit)
    session = _session_with_operations()
    tinker_compat.SamplingClient(session).sample(
        types.ModelInput.from_ints([1]),
        1,
        types.SamplingParams(max_tokens=1),
        include_prompt_logprobs=True,
        topk_prompt_logprobs=7,
    )

    assert submitted[0]["prompt_logprobs"] is True
    assert submitted[0]["topk_prompt_logprobs"] == 7
    _close(session)


def test_sampling_client_is_valid_until_the_next_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    """The normal publish/sample/train loop must work, then an old client must fail after republish."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))
    submitted: list[dict[str, Any]] = []

    async def submit(_session: SessionClient, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    monkeypatch.setattr(_sampling, "_submit_sample_batch", submit)
    training = _training_client(session)
    first = training.save_weights_and_get_sampling_client()
    first.sample(
        types.ModelInput.from_ints([1]),
        1,
        types.SamplingParams(max_tokens=1),
    )
    training.save_weights_and_get_sampling_client()

    assert len(submitted) == 1
    with pytest.raises(RuntimeError, match="snapshot checkpoints are not supported"):
        first.sample(
            types.ModelInput.from_ints([1]),
            1,
            types.SamplingParams(max_tokens=1),
        )


def test_sample_result_resolves_payload_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """Large sample outputs arrive as payload_id stubs; dropping the
    resolve_result_payload hop looks redundant and passes every other test."""
    output = SimpleNamespace(payload_id="stub")
    patch_wait(monkeypatch, output)
    wire_result = SampleResult(
        policy_segments=[],
        sequences=[
            SampledSequence(
                prompt_cache_hit_tokens=0,
                stop_reason="STOP_REASON_STOP",
                tokens=["7", 8],
                logprobs=[-0.5, -0.25],
            )
        ],
    )
    resolved_with: list[Any] = []

    async def fake_resolve(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
        resolved_with.append(result)
        return SimpleNamespace(results=[wire_result])

    monkeypatch.setattr(_payloads, "resolve_result_payload", fake_resolve)
    session = _session_with_operations(sample=AsyncMock(return_value=_OPERATION))

    response = (
        tinker_compat.SamplingClient(session)
        .sample(
            types.ModelInput.from_ints([1, 2, 3]),
            num_samples=1,
            sampling_params=types.SamplingParams(max_tokens=4),
        )
        .result()
    )

    assert resolved_with == [output]
    assert isinstance(response, types.SampleResponse)
    assert response.sequences[0].tokens == [7, 8]


async def test_sample_async_returns_sample_response(monkeypatch: pytest.MonkeyPatch) -> None:
    wire_result = SampleResult(
        policy_segments=[],
        sequences=[
            SampledSequence(
                prompt_cache_hit_tokens=0,
                stop_reason="STOP_REASON_STOP",
                tokens=[1, 2],
                logprobs=[-0.1, -0.2],
            )
        ],
    )
    patch_wait(monkeypatch, SimpleNamespace(results=[wire_result]))

    async def fake_resolve(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
        return result

    monkeypatch.setattr(_payloads, "resolve_result_payload", fake_resolve)
    session = _session_with_operations(sample=AsyncMock(return_value=_OPERATION))

    response = await tinker_compat.SamplingClient(session).sample_async(
        types.ModelInput.from_ints([1, 2, 3]),
        num_samples=1,
        sampling_params=types.SamplingParams(max_tokens=4),
    )
    assert isinstance(response, types.SampleResponse)
    assert response.sequences[0].tokens == [1, 2]
    await session.detach_async()


@pytest.mark.parametrize("collect", ["sync", "async"])
def test_sampling_rejects_bad_arguments_before_touching_the_session(collect: str) -> None:
    """Both twins must validate on the caller's own frame. Deferred into the submitted
    coroutine, a pinned or stopped session masks the ValueError with its own error."""
    session = _session_with_operations(sample=AsyncMock(return_value=_OPERATION))
    client = tinker_compat.SamplingClient(session)
    args = (types.ModelInput.from_ints([1]), 1, types.SamplingParams(max_tokens=1))

    with pytest.raises(ValueError, match="topk_prompt_logprobs"):
        if collect == "sync":
            client.sample(*args, topk_prompt_logprobs=21)
        else:
            asyncio.run(client.sample_async(*args, topk_prompt_logprobs=21))
    _close(session)


_ENTRY_POINTS = ["sample", "sample_async", "compute_logprobs", "compute_logprobs_async"]

_GATE_OUTPUT = SimpleNamespace(
    results=[
        SampleResult(
            policy_segments=[],
            sequences=[
                SampledSequence(
                    prompt_cache_hit_tokens=0,
                    stop_reason="STOP_REASON_STOP",
                    tokens=[1],
                    logprobs=[-0.5],
                )
            ],
            prompt_logprobs=[0.0, -0.25],
        )
    ]
)


def _invoke(client: tinker_compat.SamplingClient, entry: str) -> None:
    prompt = types.ModelInput.from_ints([1])
    sample_args = (prompt, 1, types.SamplingParams(max_tokens=1))
    if entry == "sample":
        client.sample(*sample_args)
    elif entry == "sample_async":
        asyncio.run(client.sample_async(*sample_args))
    elif entry == "compute_logprobs":
        client.compute_logprobs(prompt)
    else:
        asyncio.run(client.compute_logprobs_async(prompt))


@pytest.mark.parametrize("entry", _ENTRY_POINTS)
def test_stale_sampling_client_is_rejected_at_every_entry_point(entry: str) -> None:
    published = _sampling._PublishedWeights(version=2)
    stale = tinker_compat.SamplingClient(_session_with_operations(), published, 1, _allow_stale=False)

    with pytest.raises(RuntimeError, match="stale"):
        _invoke(stale, entry)
    _close(stale._session)


@pytest.mark.parametrize("entry", _ENTRY_POINTS)
def test_allow_stale_sampling_client_passes_the_gate(entry: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """allow_stale must reach submission at every gated entry point, not just ``sample``."""
    patch_wait(monkeypatch, _GATE_OUTPUT)

    async def fake_resolve(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
        return result

    monkeypatch.setattr(_payloads, "resolve_result_payload", fake_resolve)
    submitted: list[dict[str, Any]] = []

    async def submit(_session: SessionClient, **kwargs: Any) -> Any:
        submitted.append(kwargs)
        return _OPERATION

    monkeypatch.setattr(_sampling, "_submit_sample_batch", submit)
    published = _sampling._PublishedWeights(version=2)
    stale = tinker_compat.SamplingClient(_session_with_operations(), published, 1, _allow_stale=True)

    _invoke(stale, entry)

    assert len(submitted) == 1
    _close(stale._session)


def test_compute_logprobs_posts_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    """compute_logprobs is a one-token sample with prompt_logprobs on; index 0 comes back None."""
    output = SimpleNamespace(
        results=[
            SampleResult(
                policy_segments=[],
                sequences=[SampledSequence(prompt_cache_hit_tokens=0, stop_reason="STOP_REASON_STOP", tokens=[1])],
                prompt_logprobs=[0.0, -0.25, -0.5],
            )
        ]
    )
    patch_wait(monkeypatch, output)

    async def fake_resolve(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
        return result

    monkeypatch.setattr(_payloads, "resolve_result_payload", fake_resolve)
    posted: dict[str, Any] = {}

    async def sample(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        posted.update(kwargs)
        return _OPERATION

    session = _session_with_operations(sample=sample)
    result = tinker_compat.SamplingClient(session).compute_logprobs(types.ModelInput.from_ints([1, 2, 3])).result()

    assert result == [None, -0.25, -0.5]
    assert posted["prompt_logprobs"] is True
    assert posted["sampling_params"]["max_tokens"] == 1
    _close(session)
