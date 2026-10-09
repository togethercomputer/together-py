from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from together import NotFoundError
from together.types.beta import Model, EndpointDeployment
from together.lib.cli.utils.config import CLIConfig
from together.types.beta.models.config import Config
from together.lib.cli.api.beta.endpoints._utils._resolve_model import load_model
from together.lib.cli.api.beta.endpoints._utils._adapter_deploy import (
    is_adapter_model,
    select_lora_config,
    config_adapter_mode,
    config_serves_adapters,
    deployment_serves_model,
    load_client_project_adapter,
    select_lora_config_for_deploy,
)


def _config(**overrides: Any) -> Config:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj",
        "referenceModelId": "ml_base",
        "referenceModel": "projects/proj/models/ml_base",
        "selectors": [],
        "certifications": [],
    }
    body.update(overrides)
    return Config.construct(**body)


def _model(**overrides: Any) -> Model:
    body: dict[str, Any] = {
        "id": "ml_base",
        "projectId": "proj",
        "name": "my-project/base",
        "organizationId": "org",
        "visibility": "VISIBILITY_PRIVATE",
        "weights": {"type": "WEIGHTS_TYPE_DEFAULT"},
    }
    body.update(overrides)
    return Model.construct(**body)


def _deployment(**overrides: Any) -> EndpointDeployment:
    body: dict[str, Any] = {
        "id": "dep_1",
        "model": "projects/proj/models/ml_base/revisions/rv_1",
        "modelId": "ml_base",
        "config": "projects/proj/configs/cr_1",
        "configId": "cr_1",
        "trafficMode": "TRAFFIC_MODE_LIVE",
    }
    body.update(overrides)
    return EndpointDeployment.construct(**body)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("fixed", "fixed"),
        ("dynamic", "dynamic"),
        ("disabled", "disabled"),
        ("ADAPTER_MODE_FIXED", "fixed"),
        ("ADAPTER_MODE_DYNAMIC", "dynamic"),
    ],
)
def test_config_adapter_mode_reads_selector(value: str, expected: str) -> None:
    model_config = _config(selectors=[{"key": "adapter_mode", "value": value}])

    assert config_adapter_mode(model_config) == expected
    assert config_serves_adapters(model_config) is (expected in {"fixed", "dynamic"})


def test_config_adapter_mode_reads_enum_extra() -> None:
    model_config = _config()
    model_config.__pydantic_extra__ = {"adapterMode": "ADAPTER_MODE_DYNAMIC"}  # type: ignore[attr-defined]

    assert config_adapter_mode(model_config) == "dynamic"
    assert config_serves_adapters(model_config)


def test_missing_adapter_mode_does_not_serve_adapters() -> None:
    assert config_adapter_mode(_config()) is None
    assert not config_serves_adapters(_config())


def test_deployment_serves_model_matches_revision_path() -> None:
    base = _model()
    assert deployment_serves_model(_deployment(), base)
    assert not deployment_serves_model(_deployment(modelId="ml_other", model="projects/proj/models/ml_other"), base)


def test_select_lora_config_requires_a_choice_when_fixed_and_dynamic_exist() -> None:
    fixed = _config(id="cr_fixed", selectors=[{"key": "adapter_mode", "value": "fixed"}])
    dynamic = _config(id="cr_dynamic", selectors=[{"key": "adapter_mode", "value": "dynamic"}])

    with pytest.raises(ValueError, match="Multiple configs found"):
        select_lora_config([fixed, dynamic], None, model="my-project/base")


async def test_select_lora_config_prompts_when_fixed_and_dynamic_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed = _config(id="cr_fixed", selectors=[{"key": "adapter_mode", "value": "fixed"}])
    dynamic = _config(id="cr_dynamic", selectors=[{"key": "adapter_mode", "value": "dynamic"}])

    async def choose(_self: object, _field: str) -> str:
        return "cr_fixed"

    monkeypatch.setattr(
        "together.lib.cli.utils._prompt.PromptParameter.prompt",
        choose,
    )
    cli = CLIConfig(client=None, non_interactive=False, json=False, project_id="proj")  # type: ignore[arg-type]

    selected = await select_lora_config_for_deploy(cli, [fixed, dynamic], None, model="my-project/base")

    assert selected.id == "cr_fixed"


