from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from together.post_training import tinker as tinker_compat, _payloads
from tests.unit.post_training_wait import patch_wait
from together.post_training.tinker import _sampling
from tests.unit._post_training_tinker import (
    _OPERATION,
    _WEIGHTS_SYNC_OUTPUT,
    _close,
    _training_client,
    _session_with_operations,
)
from together.post_training.clients.session import SessionClient
from together.types.post_training.sample_result import SampleResult
from together.types.post_training.sampled_sequence import SampledSequence


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


@pytest.mark.parametrize("collect", ["sync", "async"])
@pytest.mark.parametrize(
    "option",
    [
        {"topk_sample_logprobs": 5},
        {"target_prompt_logprobs": types.TensorData([1], dtype="int64")},
        {"prompt_alt_tokens_k": 2},
        {"prompt_logprobs_last_n": 4},
    ],
    ids=lambda option: next(iter(option)),
)
def test_sample_rejects_tinker_options_together_lacks(collect: str, option: dict[str, Any]) -> None:
    """Tinker sampling options Together lacks fail by name before any request is sent."""
    sample = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(sample=sample)
    client = tinker_compat.SamplingClient(session)
    args = (types.ModelInput.from_ints([1]), 1, types.SamplingParams(max_tokens=1))

    with pytest.raises(NotImplementedError, match=next(iter(option))):
        if collect == "sync":
            client.sample(*args, **option)
        else:
            asyncio.run(client.sample_async(*args, **option))

    sample.assert_not_awaited()
    _close(session)


@pytest.mark.parametrize("collect", ["sync", "async"])
def test_compute_logprobs_rejects_last_n(collect: str) -> None:
    sample = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(sample=sample)
    client = tinker_compat.SamplingClient(session)
    prompt = types.ModelInput.from_ints([1, 2])

    with pytest.raises(NotImplementedError, match="prompt_logprobs_last_n"):
        if collect == "sync":
            client.compute_logprobs(prompt, prompt_logprobs_last_n=1)
        else:
            asyncio.run(client.compute_logprobs_async(prompt, prompt_logprobs_last_n=1))

    sample.assert_not_awaited()
    _close(session)


def test_sampling_client_result_returns_itself() -> None:
    """Tinker code calls .result() on the client save_weights_and_get_sampling_client returns."""
    session = _session_with_operations()
    client = tinker_compat.SamplingClient(session)

    assert client.result() is client
    _close(session)


def _one_sequence_output(*, prompt_logprobs: list[float] | None = None) -> Any:
    return SimpleNamespace(
        results=[
            SampleResult(
                policy_segments=[],
                sequences=[SampledSequence(prompt_cache_hit_tokens=0, stop_reason="STOP_REASON_STOP", tokens=[1])],
                prompt_logprobs=prompt_logprobs,
            )
        ]
    )


async def _passthrough_payload(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
    return result


async def test_plain_sample_and_compute_logprobs_are_awaitable_inside_a_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    """tinker-cookbook's completers await the plain sample call; tinker 0.39 deprecates sample_async."""
    patch_wait(monkeypatch, _one_sequence_output(prompt_logprobs=[0.0, -0.25]))
    monkeypatch.setattr(_payloads, "resolve_result_payload", _passthrough_payload)
    session = _session_with_operations(sample=AsyncMock(return_value=_OPERATION))
    client = tinker_compat.SamplingClient(session)

    response = await client.sample(
        types.ModelInput.from_ints([1, 2]), num_samples=1, sampling_params=types.SamplingParams(max_tokens=1)
    )
    logprobs = await client.compute_logprobs(types.ModelInput.from_ints([1, 2]))

    assert isinstance(response, types.SampleResponse)
    assert logprobs == [None, -0.25]
    await session.detach_async()


async def test_samples_inside_a_loop_are_sent_concurrently(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unlike training requests, a rollout's samples are not queued one behind another."""
    patch_wait(monkeypatch, _one_sequence_output())
    monkeypatch.setattr(_payloads, "resolve_result_payload", _passthrough_payload)
    in_flight = 0
    peak = 0

    async def sample(*_: Any, **__: Any) -> Any:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.05)
        in_flight -= 1
        return _OPERATION

    session = _session_with_operations(sample=AsyncMock(side_effect=sample))
    client = tinker_compat.SamplingClient(session)
    params = types.SamplingParams(max_tokens=1)

    futures = [
        client.sample(types.ModelInput.from_ints([1, 2]), num_samples=1, sampling_params=params) for _ in range(3)
    ]
    await asyncio.gather(*futures)

    assert peak == 3
    await session.detach_async()
