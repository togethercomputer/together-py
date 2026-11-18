from __future__ import annotations

import gc
import sys
import asyncio
import warnings
import threading
import concurrent.futures
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import ANY, AsyncMock
from collections.abc import Callable

import pytest

pytest.importorskip("tinker")

import tinker
from tinker import types

from together.post_training import WeightSyncType, tinker as tinker_compat, _operations as rl_ops
from tests.unit.post_training_wait import patch_wait
from together.post_training.tinker import _training
from tests.unit._post_training_tinker import (
    _OPERATION,
    _WEIGHTS_SYNC_OUTPUT,
    _close,
    _tensors,
    _rl_loop_datum,
    _advantage_datum,
    _training_client,
    _session_with_operations,
)


def _scored_output(*logprobs: list[float]) -> dict[str, Any]:
    """A forward_only operation output, whose per-sample tensors carry the logprobs."""
    return {
        "loss": 0.5,
        "loss_fn_outputs": [{"tensors": {"logprobs": {"data": values, "dtype": "float32"}}} for values in logprobs],
    }


def _recording(order: list[str], name: str, *, delay: float = 0.0) -> AsyncMock:
    """A request stub that reaches the server, and is recorded, after ``delay`` seconds."""

    async def post(*_: Any, **__: Any) -> Any:
        await asyncio.sleep(delay)
        order.append(name)
        return _OPERATION

    return AsyncMock(side_effect=post)


def test_save_weights_publishes_synchronously_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """SYNCHRONOUS stays the default so the returned SamplingClient sees the updated policy;
    BACKGROUND_PUBLISH would silently turn the loop off-policy unless the caller asks for it."""
    timeouts = patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    sampling = _training_client(session).save_weights_and_get_sampling_client()

    weights_sync.assert_awaited_once_with("sess", idempotency_key=ANY, weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    assert timeouts == [None]
    assert isinstance(sampling, tinker_compat.SamplingClient)
    assert sampling._allow_stale is False


@pytest.mark.parametrize(
    "weight_sync_type",
    ["WEIGHT_SYNC_TYPE_SYNCHRONOUS", "WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH", "WEIGHT_SYNC_TYPE_PIPELINE"],
)
def test_save_weights_forwards_the_requested_sync_mode(
    monkeypatch: pytest.MonkeyPatch,
    weight_sync_type: WeightSyncType,
) -> None:
    """The shim must not rewrite the caller's mode; PIPELINE on LoRA is the server's call to reject."""
    timeouts = patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    _training_client(session).save_weights_and_get_sampling_client(weight_sync_type=weight_sync_type)

    weights_sync.assert_awaited_once_with("sess", idempotency_key=ANY, weight_sync_type=weight_sync_type)
    # timeout=None survives the new keyword: a publish outlives the 300 s operation default.
    assert timeouts == [None]


def test_allow_stale_reaches_the_returned_sampling_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """allow_stale must survive to the client, and the client must outlive a later publish."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))
    client = _training_client(session)

    sampling = client.save_weights_and_get_sampling_client(allow_stale=True)
    assert sampling._allow_stale is True

    client.save_weights_and_get_sampling_client()
    assert sampling._version != sampling._published_weights.version
    sampling._check_fresh()  # would raise without the opt-out


async def test_allow_stale_reaches_the_returned_sampling_client_async(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))

    sampling = await _training_client(session).save_weights_and_get_sampling_client_async(allow_stale=True)

    assert sampling._allow_stale is True
    await session.detach_async()


_ADAM = types.AdamParams(learning_rate=1e-4)
_CHECKPOINT_UUID = "123e4567-e89b-12d3-a456-426614174000"
_CHECKPOINT_OUTPUT = {"checkpoint": {"id": _CHECKPOINT_UUID, "step": 42, "created_at": "2026-10-08T00:00:00Z"}}


def test_save_state_returns_bare_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    create = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(create_training_checkpoint=create)

    saved = _training_client(session).save_state("checkpoint-001").result()

    create.assert_awaited_once_with("sess", idempotency_key=ANY)
    assert timeouts == [None]
    assert saved.path == _CHECKPOINT_UUID
    assert "://" not in saved.path
    assert "?" not in saved.path


def test_save_state_warns_on_ttl_and_overwrite(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(create_training_checkpoint=AsyncMock(return_value=_OPERATION))
    client = _training_client(session)

    with pytest.warns(UserWarning, match="ttl_seconds"):
        client.save_state("checkpoint-001", ttl_seconds=60).result()
    with pytest.warns(UserWarning, match="overwrite"):
        client.save_state("checkpoint-001", overwrite=True).result()


def test_save_weights_for_sampler_returns_bare_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    create = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(create_inference_checkpoint=create)

    saved = _training_client(session).save_weights_for_sampler("final").result()

    create.assert_awaited_once_with("sess", idempotency_key=ANY)
    assert timeouts == [None]
    assert saved.path == _CHECKPOINT_UUID


def test_save_weights_for_sampler_warns_on_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(create_inference_checkpoint=AsyncMock(return_value=_OPERATION))
    client = _training_client(session)

    with pytest.warns(UserWarning, match="ttl_seconds"):
        client.save_weights_for_sampler("final", ttl_seconds=3600).result()


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({}, None),
        ({"name": "ckpt"}, r"ignores \['name'\]"),
        ({"retry_config": {"max_retries": 3}}, r"ignores \['retry_config'\]"),
        ({"record_stability_info": True}, r"ignores \['record_stability_info'\]"),
    ],
)
def test_save_weights_warns_on_ignored_args(
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

    weights_sync.assert_awaited_once_with("sess", idempotency_key=ANY, weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
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
    """A default forward_backward yields loss:sum and the per-datum logprobs tinker code reads every step."""
    patch_wait(monkeypatch, {**_scored_output([-0.1, -0.2]), "metrics": {"loss/kl_ref/mean": 0.01}})
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    output = _training_client(session).forward_backward([_rl_loop_datum()], "importance_sampling").result()

    assert isinstance(output, types.ForwardBackwardOutput)
    assert output.metrics["loss:sum"] == 0.5
    assert output.metrics["loss/kl_ref/mean"] == 0.01
    assert output.loss_fn_outputs[0]["logprobs"].data == pytest.approx([-0.1, -0.2])
    _close(session)


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
@pytest.mark.parametrize("entrypoint", ["sync", "async"])
def test_forward_backward_submits_generic_tensor_map(
    datum: types.Datum,
    loss_fn: types.LossFnType,
    expected_type: str,
    expected_loss_fn_inputs: dict[str, Any],
    entrypoint: str,
) -> None:
    """Datums go out under loss_fn_inputs, never Together's named loss_inputs shape."""
    submitted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)
    training = _training_client(session)
    if entrypoint == "sync":
        training.forward_backward([datum], loss_fn)
    else:
        asyncio.run(training.forward_backward_async([datum], loss_fn))

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


