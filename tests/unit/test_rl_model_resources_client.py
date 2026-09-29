from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from together._types import omit
from together.lib.beta.rl import MuonConfig, ComputeConfig, WandbMetadata, OptimizerConfig, SessionMetadata
from together.lib.beta.rl.clients import model_resources as model_resources_client_module
from together.lib.beta.rl.clients.session import SessionClient
from together.lib.beta.rl.clients.model_resources import ModelResourcesClient

_STOPPING = SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_STOPPING")


def _fake_client(status: str = "MODEL_RESOURCES_STATUS_READY") -> MagicMock:
    client = MagicMock()
    client.beta.rl.model_resources.create = AsyncMock(return_value=SimpleNamespace(id="res-1"))
    client.beta.rl.model_resources.retrieve = AsyncMock(return_value=SimpleNamespace(status=status))
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    return client


def _patch_together(monkeypatch: pytest.MonkeyPatch, client: MagicMock) -> None:
    def fake_together(**_kw: Any) -> MagicMock:
        return client

    monkeypatch.setattr(model_resources_client_module, "AsyncTogether", fake_together)


async def test_create_async_returns_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    resources = await ModelResourcesClient.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    assert resources.model_resources_id == "res-1"
    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["base_model"] == "Qwen/Qwen3-0.6B"
    assert create_kwargs["lora_enabled"] is True
    client.beta.rl.model_resources.retrieve.assert_awaited_with("res-1")


