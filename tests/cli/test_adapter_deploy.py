from __future__ import annotations

from typing import Any

import pytest

from together.types.beta import Model, EndpointDeployment
from together.types.beta.models.config import Config
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.api.beta.endpoints._utils._adapter_deploy import (
    select_lora_config,
    config_adapter_mode,
    config_serves_adapters,
    deployment_serves_model,
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