def test_forward_sends_the_loss_config_it_scores_under() -> None:
    """The loss shapes what forward's logprobs mean, so a valid config reaches the wire and
    a bad key still raises rather than vanishing."""
    posted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> Any:
        posted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)
    training = _training_client(session)

    training.forward([_rl_loop_datum()], "ppo", {"clip_high_threshold": 0.3})

    assert posted[0]["loss"] == {"type": "LOSS_TYPE_PPO", "ppo_params": {"clip_high_threshold": 0.3}}
    assert posted[0]["forward_only"] is True
    assert posted[0]["return_loss_fn_outputs"] is True

    with pytest.raises(ValueError, match="Unsupported keys in loss_fn_config"):
        training.forward([_rl_loop_datum()], "ppo", {"nope": 1.0})
    _close(session)


def test_forward_fills_loss_fn_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """The per-datum logprobs the server returns for forward land in loss_fn_outputs."""
    patch_wait(monkeypatch, _scored_output([-0.1, -0.2]))
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    output = _training_client(session).forward([_cross_entropy_datum()], "cross_entropy").result()

    assert len(output.loss_fn_outputs) == 1
    assert output.loss_fn_outputs[0]["logprobs"].data == pytest.approx([-0.1, -0.2])
    _close(session)


def test_forward_masks_zero_weight_positions(monkeypatch: pytest.MonkeyPatch) -> None:
    """A zero-weight position scores as exactly 0.0, not a true logprob.

    forward submits a real loss with forward_only, so the loss's own masking reaches the
    logprobs it reads back. The zero is that mask artifact and is intended: the datum's
    weights go to the wire unchanged, deliberately unlike the custom path's scoring pass,
    which rewrites them to unit weights because it discards the loss.
    """
    posted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> Any:
        posted.append(kwargs)
        return _OPERATION

    patch_wait(monkeypatch, _scored_output([-0.1, 0.0]))
    session = _session_with_operations(forward_backward=forward_backward)

    output = _training_client(session).forward([_cross_entropy_datum()], "cross_entropy").result()

    assert posted[0]["samples"][0]["loss_fn_inputs"]["weights"]["data"] == [1.0, 0.0]
    assert output.loss_fn_outputs[0]["logprobs"].data == pytest.approx([-0.1, 0.0])
    _close(session)


def test_forward_sends_the_policy_inputs_its_loss_declares() -> None:
    """forward scores under a real loss, so an RL datum's policy keys go through as-is
    rather than being dropped as unreadable."""
    posted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        posted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)
    _training_client(session).forward([_rl_loop_datum()], "importance_sampling")

    assert set(posted[0]["samples"][0]["loss_fn_inputs"]) == {"target_tokens", "logprobs", "advantages"}
    _close(session)


