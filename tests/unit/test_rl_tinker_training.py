from __future__ import annotations

import asyncio
import warnings
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import ANY, AsyncMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from tests.unit.rl_wait import patch_wait
from together.lib.beta.rl import WeightSyncType, tinker as tinker_compat, _operations as rl_ops
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
from together.lib.beta.rl.tinker import _training


def _scored_output(*logprobs: list[float]) -> dict[str, Any]:
    """A forward_only operation output, whose per-sample tensors carry the logprobs."""
    return {
        "loss": 0.5,
        "loss_fn_outputs": [{"tensors": {"logprobs": {"data": values, "dtype": "float32"}}} for values in logprobs],
    }


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


_CHECKPOINT_UUID = "123e4567-e89b-12d3-a456-426614174000"
_REGISTERED_MODEL = "user/Qwen3.5-4B-adapter-rl-step-42-20260827-123e4567"


def test_save_state_returns_bare_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, {"checkpoint_id": _CHECKPOINT_UUID})
    create = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(create_training_checkpoint=create)

    saved = _training_client(session).save_state("checkpoint-001").result()

    create.assert_awaited_once_with("sess", idempotency_key=ANY)
    assert timeouts == [None]
    assert saved.path == _CHECKPOINT_UUID
    assert "://" not in saved.path
    assert "?" not in saved.path


def test_save_state_warns_on_ttl_and_overwrite(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, {"checkpoint_id": _CHECKPOINT_UUID})
    session = _session_with_operations(create_training_checkpoint=AsyncMock(return_value=_OPERATION))
    client = _training_client(session)

    with pytest.warns(UserWarning, match="ttl_seconds"):
        client.save_state("checkpoint-001", ttl_seconds=60).result()
    with pytest.warns(UserWarning, match="overwrite"):
        client.save_state("checkpoint-001", overwrite=True).result()


def test_save_weights_for_sampler_returns_registered_model_name(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, {"model_name": _REGISTERED_MODEL})
    create = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(create_inference_checkpoint=create)

    saved = _training_client(session).save_weights_for_sampler("final").result()

    create.assert_awaited_once_with("sess", idempotency_key=ANY)
    assert timeouts == [None]
    assert saved.path == _REGISTERED_MODEL


def test_save_weights_for_sampler_warns_on_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, {"model_name": _REGISTERED_MODEL})
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
    assert request["return_loss_fn_outputs"] is _training.omit
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
    """forward is the one path that asks for per-datum logprobs; they must land in
    loss_fn_outputs rather than staying empty like forward_backward's."""
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


def test_forward_backward_custom_rejects_logprob_count_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    # Two samples, but the scoring pass returns only one logprob array.
    patch_wait(monkeypatch, _scored_output([-1.0]))
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={"target_tokens": types.TensorData([1, 2], dtype="int64")},
    )

    def loss_fn(_data: Any, logprobs_list: list[Any]) -> tuple[Any, dict[str, float]]:
        return sum(logprobs_list), {}

    with pytest.raises(RuntimeError, match="1 logprob arrays for 2 samples"):
        _training_client(session).forward_backward_custom([datum, datum], loss_fn)
    _close(session)


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