@pytest.mark.parametrize("num_generator_replicas", [0, 1, 2])
async def test_create_async_passes_compute_config(
    monkeypatch: pytest.MonkeyPatch,
    num_generator_replicas: int,
) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResourcesClient.create_async(
        base_model="Qwen/Qwen3-0.6B",
        compute_config=ComputeConfig(num_generator_replicas=num_generator_replicas),
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["compute_config"] == {"num_generator_replicas": num_generator_replicas}


async def test_create_async_omits_compute_config_so_the_server_decides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResourcesClient.create_async(
        base_model="Qwen/Qwen3-0.6B",
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["compute_config"] is omit


async def test_create_async_forwards_optimizer_config(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    optimizer_config = OptimizerConfig(muon=MuonConfig(scaling_strategy="MUON_SCALING_STRATEGY_MATCH_ADAM"))
    await ModelResourcesClient.create_async(
        base_model="Qwen/Qwen3-0.6B",
        optimizer_config=optimizer_config,
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["optimizer_config"] == {"muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_MATCH_ADAM"}}


async def test_create_async_omits_optimizer_config_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResourcesClient.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["optimizer_config"] is model_resources_client_module.omit


def test_create_forwards_base_weights_ref(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    ModelResourcesClient.create(
        base_model="Qwen/Qwen3.5-9B",
        base_weights_ref="together://ml_abc@rv_def",
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["base_weights_ref"] == "together://ml_abc@rv_def"


async def test_create_async_omits_base_weights_ref_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResourcesClient.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["base_weights_ref"] is omit


async def test_create_async_stops_and_closes_on_terminal_status(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client(status="MODEL_RESOURCES_STATUS_ERROR")
    _patch_together(monkeypatch, client)

    with pytest.raises(RuntimeError, match="MODEL_RESOURCES_STATUS_ERROR"):
        await ModelResourcesClient.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


async def test_create_async_times_out_and_cleans_up(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client(status="MODEL_RESOURCES_STATUS_CREATING")
    _patch_together(monkeypatch, client)

    with pytest.raises(TimeoutError):
        await ModelResourcesClient.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.0, interval=0.0)

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


async def test_stop_async_closes_client() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.beta.rl.model_resources.retrieve = AsyncMock()
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    result = await resources.stop_async()

    assert result is _STOPPING
    assert resources._loop.closed
    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1", force=omit)
    client.beta.rl.model_resources.retrieve.assert_not_awaited()
    client.close.assert_awaited_once()


async def test_stop_async_waits_until_resources_stop_billing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(model_resources_client_module, "DEFAULT_MODEL_RESOURCES_STOP_INTERVAL", 0.0)
    client = MagicMock()
    output = SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_READY")
    client.beta.rl.model_resources.stop = AsyncMock(return_value=output)
    client.beta.rl.model_resources.retrieve = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    result = await resources.stop_async()

    assert result is output
    client.beta.rl.model_resources.retrieve.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


def test_retrieve_returns_resource() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_READY")
    )
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    result = resources.retrieve()

    assert result.id == "res-1"
    resources.stop()


async def test_retrieve_async_returns_resource() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_READY")
    )
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    result = await resources.retrieve_async()

    assert result.id == "res-1"
    client.beta.rl.model_resources.retrieve.assert_awaited_once_with("res-1")


async def test_create_session_async_uses_model_resources_id(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    captured: dict[str, Any] = {}

    async def fake_create_async(**kwargs: Any) -> object:
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(SessionClient, "create_async", fake_create_async)

    client = MagicMock()
    client.api_key = "key-1"
    client.base_url = "http://host"
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))
    metadata = SessionMetadata(wandb=WandbMetadata(project="project-1", run_id="run-1"))

    result = await resources.create_session_async(
        display_name="session-1",
        metadata=metadata,
        resume_from_checkpoint_id="ckpt-1",
        lora_config=None,
    )

    assert result is sentinel
    assert captured["model_resources_id"] == "res-1"
    assert captured["api_key"] == "key-1"
    assert captured["base_url"] == "http://host"
    assert captured["display_name"] == "session-1"
    assert captured["metadata"] is metadata
    assert captured["resume_from_checkpoint_id"] == "ckpt-1"


def test_create_session_forwards_session_details(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    captured: dict[str, Any] = {}

    def fake_create(**kwargs: Any) -> object:
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(SessionClient, "create", fake_create)

    client = MagicMock()
    client.api_key = "key-1"
    client.base_url = "http://host"
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))
    metadata = SessionMetadata(wandb=WandbMetadata(project="project-1"))

    result = resources.create_session(display_name="session-1", metadata=metadata)

    assert result is sentinel
    assert captured["display_name"] == "session-1"
    assert captured["metadata"] is metadata


async def test_attach_async_binds_existing_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    resources = await ModelResourcesClient.attach_async(model_resources_id="res-1")

    assert resources.model_resources_id == "res-1"
    client.beta.rl.model_resources.retrieve.assert_awaited_once_with("res-1")
    client.beta.rl.model_resources.create.assert_not_awaited()
    client.close.assert_not_awaited()


async def test_attach_async_raises_and_closes_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    client.beta.rl.model_resources.retrieve = AsyncMock(side_effect=RuntimeError("not found"))
    _patch_together(monkeypatch, client)

    with pytest.raises(RuntimeError, match="not found"):
        await ModelResourcesClient.attach_async(model_resources_id="missing")

    client.close.assert_awaited_once()


async def test_detach_async_closes_client_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock()
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    await resources.detach_async()

    client.close.assert_awaited_once()
    client.beta.rl.model_resources.stop.assert_not_awaited()


def test_detach_marks_the_handle_closed_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock()
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))
    resources.detach()

    assert resources._loop.closed
    client.close.assert_awaited_once()
    client.beta.rl.model_resources.stop.assert_not_awaited()


def test_context_manager_stops() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    with resources:
        assert resources.model_resources_id == "res-1"

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1", force=omit)
    client.close.assert_awaited_once()


async def test_async_context_manager_stops() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    async with resources:
        assert resources.model_resources_id == "res-1"

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1", force=omit)
    client.close.assert_awaited_once()


async def test_stop_forwards_force_to_the_api() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value=_STOPPING)
    client.close = AsyncMock()
    resources = ModelResourcesClient("res-1", _client=cast(Any, client))

    await resources.stop_async(force=True)

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1", force=True)


def test_model_resources_client_is_publicly_exported() -> None:
    from together.lib.beta.rl import ModelResourcesClient as FromRl, ModelResourcesStatus

    assert FromRl is ModelResourcesClient
    assert ModelResourcesStatus is not None


def test_rl_public_api_hides_generated_param_suffixes() -> None:
    import together.lib.beta.rl as rl

    assert not [name for name in rl.__all__ if name.endswith("Param")]