def test_forward_forwards_a_genuinely_unknown_input_with_a_warning() -> None:
    """A key this SDK has not heard of may be a server input newer than the SDK, so it
    warns and goes through like everywhere else."""
    posted: list[dict[str, Any]] = []

    async def forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        posted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(forward_backward=forward_backward)
    datum = _rl_loop_datum()
    datum.loss_fn_inputs["router_bias"] = types.TensorData([0.0, 0.0], dtype="float32")

    with pytest.warns(UserWarning, match="Unsupported loss_fn_inputs keys"):
        _training_client(session).forward([datum], "importance_sampling")

    assert set(posted[0]["samples"][0]["loss_fn_inputs"]) == {
        "target_tokens",
        "logprobs",
        "advantages",
        "router_bias",
    }
    _close(session)


def test_forward_backward_custom_submits_grads(monkeypatch: pytest.MonkeyPatch) -> None:
    """The custom path scores the batch, then posts the client loss's dL/dlogprobs verbatim —
    not tinker's CE-weights surrogate."""
    pytest.importorskip("torch")
    import torch

    waits = iter([_scored_output([-1.0, -2.0]), {"ok": True}])

    async def fake(
        *,
        client: Any,  # noqa: ARG001
        session_id: str,  # noqa: ARG001
        operation: Any,
        timeout: float | None,  # noqa: ARG001
        interval: float,  # noqa: ARG001
    ) -> Any:
        return SimpleNamespace(
            id=getattr(operation, "id", "op"),
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output=next(waits),
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake)
    custom_posted: list[Any] = []
    scoring_posted: list[Any] = []

    async def custom_forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        custom_posted.append(kwargs)
        return _OPERATION

    async def forward_backward(_session_id: str, **kwargs: Any) -> dict[str, Any]:
        scoring_posted.append(kwargs)
        return _OPERATION

    session = _session_with_operations(
        forward_backward=forward_backward,
        custom_forward_backward=custom_forward_backward,
    )

    def loss_fn(_data: Any, logprobs_list: list[torch.Tensor]) -> tuple[torch.Tensor, dict[str, float]]:
        loss = sum(lp.sum() for lp in logprobs_list)
        return loss, {"custom_metric": 1.5}

    # Weights omitted on purpose — the custom path must synthesize zeros.
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={"target_tokens": types.TensorData([1, 2], dtype="int64")},
    )
    output = _training_client(session).forward_backward_custom([datum], loss_fn).result()

    assert output.metrics["custom_metric"] == 1.5
    assert output.loss_fn_outputs[0]["logprobs"].data == pytest.approx([-1.0, -2.0])
    assert custom_posted[0]["gradients"][0]["data"] == pytest.approx([1.0, 1.0])
    assert custom_posted[0]["samples"][0]["loss_fn_inputs"]["weights"]["data"] == [0.0, 0.0]
    # Zero weights would mask the scoring pass's logprobs, which the client loss needs.
    assert scoring_posted[0]["samples"][0]["loss_fn_inputs"]["weights"]["data"] == [1.0, 1.0]
    _close(session)


def test_custom_loss_grads_raise_when_grad_missing() -> None:
    pytest.importorskip("torch")
    import torch

    def loss_fn(_data: Any, _logprobs_list: list[torch.Tensor]) -> tuple[torch.Tensor, dict[str, float]]:
        # The loss ignores the leaves, so backward never populates their .grad.
        return torch.tensor(0.0, requires_grad=True), {}

    with pytest.raises(ValueError, match="No gradient computed"):
        _training._custom_loss_grads([], [[-1.0, -2.0]], loss_fn)


def test_forward_backward_custom_rejects_logprob_count_mismatch() -> None:
    # Two samples, but the scoring pass returned only one logprob array.
    forward_out = types.ForwardBackwardOutput(
        loss_fn_output_type="",
        loss_fn_outputs=[{"logprobs": types.TensorData([-1.0, -2.0], dtype="float32")}],
        metrics={},
    )

    def loss_fn(_data: Any, logprobs_list: list[Any]) -> tuple[Any, dict[str, float]]:
        return sum(logprobs_list), {}

    with pytest.raises(RuntimeError, match="1 logprob arrays for 2 samples"):
        _training._grads_from_forward([_unweighted_datum(), _unweighted_datum()], forward_out, loss_fn)


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
async def test_optim_step_generates_fresh_keys(async_mode: bool) -> None:
    optim_step = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(optim_step=optim_step)
    training = _training_client(session)
    params = types.AdamParams(learning_rate=1e-4)
    try:
        for _ in range(2):
            if async_mode:
                await training.optim_step_async(params)
            else:
                await asyncio.to_thread(training.optim_step, params)
    finally:
        await session.detach_async()

    keys = [call.kwargs["idempotency_key"] for call in optim_step.await_args_list]
    assert len(keys) == 2
    assert all(isinstance(key, str) and key for key in keys)
    assert keys[0] != keys[1]


