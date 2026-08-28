from __future__ import annotations

import asyncio
import warnings
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from tests.unit.rl_wait import patch_wait
from together.lib.beta.rl import tinker as tinker_compat, _operations as rl_ops
from tests.unit._rl_tinker import (
    _OPERATION,
    _WEIGHTS_SYNC_OUTPUT,
    _close,
    _tensors,
    _rl_loop_datum,
    _advantage_datum,
    _training_client,
    _session_with_operations,
)


def test_save_weights_publishes_synchronously(monkeypatch: pytest.MonkeyPatch) -> None:
    """SYNCHRONOUS so the returned SamplingClient sees the updated policy;
    BACKGROUND_PUBLISH would silently turn the loop off-policy."""
    timeouts = patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    sampling = _training_client(session).save_weights_and_get_sampling_client()

    weights_sync.assert_awaited_once_with("sess", weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    assert timeouts == [None]
    assert isinstance(sampling, tinker_compat.SamplingClient)


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({}, None),
        ({"name": "ckpt"}, r"ignores \['name'\]"),
        ({"retry_config": {"max_retries": 3}}, r"ignores \['retry_config'\]"),
    ],
)
def test_save_weights_warns_on_name_and_retry_config(
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict[str, Any],
    match: str | None,
) -> None:
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))
    client = _training_client(session)

    if match is None:
        with warnings.catch_warnings(record=True) as quiet:
            warnings.simplefilter("always")
            client.save_weights_and_get_sampling_client(**kwargs)
        assert quiet == []
    else:
        # Match the ignored-arg list, not the body ("named checkpoints" contains "name").
        with pytest.warns(UserWarning, match=match):
            client.save_weights_and_get_sampling_client(**kwargs)


async def test_save_weights_async_returns_sampling_client(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    sampling = await _training_client(session).save_weights_and_get_sampling_client_async()

    weights_sync.assert_awaited_once_with("sess", weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    assert isinstance(sampling, tinker_compat.SamplingClient)
    await session.detach_async()


def test_future_result_waits_without_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """tinker futures wait indefinitely, and a long rollout easily outlives the SDK's
    default 300 s operation deadline — normalizing to DEFAULT_OPERATION_TIMEOUT would
    kill hour-long steps mid-loop."""
    timeouts = patch_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))

    _training_client(session).optim_step(types.AdamParams(learning_rate=1e-4)).result()

    assert timeouts == [None]


def test_future_result_forwards_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tinker's timeout argument must bound polling instead of raising TypeError."""
    timeouts = patch_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))

    _training_client(session).optim_step(types.AdamParams(learning_rate=1e-4)).result(timeout=2.5)

    assert timeouts == [pytest.approx(2.5, abs=0.01)]


def test_forward_backward_result_is_tinker_shaped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolving forward_backward must yield ForwardBackwardOutput with loss:sum, not invent logprobs."""
    patch_wait(monkeypatch, {"loss": 0.5, "metrics": {"loss/kl_ref/mean": 0.01}})
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    output = _training_client(session).forward_backward([_rl_loop_datum()], "importance_sampling").result()

    assert isinstance(output, types.ForwardBackwardOutput)
    assert output.metrics["loss:sum"] == 0.5
    assert output.metrics["loss/kl_ref/mean"] == 0.01
    assert output.loss_fn_outputs == []


def _policy_datum() -> types.Datum:
    """A minimal policy-loss Datum; _rl_loop_datum's alignment is asserted elsewhere."""
    return types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([2, 0], dtype="int64"),
            "logprobs": types.TensorData([-0.5, -0.25], dtype="float32"),
            "advantages": types.TensorData([0.5, 0.5], dtype="float32"),
        },
    )


def _cross_entropy_datum() -> types.Datum:
    return types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([2, 0], dtype="int64"),
            "weights": types.TensorData([1.0, 0.0], dtype="float32"),
        },
    )


