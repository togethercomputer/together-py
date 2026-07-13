from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from together.lib.beta.rl import model_resources as mr_module
from together.lib.beta.rl.trainer import Trainer
from together.lib.beta.rl.model_resources import ModelResources


def _fake_client(status: str = "MODEL_RESOURCES_STATUS_READY") -> MagicMock:
    client = MagicMock()
    client.beta.rl.model_resources.create = AsyncMock(return_value=SimpleNamespace(id="res-1"))
    client.beta.rl.model_resources.retrieve = AsyncMock(return_value=SimpleNamespace(status=status))
    client.beta.rl.model_resources.stop = AsyncMock(return_value={"id": "res-1"})
    client.close = AsyncMock()
    return client


def _patch_together(monkeypatch: pytest.MonkeyPatch, client: MagicMock) -> None:
    def fake_together(**_kw: Any) -> MagicMock:
        return client

    monkeypatch.setattr(mr_module, "AsyncTogether", fake_together)


async def test_create_async_returns_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    resources = await ModelResources.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    assert resources.model_resources_id == "res-1"
    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["base_model"] == "Qwen/Qwen3-0.6B"
    assert create_kwargs["lora_enabled"] is True
    client.beta.rl.model_resources.retrieve.assert_awaited_with("res-1")


@pytest.mark.parametrize("num_generator_replicas", [0, 1, 2])
async def test_create_async_passes_num_generator_replicas(
    monkeypatch: pytest.MonkeyPatch,
    num_generator_replicas: int,
) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResources.create_async(
        base_model="Qwen/Qwen3-0.6B",
        num_generator_replicas=num_generator_replicas,
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["compute_config"] == {"num_generator_replicas": num_generator_replicas}


async def test_create_async_forwards_optimizer_config(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    optimizer_config = {"muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_MATCH_ADAMW"}}
    await ModelResources.create_async(
        base_model="Qwen/Qwen3-0.6B",
        optimizer_config=cast(Any, optimizer_config),
        timeout=0.1,
        interval=0.0,
    )

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["optimizer_config"] == optimizer_config


async def test_create_async_omits_optimizer_config_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    await ModelResources.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    create_kwargs = client.beta.rl.model_resources.create.await_args.kwargs
    assert create_kwargs["optimizer_config"] is mr_module.omit


async def test_create_async_stops_and_closes_on_terminal_status(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client(status="MODEL_RESOURCES_STATUS_ERROR")
    _patch_together(monkeypatch, client)

    with pytest.raises(RuntimeError, match="MODEL_RESOURCES_STATUS_ERROR"):
        await ModelResources.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.1, interval=0.0)

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


async def test_create_async_times_out_and_cleans_up(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client(status="MODEL_RESOURCES_STATUS_CREATING")
    _patch_together(monkeypatch, client)

    with pytest.raises(TimeoutError):
        await ModelResources.create_async(base_model="Qwen/Qwen3-0.6B", timeout=0.0, interval=0.0)

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


async def test_stop_async_closes_client_and_event_loop() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value={"id": "res-1"})
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    resources = ModelResources("res-1", _client=cast(Any, client))
    resources._event_loop = event_loop

    result = await resources.stop_async()

    assert result == {"id": "res-1"}
    assert event_loop.is_closed()
    assert resources._event_loop is None
    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


def test_retrieve_returns_resource() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_READY")
    )
    client.beta.rl.model_resources.stop = AsyncMock(return_value={"id": "res-1"})
    client.close = AsyncMock()
    resources = ModelResources("res-1", _client=cast(Any, client))

    result = resources.retrieve()

    assert result.id == "res-1"
    resources.stop()


async def test_retrieve_async_returns_resource() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(id="res-1", status="MODEL_RESOURCES_STATUS_READY")
    )
    resources = ModelResources("res-1", _client=cast(Any, client))

    result = await resources.retrieve_async()

    assert result.id == "res-1"
    client.beta.rl.model_resources.retrieve.assert_awaited_once_with("res-1")


async def test_attach_trainer_async_uses_model_resources_id(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    captured: dict[str, Any] = {}

    async def fake_create_async(**kwargs: Any) -> object:
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(Trainer, "create_async", fake_create_async)

    client = MagicMock()
    client.api_key = "key-1"
    client.base_url = "http://host"
    resources = ModelResources("res-1", _client=cast(Any, client))

    result = await resources.attach_trainer_async(lora_config=None)

    assert result is sentinel
    assert captured["model_resources_id"] == "res-1"
    assert captured["api_key"] == "key-1"
    assert captured["base_url"] == "http://host"


async def test_attach_async_binds_existing_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    _patch_together(monkeypatch, client)

    resources = await ModelResources.attach_async(model_resources_id="res-1")

    assert resources.model_resources_id == "res-1"
    client.beta.rl.model_resources.retrieve.assert_awaited_once_with("res-1")
    client.beta.rl.model_resources.create.assert_not_awaited()
    client.close.assert_not_awaited()


async def test_attach_async_raises_and_closes_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _fake_client()
    client.beta.rl.model_resources.retrieve = AsyncMock(side_effect=RuntimeError("not found"))
    _patch_together(monkeypatch, client)

    with pytest.raises(RuntimeError, match="not found"):
        await ModelResources.attach_async(model_resources_id="missing")

    client.close.assert_awaited_once()


async def test_detach_async_closes_client_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock()
    client.close = AsyncMock()
    resources = ModelResources("res-1", _client=cast(Any, client))

    await resources.detach_async()

    client.close.assert_awaited_once()
    client.beta.rl.model_resources.stop.assert_not_awaited()


def test_detach_closes_event_loop_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock()
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    resources = ModelResources("res-1", _client=cast(Any, client))
    resources._event_loop = event_loop

    resources.detach()

    assert event_loop.is_closed()
    assert resources._event_loop is None
    client.close.assert_awaited_once()
    client.beta.rl.model_resources.stop.assert_not_awaited()


def test_context_manager_stops() -> None:
    client = MagicMock()
    client.beta.rl.model_resources.stop = AsyncMock(return_value={"id": "res-1"})
    client.close = AsyncMock()
    resources = ModelResources("res-1", _client=cast(Any, client))

    with resources:
        assert resources.model_resources_id == "res-1"

    client.beta.rl.model_resources.stop.assert_awaited_once_with("res-1")
    client.close.assert_awaited_once()


def test_model_resources_is_publicly_exported() -> None:
    from together.lib.beta import ModelResources as FromBeta
    from together.lib.beta.rl import ModelResources as FromRl, ModelResourcesStatus

    assert FromRl is ModelResources
    assert FromBeta is ModelResources
    assert ModelResourcesStatus is not None