@pytest.mark.parametrize(
    ("kwargs", "allow_stale"),
    [
        ({}, False),
        ({"kind": "snapshot"}, False),
        ({"kind": "snapshot", "allow_stale": True}, True),
        ({"kind": "inflight"}, True),
    ],
)
def test_sampling_client_kind_maps_onto_allow_stale(
    monkeypatch: pytest.MonkeyPatch, kwargs: dict[str, Any], allow_stale: bool
) -> None:
    """An inflight client samples whatever weights are live, which is what allow_stale means here."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))

    sampling = _training_client(session).save_weights_and_get_sampling_client(**kwargs)

    assert sampling._allow_stale is allow_stale


async def test_sampling_client_kind_maps_onto_allow_stale_async(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))

    sampling = await _training_client(session).save_weights_and_get_sampling_client_async(kind="inflight")

    assert sampling._allow_stale is True
    await session.detach_async()


def test_unknown_sampling_client_kind_is_rejected_before_publishing() -> None:
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    with pytest.raises(ValueError, match="sampling client kind"):
        _training_client(session).save_weights_and_get_sampling_client(kind=cast(Any, "pinned"))

    weights_sync.assert_not_awaited()
    _close(session)


def test_save_calls_accept_user_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """Both saves take user_metadata; Together keeps no per-checkpoint metadata."""
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(
        create_training_checkpoint=AsyncMock(return_value=_OPERATION),
        create_inference_checkpoint=AsyncMock(return_value=_OPERATION),
    )
    client = _training_client(session)

    assert client.save_state("ckpt", user_metadata={"k": "v"}).result().path == _CHECKPOINT_UUID
    assert client.save_weights_for_sampler("final", user_metadata={"k": "v"}).result().path == _CHECKPOINT_UUID


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "kwargs",
    [{"optim_params": _ADAM}, {"adam_params": _ADAM}],
    ids=["optim_params", "adam_params"],
)
async def test_optim_step_accepts_both_parameter_names(async_mode: bool, kwargs: dict[str, Any]) -> None:
    """optim_params is the argument; adam_params stays a keyword alias."""
    optim_step = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(optim_step=optim_step)
    training = _training_client(session)
    try:
        if async_mode:
            await training.optim_step_async(**kwargs)
        else:
            await asyncio.to_thread(training.optim_step, **kwargs)
    finally:
        await session.detach_async()

    assert optim_step.await_args.kwargs["adam_params"]["learning_rate"] == pytest.approx(1e-4)


@pytest.mark.parametrize("collect", ["sync", "async"])
@pytest.mark.parametrize(
    ("kwargs", "error", "match"),
    [
        ({"optim_params": _ADAM, "adam_params": _ADAM}, ValueError, "not both"),
        ({"optim_params": types.DimuonParams(learning_rate=1e-4)}, NotImplementedError, "DimuonParams"),
        ({}, TypeError, "requires optim_params"),
    ],
    ids=["both", "dimuon", "missing"],
)
def test_optim_step_rejects_params_before_submitting(
    collect: str, kwargs: dict[str, Any], error: type[Exception], match: str
) -> None:
    optim_step = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(optim_step=optim_step)
    training = _training_client(session)

    with pytest.raises(error, match=match):
        if collect == "sync":
            training.optim_step(**kwargs)
        else:
            asyncio.run(training.optim_step_async(**kwargs))

    optim_step.assert_not_awaited()
    _close(session)


@pytest.mark.parametrize("loss_fn", ["gspo", "stable_reinforce", "custom"])
def test_tinker_losses_together_lacks_are_named_unsupported(loss_fn: str) -> None:
    """Tinker losses Together lacks fail as unsupported, not as unknown names."""
    session = _session_with_operations()

    with pytest.raises(NotImplementedError, match="not supported on Together"):
        _training_client(session).forward_backward([_rl_loop_datum()], cast(Any, loss_fn))
    _close(session)


def test_forward_backward_custom_rejects_loss_handles() -> None:
    session = _session_with_operations()
    handle = tinker.LossHandle(name="loss", inputs=(), session_id="tinker-session", graph=cast(Any, None))

    with pytest.raises(NotImplementedError, match="LossHandle"):
        _training_client(session).forward_backward_custom([_rl_loop_datum()], cast(Any, handle))
    _close(session)


async def test_operation_future_coroutine_awaits_the_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tinker code wraps futures with .coroutine() for asyncio.create_task."""
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(create_training_checkpoint=AsyncMock(return_value=_OPERATION))

    future = await _training_client(session).save_state_async("ckpt")
    saved = await asyncio.create_task(future.coroutine())

    assert saved.path == _CHECKPOINT_UUID
    await session.detach_async()