@pytest.mark.parametrize(
    ("datum", "loss_fn", "expected_type", "expected_loss_fn_inputs"),
    [
        (
            _policy_datum(),
            "importance_sampling",
            "LOSS_TYPE_IMPORTANCE_SAMPLING",
            {
                "target_tokens": {"data": [2, 0], "dtype": "int64"},
                "logprobs": {"data": [-0.5, -0.25], "dtype": "float32"},
                "advantages": {"data": [0.5, 0.5], "dtype": "float32"},
            },
        ),
        (
            _cross_entropy_datum(),
            "cross_entropy",
            "LOSS_TYPE_CROSS_ENTROPY",
            {
                "target_tokens": {"data": [2, 0], "dtype": "int64"},
                "weights": {"data": [1.0, 0.0], "dtype": "float32"},
            },
        ),
    ],
)
def test_forward_backward_submits_generic_tensor_map(
    datum: types.Datum,
    loss_fn: types.LossFnType,
    expected_type: str,
    expected_loss_fn_inputs: dict[str, Any],
) -> None:
    """Datums go out under loss_fn_inputs, never Together's named loss_inputs shape."""
    submitted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)
    _training_client(session).forward_backward([datum], loss_fn)

    request = submitted[0]
    assert request["loss"]["type"] == expected_type
    sample = request["samples"][0]
    assert "loss_inputs" not in sample
    assert sample["loss_fn_inputs"] == expected_loss_fn_inputs


def test_operations_post_eagerly_at_call_time() -> None:
    """grpo_gsm8k fires all sample POSTs before collecting any, and submits
    forward_backward + optim_step before resolving either; a lazy-submit refactor
    would serialize the whole loop with every other test still green."""
    submitted: list[str] = []

    def poster(name: str) -> Any:
        async def post(_session_id: str, **_kwargs: Any) -> dict[str, Any]:
            submitted.append(name)
            return _OPERATION

        return post

    session = _session_with_operations(
        forward_backward=poster("forward_backward"),
        optim_step=poster("optim_step"),
        sample=poster("sample"),
    )
    training = _training_client(session)

    training.forward_backward([_rl_loop_datum()], "importance_sampling")
    training.optim_step(types.AdamParams(learning_rate=1e-4))
    assert submitted == ["forward_backward", "optim_step"]

    tinker_compat.SamplingClient(session).sample(
        types.ModelInput.from_ints([1, 2, 3]),
        num_samples=1,
        sampling_params=types.SamplingParams(max_tokens=4),
    )
    assert submitted == ["forward_backward", "optim_step", "sample"]


def test_fractional_weights_warn_for_policy_losses() -> None:
    """Together binarizes policy-loss weights while Tinker multiplies them in, so a
    ported script would silently optimize a different objective without this warning."""
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([2, 0], dtype="int64"),
            "logprobs": types.TensorData([-0.5, -0.25], dtype="float32"),
            "advantages": types.TensorData([0.5, 0.5], dtype="float32"),
            "weights": types.TensorData([0.5, 1.0], dtype="float32"),
        },
    )
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    with pytest.warns(UserWarning, match="gradients differ from Tinker"):
        _training_client(session).forward_backward([datum], "importance_sampling")


@pytest.mark.parametrize(
    ("loss_fn", "input_keys", "weights"),
    [
        # cross_entropy honors fractional weights, so there is nothing to warn about...
        ("cross_entropy", ("target_tokens",), [0.5, 1.0]),
        # ...and a 0/1 policy weight already means what Together will do with it.
        ("importance_sampling", ("target_tokens", "logprobs", "advantages"), [0.0, 1.0]),
    ],
)
def test_weights_do_not_warn_when_semantics_agree(
    loss_fn: types.LossFnType, input_keys: tuple[str, ...], weights: list[float]
) -> None:
    inputs = {**_tensors(*input_keys), "weights": types.TensorData(weights, dtype="float32")}
    datum = types.Datum(model_input=types.ModelInput.from_ints([1, 2]), loss_fn_inputs=inputs)
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _training_client(session).forward_backward([datum], loss_fn)


