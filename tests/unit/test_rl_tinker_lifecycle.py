from __future__ import annotations

import signal
import asyncio
import warnings
import threading
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from together.lib.beta import rl
from together.lib.beta.rl import (
    Sample,
    LossConfig,
    tinker as tinker_compat,
    _request_types,
)
from tests.unit._rl_tinker import (
    _noop,
    _ignore,
    _session_mock,
    _model_resources_mock,
)
from together.lib.beta.rl.tinker import _service, _teardown
from together.lib.beta.rl.clients.session import SessionClient


def test_module_reexports_types_without_genuine_clients() -> None:
    """Types come from tinker.types; Together clients must not leak real tinker ones."""
    assert tinker_compat.types is types
    assert tinker_compat.Datum is types.Datum
    assert tinker_compat.ModelInput is types.ModelInput
    assert tinker_compat.APIFuture is not __import__("tinker").APIFuture
    assert not hasattr(tinker_compat, "RestClient")
    assert not hasattr(tinker_compat, "resources")
    with pytest.raises(AttributeError, match="RestClient"):
        _ = tinker_compat.RestClient


def test_request_types_are_reexported() -> None:
    """The package re-export must resolve to the handwritten request types, not to a
    regenerated types.beta.rl symbol of the same name."""
    assert Sample is _request_types.Sample
    assert LossConfig is _request_types.LossConfig
    assert {"Sample", "LossConfig"} <= set(rl.__all__)


def test_create_lora_training_client_warns_on_reproducibility_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def refuse(**_: object) -> None:
        raise RuntimeError("no network in unit tests")

    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", refuse)
    # keep the real process-wide SIGTERM handler out of the test suite
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.warns(UserWarning, match="train_mlp"), pytest.raises(RuntimeError):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", train_mlp=False)


def test_create_lora_training_client_forwards_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.side_effect = RuntimeError("stop")
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(RuntimeError, match="stop"):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", rank=16, seed=7)

    resources.create_session_async.assert_awaited_once_with(lora_config={"rank": 16, "seed": 7})
    resources.stop_async.assert_awaited_once_with()


def test_create_lora_training_client_forwards_train_unembed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.side_effect = RuntimeError("stop")
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(RuntimeError, match="stop"):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", rank=16, train_unembed=False)

    resources.create_session_async.assert_awaited_once_with(lora_config={"rank": 16, "train_unembed": False})
    resources.stop_async.assert_awaited_once_with()


async def test_create_lora_training_client_async_returns_training_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _session_mock()
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    training = await tinker_compat.ServiceClient().create_lora_training_client_async(
        "Qwen/Qwen3.5-4B",
        rank=16,
        seed=7,
    )

    assert isinstance(training, tinker_compat.TrainingClient)
    resources.create_session_async.assert_awaited_once_with(lora_config={"rank": 16, "seed": 7})


def test_create_lora_training_client_rejects_unknown_kwargs() -> None:
    """A misspelled rank must fail instead of silently provisioning rank 32."""
    with pytest.raises(TypeError, match="rnak"):
        tinker_compat.ServiceClient().create_lora_training_client("model", rnak=8)  # type: ignore[call-arg]


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"http_client": object()}, "http_client"),
        ({"max_retries": 3}, "max_retries"),
        ({"timeout": 30.0}, "timeout"),
        (
            {"default_headers": {"X-Foo": "bar"}, "timeout": 30.0, "max_retries": 3},
            r"ignores these options: max_retries, timeout",
        ),
    ],
)
def test_service_client_warns_on_ops_kwargs(kwargs: dict[str, Any], match: str) -> None:
    with pytest.warns(UserWarning, match=match):
        tinker_compat.ServiceClient(**kwargs)