async def test_publish_inside_a_loop_returns_an_awaitable_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tinker's async style awaits what the synchronous publish returns."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    pending = _training_client(session).save_weights_and_get_sampling_client(kind="inflight")
    assert not isinstance(pending, tinker_compat.SamplingClient)

    sampling = await cast(Any, pending)  # typed as the client, so the isinstance check narrows it to Never
    assert isinstance(sampling, tinker_compat.SamplingClient)
    assert sampling._allow_stale is True
    assert await sampling is sampling
    weights_sync.assert_awaited_once_with("sess", idempotency_key=ANY, weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    await session.detach_async()


def test_operation_future_converts_to_a_concurrent_future(monkeypatch: pytest.MonkeyPatch) -> None:
    """future() hands blocking or threaded code a standard Future without blocking the caller."""
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(create_training_checkpoint=AsyncMock(return_value=_OPERATION))

    future = _training_client(session).save_state("ckpt").future()

    assert isinstance(future, concurrent.futures.Future)
    assert future.result(timeout=10).path == _CHECKPOINT_UUID
    _close(session)


async def test_publish_inside_a_loop_posts_before_a_later_step(monkeypatch: pytest.MonkeyPatch) -> None:
    """The sampler must serve the weights at call time: a step awaited before the publish must not run first."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(
        weights_sync=_recording(order, "weights_sync"), optim_step=_recording(order, "optim_step")
    )
    training = _training_client(session)
    earlier = await training.save_weights_and_get_sampling_client_async()

    pending = training.save_weights_and_get_sampling_client()
    await (await training.optim_step_async(types.AdamParams(learning_rate=1e-4)))
    sampling = await pending

    assert order == ["weights_sync", "weights_sync", "optim_step"]
    assert sampling._version == 2
    with pytest.raises(RuntimeError, match="stale"):
        earlier._check_fresh()
    await session.detach_async()


async def test_consecutive_publishes_inside_a_loop_keep_call_order(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    calls: list[str] = []

    async def post(*_: Any, weight_sync_type: str, **__: Any) -> Any:
        calls.append(weight_sync_type)
        return _OPERATION

    session = _session_with_operations(weights_sync=AsyncMock(side_effect=post))
    training = _training_client(session)

    first = training.save_weights_and_get_sampling_client(weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    second = training.save_weights_and_get_sampling_client(weight_sync_type="WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH")

    assert [(await first)._version, (await second)._version] == [1, 2]
    assert calls == ["WEIGHT_SYNC_TYPE_SYNCHRONOUS", "WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH"]
    await session.detach_async()


async def test_failed_publish_inside_a_loop_does_not_block_later_steps(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The failure reaches the publish's awaiter only; later steps proceed and nothing logs it as unretrieved."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    optim_step = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(
        weights_sync=AsyncMock(side_effect=RuntimeError("sync rejected")), optim_step=optim_step
    )
    training = _training_client(session)

    pending = training.save_weights_and_get_sampling_client()
    for _ in range(2):
        await (await training.optim_step_async(types.AdamParams(learning_rate=1e-4)))
    with pytest.raises(RuntimeError, match="sync rejected"):
        await pending

    assert optim_step.await_count == 2
    assert training._published_weights.version == 0
    gc.collect()
    await asyncio.sleep(0)
    assert "never retrieved" not in caplog.text
    await session.detach_async()


async def test_async_publish_posts_before_a_step_called_after_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """The *_async publish orders later steps behind its request, like the synchronous call does."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(
        weights_sync=_recording(order, "weights_sync", delay=0.1), optim_step=_recording(order, "optim_step")
    )
    training = _training_client(session)

    publish = asyncio.ensure_future(training.save_weights_and_get_sampling_client_async())
    await asyncio.sleep(0)
    await (await training.optim_step_async(types.AdamParams(learning_rate=1e-4)))
    await publish

    assert order == ["weights_sync", "optim_step"]
    await session.detach_async()


async def test_cancelled_publish_waiter_keeps_the_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cancelling the wait must not withdraw a sync that later steps were already ordered behind."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(
        weights_sync=_recording(order, "weights_sync", delay=0.1), optim_step=_recording(order, "optim_step")
    )
    training = _training_client(session)

    publish = asyncio.ensure_future(training.save_weights_and_get_sampling_client_async())
    await asyncio.sleep(0)
    publish.cancel()
    await (await training.optim_step_async(types.AdamParams(learning_rate=1e-4)))

    assert publish.cancelled()
    assert order == ["weights_sync", "optim_step"]
    assert training._published_weights.version == 1
    await session.detach_async()