def test_select_lora_config_falls_back_to_fixed_when_no_dynamic_config() -> None:
    disabled = _config(id="cr_disabled", selectors=[{"key": "adapter_mode", "value": "disabled"}])
    fixed = _config(id="cr_fixed", selectors=[{"key": "adapter_mode", "value": "fixed"}])

    selected = select_lora_config([disabled, fixed], None, model="my-project/base")

    assert selected.id == "cr_fixed"


def test_select_lora_config_picks_the_only_fixed_or_dynamic_config() -> None:
    disabled = _config(id="cr_disabled", selectors=[{"key": "adapter_mode", "value": "disabled"}])
    dynamic = _config(id="cr_dynamic", selectors=[{"key": "adapter_mode", "value": "dynamic"}])

    selected = select_lora_config([disabled, dynamic], None, model="my-project/base")

    assert selected.id == "cr_dynamic"


def test_select_lora_config_rejects_disabled_explicit_config() -> None:
    disabled = _config(id="cr_disabled", selectors=[{"key": "adapter_mode", "value": "disabled"}])

    with pytest.raises(ValueError, match="adapter_mode disabled"):
        select_lora_config([disabled], "cr_disabled", model="my-project/base")


def test_select_lora_config_fails_when_none_can_host_an_adapter() -> None:
    disabled = _config(selectors=[{"key": "adapter_mode", "value": "disabled"}])

    with pytest.raises(ValueError, match="No fixed or dynamic LoRA config"):
        select_lora_config([disabled], None, model="ml_base")


def _cli(client: Any, *, project_id: str | None) -> CLIConfig:
    return CLIConfig(client=client, non_interactive=True, json=True, project_id=project_id)


async def test_bare_id_without_project_skips_default_project_retrieve() -> None:
    client = MagicMock()
    client.project_id = "proj_default"
    client.beta.models.retrieve = AsyncMock()

    assert await load_model(_cli(client, project_id=None), "ml_public") is None
    client.beta.models.retrieve.assert_not_awaited()


async def test_bare_id_not_in_project_is_not_an_adapter() -> None:
    client = MagicMock()
    client.project_id = "proj"
    client.beta.models.retrieve = AsyncMock(
        side_effect=NotFoundError(message="Model not found", response=MagicMock(), body=None),
    )

    assert await load_model(_cli(client, project_id="proj"), "ml_public") is None
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_public", project_id="proj")