def test_service_client_stays_silent_on_header_query_kwargs() -> None:
    """Headers/query stay quiet; they are paste boilerplate, not tuned ops knobs."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        tinker_compat.ServiceClient(default_headers={"X-Foo": "bar"}, default_query={"q": "1"})
    assert caught == []


def test_service_client_rejects_unknown_kwargs() -> None:
    with pytest.raises(TypeError, match="not_a_real_kwarg"):
        tinker_compat.ServiceClient(not_a_real_kwarg=1)


def test_attached_resources_are_detached_but_not_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Closing a borrowed resource must stop our session without deallocating another owner's GPUs."""
    session = _session_mock()
    resources = _model_resources_mock("mr-1")
    resources.retrieve_async.return_value = SimpleNamespace(base_model="model", lora_enabled=True)
    resources.create_session_async.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "attach_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    training = tinker_compat.ServiceClient(model_resources_id="mr-1").create_lora_training_client("model")
    training.close()
    training.close()

    session.stop.assert_called_once_with()
    resources.detach.assert_called_once_with()
    resources.stop.assert_not_called()


def test_created_resources_close_with_context_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    """The additive context manager must promptly release sessions and resources in notebooks."""
    session = _session_mock()
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    with tinker_compat.ServiceClient().create_lora_training_client("model") as training:
        assert isinstance(training, tinker_compat.TrainingClient)

    session.stop.assert_called_once_with()
    resources.stop.assert_called_once_with()
    resources.detach.assert_not_called()


def _provision_attached(service: tinker_compat.ServiceClient, entry: str) -> None:
    if entry == "sync":
        service.create_lora_training_client("model")
    else:
        asyncio.run(service.create_lora_training_client_async("model"))