async def test_training_async_returns_shared_future(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, {"loss": 0.25, "metrics": {}})
    session = _session_with_operations(
        forward_backward=AsyncMock(return_value=_OPERATION),
        optim_step=AsyncMock(return_value=_OPERATION),
    )
    training = _training_client(session)

    fwd = await training.forward_backward_async([_rl_loop_datum()], "importance_sampling")
    opt = await training.optim_step_async(types.AdamParams(learning_rate=1e-4))
    assert isinstance(fwd, tinker_compat.APIFuture)
    assert isinstance(opt, tinker_compat.APIFuture)
    output = await fwd
    assert output.metrics["loss:sum"] == 0.25
    assert await opt == types.OptimStepResponse()
    await session.detach_async()


@pytest.mark.parametrize("collect", ["sync", "async"])
@pytest.mark.parametrize("loss_fn", ["grpo", "LOSS_TYPE_PPO"])
def test_unsupported_losses_are_rejected(loss_fn: str, collect: str) -> None:
    """Both twins reject names outside Tinker's supported loss names on the caller's frame."""
    session = _session_with_operations()
    training = _training_client(session)
    data = [_rl_loop_datum()]

    with pytest.raises(ValueError, match="Unknown loss_fn"):
        if collect == "sync":
            training.forward_backward(data, cast(Any, loss_fn))
        else:
            asyncio.run(training.forward_backward_async(data, cast(Any, loss_fn)))
    _close(session)


def test_async_twin_resolves_inside_a_caller_owned_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    """A script that wraps the async twins in asyncio.run drives a loop that is not the
    session's, so a bare `return self.optim_step(...)` would raise "this event loop is
    already running" only under that caller."""
    patch_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))
    session.run(asyncio.sleep(0))
    training = _training_client(session)

    async def step() -> types.OptimStepResponse:
        future = await training.optim_step_async(types.AdamParams(learning_rate=1e-4))
        return await future.result_async()

    assert asyncio.run(step()) == types.OptimStepResponse()
    _close(session)


def test_overlapping_result_async_calls_run_concurrently(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two operations collected from a foreign loop must poll at the same time; bridging
    them one at a time would silently turn an N-way rollout into a sequential one."""

    patch_wait(monkeypatch, {"loss": 0.5, "metrics": {}})
    complete = rl_ops.async_wait_for_operation
    in_flight = 0
    peak_in_flight = 0

    async def slow(**kwargs: Any) -> Any:
        nonlocal in_flight, peak_in_flight
        in_flight += 1
        peak_in_flight = max(peak_in_flight, in_flight)
        try:
            await asyncio.sleep(0)
        finally:
            in_flight -= 1
        return await complete(**kwargs)

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", slow)
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))
    session.run(asyncio.sleep(0))
    training = _training_client(session)

    async def train_twice() -> list[types.ForwardBackwardOutput]:
        futures = await asyncio.gather(
            training.forward_backward_async([_rl_loop_datum()], "importance_sampling"),
            training.forward_backward_async([_rl_loop_datum()], "importance_sampling"),
        )
        return list(await asyncio.gather(*(future.result_async() for future in futures)))

    outputs = asyncio.run(train_twice())

    assert [output.metrics["loss:sum"] for output in outputs] == [0.5, 0.5]
    assert peak_in_flight == 2, "the two polls ran back to back instead of together"
    _close(session)


def test_forward_backward_reports_an_empty_payload_plainly(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, None)
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))
    future = _training_client(session).forward_backward([_rl_loop_datum()], "importance_sampling")

    with pytest.raises(RuntimeError, match="empty output"):
        future.result()
    _close(session)


def test_forward_backward_sends_loss_with_flat_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, {"loss": 1.0, "metrics": {}})
    posted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> Any:
        posted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)

    _training_client(session).forward_backward([_advantage_datum()], "ppo").result()

    assert posted[0]["loss"]["type"] == "LOSS_TYPE_PPO"
    assert posted[0]["samples"][0]["loss_fn_inputs"]["advantages"]["data"] == [0.0, 0.5, 0.5]
    _close(session)