@pytest.mark.parametrize("give_up", ["timeout", "cancel"])
async def test_publish_survives_a_waiter_giving_up(monkeypatch: pytest.MonkeyPatch, give_up: str) -> None:
    """Awaits of one publish share its task; one waiter's timeout or cancel must not fail the rest."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(weights_sync=_recording(order, "weights_sync", delay=0.1))
    pending = cast(Any, _training_client(session).save_weights_and_get_sampling_client())

    other = asyncio.ensure_future(pending.result_async())
    if give_up == "timeout":
        with pytest.raises(TimeoutError):
            await pending.result_async(timeout=0.01)
    else:
        first = asyncio.ensure_future(pending.result_async())
        await asyncio.sleep(0.01)
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
    sampling = await other

    assert isinstance(sampling, tinker_compat.SamplingClient)
    assert await pending is sampling
    assert order == ["weights_sync"]
    await session.detach_async()


async def test_failed_request_after_a_cancelled_wait_is_not_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Nobody is left to see the failure, so asyncio must not report it as never retrieved."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)

    async def rejected(*_: Any, **__: Any) -> Any:
        await asyncio.sleep(0.1)
        raise RuntimeError("sync rejected")

    session = _session_with_operations(weights_sync=AsyncMock(side_effect=rejected))
    training = _training_client(session)

    publish = asyncio.ensure_future(training.save_weights_and_get_sampling_client_async())
    await asyncio.sleep(0)
    publish.cancel()
    posted = training._last_request
    assert posted is not None
    await asyncio.to_thread(concurrent.futures.wait, [posted], 10)
    await asyncio.sleep(0.05)  # let the failure reach the abandoned waiter on this loop

    assert publish.cancelled()
    assert training._published_weights.version == 0
    # The task's CancelledError traceback and the client's in-flight request both reach the waiter.
    del publish, posted, training
    gc.collect()
    await asyncio.sleep(0)
    assert "never retrieved" not in caplog.text
    await session.detach_async()


async def test_abandoned_step_wait_is_not_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A step that gives up waiting behind a publish must not leave its failure reported as never retrieved."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    release = threading.Event()

    async def rejected(*_: Any, **__: Any) -> Any:
        await asyncio.to_thread(release.wait, 10)
        raise RuntimeError("sync rejected")

    session = _session_with_operations(
        weights_sync=AsyncMock(side_effect=rejected), optim_step=AsyncMock(return_value=_OPERATION)
    )
    training = _training_client(session)

    pending = training.save_weights_and_get_sampling_client()  # posted now, never awaited
    posted = training._last_request
    assert posted is not None
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(training.optim_step_async(types.AdamParams(learning_rate=1e-4)), 0.05)
    step = training._last_request
    assert step is not None and step is not posted
    release.set()  # the publish fails only now, after the step stopped waiting for it
    await asyncio.to_thread(concurrent.futures.wait, [posted, step], 10)
    await asyncio.sleep(0.05)  # let the failure reach the abandoned waiter on its loop

    # The posted future's callbacks, the client and the pending handle all reach the waiter.
    del posted, step, pending, training
    gc.collect()
    await asyncio.sleep(0)
    assert "never retrieved" not in caplog.text
    await session.detach_async()


def test_failed_sync_still_retires_earlier_snapshot_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    """The version moves when the server accepts the sync, so no snapshot client outlives weights that began to change."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))
    training = _training_client(session)
    earlier = training.save_weights_and_get_sampling_client()

    async def failed_wait(**_: Any) -> Any:
        raise RuntimeError("sync failed")

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", failed_wait)
    with pytest.raises(RuntimeError, match="sync failed"):
        training.save_weights_and_get_sampling_client()

    with pytest.raises(RuntimeError, match="stale"):
        earlier._check_fresh()
    _close(session)


_FORWARD_BACKWARD_OUTPUT = {"loss": 0.5, "metrics": {}}


@pytest.mark.parametrize(
    "call,operation,output,expected",
    [
        pytest.param(
            lambda training: training.forward([_rl_loop_datum()], "importance_sampling"),
            "forward_backward",
            _FORWARD_BACKWARD_OUTPUT,
            types.ForwardBackwardOutput,
            id="forward",
        ),
        pytest.param(
            lambda training: training.forward_backward([_rl_loop_datum()], loss_fn="importance_sampling"),
            "forward_backward",
            _FORWARD_BACKWARD_OUTPUT,
            types.ForwardBackwardOutput,
            id="forward_backward",
        ),
        pytest.param(
            lambda training: training.optim_step(_ADAM), "optim_step", None, types.OptimStepResponse, id="optim_step"
        ),
        pytest.param(
            lambda training: training.save_state("ckpt"),
            "create_training_checkpoint",
            _CHECKPOINT_OUTPUT,
            types.SaveWeightsResponse,
            id="save_state",
        ),
        pytest.param(
            lambda training: training.save_weights_for_sampler("final"),
            "create_inference_checkpoint",
            _CHECKPOINT_OUTPUT,
            types.SaveWeightsForSamplerResponse,
            id="save_weights_for_sampler",
        ),
    ],
)
async def test_plain_calls_return_an_awaitable_inside_a_loop(
    monkeypatch: pytest.MonkeyPatch,
    call: Callable[[tinker_compat.TrainingClient], Any],
    operation: str,
    output: Any,
    expected: type,
) -> None:
    """tinker 0.39 deprecates the *_async methods: async code calls the plain method and awaits its future."""
    patch_wait(monkeypatch, output)
    posted = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(**{operation: posted})

    result = await call(_training_client(session))

    assert isinstance(result, expected)
    if output is _CHECKPOINT_OUTPUT:
        assert result.path == _CHECKPOINT_UUID
    posted.assert_awaited_once()
    await session.detach_async()