async def test_adapter_rollback_text_is_omitted_in_json_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from together.types.beta import Endpoint
    from together.lib.cli.api.beta.endpoints import deploy as deploy_mod

    base = _model()
    selected = _config(selectors=[{"key": "adapter_mode", "value": "dynamic"}])
    endpoint = Endpoint.construct(id="ep_1", name="proj/ep", etag="etag")
    deployment = _deployment(id="dep_1", etag="dtag")

    async def _return_base(*_args: object, **_kwargs: object) -> Model:
        return base

    async def _return_configs(*_args: object, **_kwargs: object) -> list[Config]:
        return [selected]

    async def _no_endpoint(*_args: object, **_kwargs: object) -> None:
        return None

    async def _return_config(*_args: object, **_kwargs: object) -> Config:
        return selected

    async def _new_endpoint(*_args: object, **_kwargs: object) -> tuple[Endpoint, bool]:
        return endpoint, True

    async def _passthrough(_message: str, request: Any) -> Any:
        return await request

    monkeypatch.setattr(deploy_mod, "load_base_model", _return_base)
    monkeypatch.setattr(deploy_mod, "list_model_configs", _return_configs)
    monkeypatch.setattr(deploy_mod, "_peek_endpoint", _no_endpoint)
    monkeypatch.setattr(deploy_mod, "select_lora_config_for_deploy", _return_config)
    monkeypatch.setattr(deploy_mod, "assert_explicit_project_id", _no_endpoint)
    monkeypatch.setattr(deploy_mod, "_find_or_create_endpoint", _new_endpoint)
    monkeypatch.setattr(deploy_mod, "show_loading_status", _passthrough)

    client = MagicMock()
    client.beta.endpoints.delete = AsyncMock()
    client.beta.endpoints.deployments.delete = AsyncMock()
    client.beta.endpoints.deployments.create = AsyncMock(side_effect=RuntimeError("create failed"))
    cli = _cli(client, project_id="proj")
    cli.json = True

    with pytest.raises(RuntimeError, match="create failed"):
        await deploy_mod._deploy_adapter(
            cli,
            adapter=_model(id="ml_lora", name="proj/lora", weights={"type": "WEIGHTS_TYPE_ADAPTER"}),
            adapter_revision=None,
            endpoint_name_or_id="ep",
            config_id=None,
            min_replicas=None,
            max_replicas=None,
            scale_up_window=None,
            scale_down_window=None,
            scaling_metric=None,
            scaling_target=None,
            scaling_percentile=None,
            deployment_name="dep",
            placement_id=None,
            placement_value=None,
            inactive_timeout=None,
            max_concurrent_requests_per_replica=None,
            traffic_weight=None,
        )

    assert "Rolling back" not in capsys.readouterr().out

    client.beta.endpoints.deployments.create = AsyncMock(return_value=deployment)
    client.beta.endpoints.adapters.create = AsyncMock(side_effect=RuntimeError("attach failed"))

    with pytest.raises(RuntimeError, match="attach failed"):
        await deploy_mod._deploy_adapter(
            cli,
            adapter=_model(id="ml_lora", name="proj/lora", weights={"type": "WEIGHTS_TYPE_ADAPTER"}),
            adapter_revision=None,
            endpoint_name_or_id="ep",
            config_id=None,
            min_replicas=None,
            max_replicas=None,
            scale_up_window=None,
            scale_down_window=None,
            scaling_metric=None,
            scaling_target=None,
            scaling_percentile=None,
            deployment_name="dep",
            placement_id=None,
            placement_value=None,
            inactive_timeout=None,
            max_concurrent_requests_per_replica=None,
            traffic_weight=None,
        )

    assert "Rolling back" not in capsys.readouterr().out


async def test_bare_id_in_project_still_loads_an_adapter() -> None:
    adapter = _model(id="ml_lora", weights={"type": "WEIGHTS_TYPE_ADAPTER"})
    client = MagicMock()
    client.project_id = "proj"
    client.beta.models.retrieve = AsyncMock(return_value=adapter)

    loaded = await load_model(_cli(client, project_id="proj"), "ml_lora")

    assert loaded is adapter
    assert is_adapter_model(loaded)
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_lora", project_id="proj")


async def test_default_project_non_adapter_is_ignored() -> None:
    client = MagicMock()
    client.project_id = "proj_default"
    client.beta.models.retrieve = AsyncMock(return_value=_model(id="ml_public"))

    assert await load_client_project_adapter(_cli(client, project_id=None), "ml_public") is None
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_public", project_id="proj_default")


async def test_default_project_adapter_is_returned_for_deploy() -> None:
    adapter = _model(id="ml_lora", projectId="proj_default", weights={"type": "WEIGHTS_TYPE_ADAPTER"})
    client = MagicMock()
    client.project_id = "proj_default"
    client.beta.models.retrieve = AsyncMock(return_value=adapter)

    loaded = await load_client_project_adapter(_cli(client, project_id=None), "ml_lora")

    assert loaded is adapter
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_lora", project_id="proj_default")