@pytest.mark.parametrize("entry", ["sync", "async"])
def test_attach_rejects_wrong_base_model(monkeypatch: pytest.MonkeyPatch, entry: str) -> None:
    """Attaching must not silently train a different base model than the caller requested,
    and both entry points must release the borrowed handle on the way out."""
    resources = _model_resources_mock("mr-1")
    resources.retrieve_async.return_value = SimpleNamespace(base_model="other", lora_enabled=True)
    monkeypatch.setattr(_service.ModelResourcesClient, "attach_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(ValueError, match="other"):
        _provision_attached(tinker_compat.ServiceClient(model_resources_id="mr-1"), entry)

    resources.detach_async.assert_awaited_once_with()
    resources.create_session_async.assert_not_called()


@pytest.mark.parametrize("entry", ["sync", "async"])
def test_attach_rejects_resources_without_lora(monkeypatch: pytest.MonkeyPatch, entry: str) -> None:
    """A LoRA client must fail before session creation when borrowed resources are full-weight."""
    resources = _model_resources_mock("mr-1")
    resources.retrieve_async.return_value = SimpleNamespace(base_model="model", lora_enabled=False)
    monkeypatch.setattr(_service.ModelResourcesClient, "attach_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(ValueError, match="do not support LoRA"):
        _provision_attached(tinker_compat.ServiceClient(model_resources_id="mr-1"), entry)

    resources.detach_async.assert_awaited_once_with()
    resources.create_session_async.assert_not_called()


def test_stop_on_exit_and_sigterm_translation(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The exit hook (threading._register_atexit, so it runs before concurrent.futures
    teardown) must release the GPUs even when session.stop fails, and must not raise:
    threading._shutdown runs callbacks in a plain loop, so an escaping exception aborts
    every teardown after it. SIGTERM's default disposition skips those hooks entirely,
    so it is translated into SystemExit — chaining any handler the host installed."""
    hooks: list[Any] = []
    monkeypatch.setattr(_teardown.threading, "_register_atexit", hooks.append)
    session = _session_mock()
    # KeyboardInterrupt: even a Ctrl-C during a hung session.stop() must not skip
    # the GPU teardown, so the hook has to catch BaseException, not just Exception.
    session.stop.side_effect = KeyboardInterrupt()
    model_resources = _model_resources_mock("mr-123")
    model_resources.stop.side_effect = RuntimeError("teardown failed")

    lifecycle = _teardown._Lifecycle(
        cast(Any, session),
        cast(Any, model_resources),
        owns_model_resources=True,
    )
    _teardown._stop_on_exit(lifecycle)

    (hook,) = hooks
    hook()
    model_resources.stop.assert_called_once_with()
    assert "mr-123" in caplog.text
    assert lifecycle.closed is False

    monkeypatch.setattr(_teardown, "_sigterm_translated", False)
    chained: list[int] = []

    def previous_handler(signum: int, _frame: Any) -> None:
        chained.append(signum)

    def get_signal(_sig: int) -> Callable[[int, Any], None]:
        return previous_handler

    monkeypatch.setattr(_teardown.signal, "getsignal", get_signal)
    installed: dict[int, Any] = {}

    def install_signal(sig: int, handler: Any) -> Any:
        return installed.setdefault(sig, handler)

    monkeypatch.setattr(_teardown.signal, "signal", install_signal)

    _teardown._exit_on_sigterm()

    handler = installed[signal.SIGTERM]
    with pytest.raises(SystemExit) as excinfo:
        handler(signal.SIGTERM, None)
    assert excinfo.value.code == 128 + signal.SIGTERM
    assert chained == [signal.SIGTERM]


def test_failed_explicit_close_can_be_retried() -> None:
    """A failed close() must not mark the lifecycle closed, or GPUs become unreachable."""
    session = _session_mock()
    session.stop.side_effect = RuntimeError("busy")
    model_resources = _model_resources_mock("mr-1")
    lifecycle = _teardown._Lifecycle(
        cast(Any, session),
        cast(Any, model_resources),
        owns_model_resources=True,
    )

    with pytest.raises(RuntimeError, match="busy"):
        lifecycle.close()

    assert lifecycle.closed is False
    model_resources.stop.assert_called_once_with()

    session.stop.side_effect = None
    lifecycle.close()

    assert lifecycle.closed is True
    # The succeeded handle was dropped and only the failed one retried.
    assert session.stop.call_count == 2
    assert model_resources.stop.call_count == 1


async def test_async_close_tears_down_inside_a_running_loop() -> None:
    """An async training script must close asynchronously instead of blocking its loop."""
    session = _session_mock()
    model_resources = _model_resources_mock("mr-1")
    lifecycle = _teardown._Lifecycle(
        cast(Any, session),
        cast(Any, model_resources),
        owns_model_resources=True,
    )
    training = tinker_compat.TrainingClient(cast(Any, session), lifecycle)

    with pytest.raises(RuntimeError, match="close_async"):
        training.close()
    assert lifecycle.closed is False

    async with training:
        pass

    session.stop_async.assert_awaited_once_with()
    model_resources.stop_async.assert_awaited_once_with()
    assert lifecycle.closed is True


def test_async_close_releases_a_session_built_on_the_blocking_path() -> None:
    """aclose has to reach the session's own gate, not just drop the handles it holds.
    Mocked handles cannot show this — only a real session owns a gate."""
    client = SimpleNamespace(
        beta=SimpleNamespace(
            rl=SimpleNamespace(
                sessions=SimpleNamespace(
                    stop=AsyncMock(return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPED"))
                )
            )
        ),
        close=AsyncMock(),
    )
    session = SessionClient("sess", _client=cast(Any, client))
    session.run(asyncio.sleep(0))
    lifecycle = _teardown._Lifecycle(session)

    asyncio.run(lifecycle.aclose())

    assert lifecycle.closed is True
    with pytest.raises(RuntimeError, match="stopped or stopping"):
        session.run(asyncio.sleep(0))


def test_provisioning_registers_the_exit_time_resource_release(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without these two registrations a crashed script leaves the GPUs allocated.
    The rest of the suite stubs both out, so nothing else notices if they vanish."""
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.return_value = _session_mock()
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))

    registered: list[_teardown._Lifecycle] = []
    sigterm_threads: list[threading.Thread] = []

    def record_sigterm() -> None:
        sigterm_threads.append(threading.current_thread())

    monkeypatch.setattr(_service, "_stop_on_exit", registered.append)
    monkeypatch.setattr(_service, "_exit_on_sigterm", record_sigterm)

    training = tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B")

    assert registered == [training._lifecycle]
    # SIGTERM's default disposition skips the exit hooks entirely, and a handler can only be
    # installed from the calling thread — never from the process loop that provisions.
    assert sigterm_threads == [threading.current_thread()]


def test_exit_hook_releases_an_await_built_client() -> None:
    """Every handle shares the process loop, so how a session was built no longer decides
    whether the blocking exit hook can release it."""
    client = SimpleNamespace(
        beta=SimpleNamespace(
            rl=SimpleNamespace(
                sessions=SimpleNamespace(
                    stop=AsyncMock(return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPED"))
                )
            )
        ),
        close=AsyncMock(),
    )

    async def build() -> SessionClient:
        return SessionClient("sess", _client=cast(Any, client))

    session = asyncio.run(build())
    lifecycle = _teardown._Lifecycle(session)

    lifecycle.close(automatic=True)

    assert lifecycle.closed is True
    client.beta.rl.sessions.stop.assert_awaited()


_CHECKPOINT_UUID = "123e4567-e89b-12d3-a456-426614174000"


def test_create_rest_client_raises_tinker_error() -> None:
    with pytest.raises(__import__("tinker").TinkerError, match="RestClient"):
        tinker_compat.ServiceClient().create_rest_client()


def _training_checkpoint(*, lora_rank: int | None = 16, kind: str = "CHECKPOINT_TYPE_TRAINING") -> SimpleNamespace:
    return SimpleNamespace(
        id=_CHECKPOINT_UUID,
        base_model="Qwen/Qwen3.5-4B",
        lora_rank=lora_rank,
        type=kind,
    )


@pytest.mark.parametrize("lora_rank", [16, None])
@pytest.mark.parametrize(
    ("method", "load_optimizer"),
    [
        ("create_training_client_from_state", False),
        ("create_training_client_from_state_with_optimizer", True),
    ],
)
def test_create_training_client_from_state_describes_then_starts(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    load_optimizer: bool,
    lora_rank: int | None,
) -> None:
    monkeypatch.setattr(
        _service, "_describe_training_checkpoint", lambda *_, **__: _training_checkpoint(lora_rank=lora_rank)
    )
    session = _session_mock()
    resources = _model_resources_mock("mr-1")
    resources.create_session_async.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "create_async", AsyncMock(return_value=resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    training = getattr(tinker_compat.ServiceClient(), method)(_CHECKPOINT_UUID)

    assert isinstance(training, tinker_compat.TrainingClient)
    resources.create_session_async.assert_awaited_once_with(
        lora_config={"rank": lora_rank},
        resume_from_checkpoint_id=_CHECKPOINT_UUID,
        load_optimizer=load_optimizer,
    )
    resources.stop.assert_not_called()


def test_describe_rejects_inference_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MagicMock()
    client.beta.rl.checkpoints.retrieve.return_value = _training_checkpoint(kind="CHECKPOINT_TYPE_INFERENCE")
    client.__enter__.return_value = client
    monkeypatch.setattr(_service, "Together", lambda **_: client)

    with pytest.raises(ValueError, match="CHECKPOINT_TYPE_INFERENCE"):
        _service._describe_training_checkpoint(_CHECKPOINT_UUID, api_key=None, base_url=None)
    client.__exit__.assert_called_once()


def test_resume_rejects_weights_access_token() -> None:
    with pytest.raises(NotImplementedError, match="weights_access_token"):
        tinker_compat.ServiceClient().create_training_client_from_state(_CHECKPOINT_UUID, weights_access_token="tok")