async def test_steps_called_before_any_await_reach_the_server_in_call_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """tinker-cookbook calls optim_step before awaiting the forward_backward ahead of it."""
    patch_wait(monkeypatch, _FORWARD_BACKWARD_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(
        forward_backward=_recording(order, "forward_backward", delay=0.1),
        optim_step=_recording(order, "optim_step"),
    )
    training = _training_client(session)

    fwd_bwd = training.forward_backward([_rl_loop_datum()], loss_fn="importance_sampling")
    step = training.optim_step(_ADAM)
    await fwd_bwd
    await step

    assert order == ["forward_backward", "optim_step"]
    await session.detach_async()


async def test_publish_waits_for_a_step_called_before_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Weights must not be published before the optimizer step called ahead of the publish."""
    patch_wait(monkeypatch, _WEIGHTS_SYNC_OUTPUT)
    order: list[str] = []
    session = _session_with_operations(
        optim_step=_recording(order, "optim_step", delay=0.1),
        weights_sync=_recording(order, "weights_sync"),
    )
    training = _training_client(session)

    step = training.optim_step(_ADAM)
    sampling = await cast(Any, training.save_weights_and_get_sampling_client())
    await step

    assert order == ["optim_step", "weights_sync"]
    assert isinstance(sampling, tinker_compat.SamplingClient)
    await session.detach_async()


async def test_pending_future_refuses_to_block_inside_the_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))
    step = _training_client(session).optim_step(_ADAM)

    with pytest.raises(RuntimeError, match="await this future"):
        step.result()
    assert await step == types.OptimStepResponse()
    await session.detach_async()


async def test_pending_future_converts_like_an_api_future(monkeypatch: pytest.MonkeyPatch) -> None:
    """coroutine() and future() work on what a plain call returns inside a loop, as on tinker's APIFuture."""
    patch_wait(monkeypatch, _CHECKPOINT_OUTPUT)
    session = _session_with_operations(create_training_checkpoint=AsyncMock(return_value=_OPERATION))
    training = _training_client(session)

    from_task = await asyncio.create_task(training.save_state("a").coroutine())
    from_future = await asyncio.wrap_future(training.save_state("b").future())

    assert from_task.path == from_future.path == _CHECKPOINT_UUID
    await session.detach_async()


async def test_cancelled_wait_keeps_the_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """The request went out when the call returned; giving up on its result must not withdraw it."""
    patch_wait(monkeypatch)
    order: list[str] = []
    session = _session_with_operations(optim_step=_recording(order, "optim_step", delay=0.1))
    step = _training_client(session).optim_step(_ADAM)

    with pytest.raises(TimeoutError):
        await step.result_async(timeout=0.01)
    assert await step == types.OptimStepResponse()
    assert order == ["optim_step"]
    await session.detach_async()


def _patch_scoring_then_done(monkeypatch: pytest.MonkeyPatch, *, later_ops_fail: bool = False) -> None:
    """The first polled operation is the scoring pass; every later one completes with no output,
    or, with ``later_ops_fail``, is failed by the server."""
    scored = iter([_scored_output([-1.0, -2.0])])

    async def fake(*, operation: Any, **_: Any) -> Any:
        operation_id = getattr(operation, "id", "op")
        output = next(scored, None)
        if output is None and later_ops_fail:
            raise rl_ops.OperationFailedError(f"Operation ({operation_id}) failed: gradients rejected")
        return SimpleNamespace(
            id=operation_id,
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output={"ok": True} if output is None else output,
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake)


def _unweighted_datum() -> types.Datum:
    return types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={"target_tokens": types.TensorData([1, 2], dtype="int64")},
    )


async def _custom_loss_then_step(
    training: tinker_compat.TrainingClient, loss_fn: Any, style: str
) -> types.ForwardBackwardOutput:
    """Call forward_backward_custom and then optim_step before collecting either, in ``style``."""
    if style == "plain":
        fwd_bwd, step = training.forward_backward_custom([_unweighted_datum()], loss_fn), training.optim_step(_ADAM)
        output = await fwd_bwd
        await step
        return output
    if style == "gather":
        fwd_bwd_future, step_future = await asyncio.gather(
            training.forward_backward_custom_async([_unweighted_datum()], loss_fn),
            training.optim_step_async(_ADAM),
        )
    else:
        fwd_bwd_task = asyncio.ensure_future(training.forward_backward_custom_async([_unweighted_datum()], loss_fn))
        await asyncio.sleep(0)
        step_future = training.optim_step(_ADAM)
        fwd_bwd_future = await fwd_bwd_task
    output = await fwd_bwd_future
    await step_future
    return output


@pytest.mark.parametrize("style", ["plain", "gather", "task"])
async def test_a_step_called_during_forward_backward_custom_reaches_the_server_after_its_gradients(
    monkeypatch: pytest.MonkeyPatch, style: str
) -> None:
    """An optim_step must not run before the custom gradients, whichever call style queued it."""
    pytest.importorskip("torch")
    import torch

    _patch_scoring_then_done(monkeypatch)
    order: list[str] = []
    session = _session_with_operations(
        forward_backward=_recording(order, "forward_backward", delay=0.05),
        custom_forward_backward=_recording(order, "custom_forward_backward"),
        optim_step=_recording(order, "optim_step"),
    )
    loss_threads: list[int] = []

    def loss_fn(_data: Any, logprobs_list: list[torch.Tensor]) -> tuple[torch.Tensor, dict[str, float]]:
        loss_threads.append(threading.get_ident())
        return sum(lp.sum() for lp in logprobs_list), {"custom_metric": 1.5}

    output = await _custom_loss_then_step(_training_client(session), loss_fn, style)

    assert order == ["forward_backward", "custom_forward_backward", "optim_step"]
    assert output.metrics["custom_metric"] == 1.5
    assert loss_threads and loss_threads[0] != threading.get_ident()  # as in tinker 0.39, off the caller's loop
    await session.detach_async()


@pytest.mark.parametrize(
    "fails_on,error,match,sent",
    [
        ("client", ValueError, "bad batch", ["forward_backward"]),
        (
            "server",
            rl_ops.OperationFailedError,
            "gradients rejected",
            ["forward_backward", "custom_forward_backward"],
        ),
    ],
    ids=["client_loss", "server"],
)
async def test_failed_custom_loss_rejects_the_steps_queued_behind_it(
    monkeypatch: pytest.MonkeyPatch, fails_on: str, error: type[Exception], match: str, sent: list[str]
) -> None:
    """No optimizer step runs after a custom loss whose gradients were not accumulated, whether the
    client loss raised (as in tinker) or the server failed the gradients (stricter than tinker)."""
    pytest.importorskip("torch")
    import torch

    _patch_scoring_then_done(monkeypatch, later_ops_fail=fails_on == "server")
    order: list[str] = []
    session = _session_with_operations(
        forward_backward=_recording(order, "forward_backward"),
        custom_forward_backward=_recording(order, "custom_forward_backward"),
        optim_step=_recording(order, "optim_step"),
    )

    def loss_fn(_data: Any, logprobs_list: list[torch.Tensor]) -> tuple[torch.Tensor, dict[str, float]]:
        if fails_on == "client":
            raise ValueError("bad batch")
        return sum(lp.sum() for lp in logprobs_list), {}

    training = _training_client(session)
    fwd_bwd = training.forward_backward_custom([_unweighted_datum()], loss_fn)
    step = training.optim_step(_ADAM)

    with pytest.raises(error, match=match):
        await fwd_bwd
    with pytest.raises(RuntimeError, match="rejects every later training request") as rejected:
        await step
    assert isinstance(rejected.value.__cause__, error)
    with pytest.raises(RuntimeError, match="rejects every later training request"):
        await training.optim_step(_ADAM)
    assert order == sent
    await session.detach_async()


@pytest.mark.parametrize(
    "empty,without_torch,error,match",
    [(True, False, ValueError, "No data provided"), (False, True, ImportError, "PyTorch is not installed")],
    ids=["empty_batch", "no_torch"],
)
def test_forward_backward_custom_rejects_before_any_request(
    monkeypatch: pytest.MonkeyPatch, empty: bool, without_torch: bool, error: type[Exception], match: str
) -> None:
    """These fail on the caller's frame, as in tinker: no paid scoring pass, and the client stays usable."""
    if without_torch:
        monkeypatch.setitem(sys.modules, "torch", None)
    forward_backward = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(forward_backward=forward_backward)
    training = _training_client(session)

    with pytest.raises(error, match=match):
        training.forward_backward_custom([] if empty else [_unweighted_datum()], lambda *_: (0.0, {}))
    forward_backward.assert_not_awaited()

    training.forward_backward([_rl_loop_datum()], "importance_sampling")
    forward_backward.assert_awaited_once()
    _close(session)


@pytest.mark.parametrize(
    "kwargs,expected", [({}, True), ({"return_loss_fn_outputs": False}, False)], ids=["default", "skipped"]
)
def test_forward_backward_asks_for_per_datum_outputs_unless_told_not_to(kwargs: dict[str, Any], expected: bool) -> None:
    """tinker returns per-datum logprobs from every forward_backward; callers may opt out."""
    forward_backward = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(forward_backward=forward_backward)

    _training_client(session).forward_backward([_rl_loop_datum()], "importance_sampling", **kwargs)

    assert forward_backward.call_args.kwargs["return_loss_fn_outputs"] is expected
    _close(session)
