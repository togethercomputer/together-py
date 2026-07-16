from __future__ import annotations

from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest

from together.types.beta import Model
from together.lib.cli.utils.config import CLIConfig
from together.types.beta.models.config import Config
from together.types.beta.supported_model import SupportedModel
from together.types.beta.supported_model_deployment_profile import SupportedModelDeploymentProfile
from together.lib.cli.api.beta.endpoints._utils._resolve_model import (
    construct_model_path,
    resolve_model_and_config,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_config import construct_config_path


def _config(**overrides: Any) -> Config:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj_public",
        "referenceModelId": "ml_base",
        "referenceModel": "projects/proj_public/models/ml_base",
        "selectors": [],
        "certifications": [],
    }
    body.update(overrides)
    return Config.construct(**body)


def _private_model(**overrides: Any) -> Model:
    body: dict[str, Any] = {
        "id": "ml_custom",
        "projectId": "proj_mine",
        "name": "my-slug/custom-model",
        "baseModelId": "ml_base",
        "organizationId": "org_1",
        "visibility": "VISIBILITY_PRIVATE",
        "weights": {},
    }
    body.update(overrides)
    return Model.construct(**body)


def _profile(**overrides: Any) -> SupportedModelDeploymentProfile:
    body: dict[str, Any] = {
        "certifiedConfigRevisionId": "cr_pub",
        "certifiedModelRevisionId": "rev_1",
        "config": "projects/proj_public/configs/cr_pub",
        "gpuCount": 1,
        "gpuType": "H100",
        "model": "projects/proj_public/models/ml_pub",
        "parallelism": "TP1",
        "performanceBenchmarks": {},
        "profileId": "cr_pub",
        "quantization": "fp16",
    }
    body.update(overrides)
    return SupportedModelDeploymentProfile.construct(**body)


def _supported_model(**overrides: Any) -> SupportedModel:
    body: dict[str, Any] = {
        "id": "sm_1",
        "baseModel": "projects/proj_public/models/ml_pub",
        "baseModelId": "ml_pub",
        "capabilities": [],
        "createdAt": "2026-01-01T00:00:00Z",
        "deploymentProfiles": [_profile()],
        "displayName": "Pub Model",
        "displayType": "chat",
        "inputModalities": [],
        "name": "meta-llama/Llama-3-8b",
        "outputModalities": [],
        "products": [],
        "publisher": "meta-llama",
        "status": "SUPPORTED_MODEL_STATUS_SUPPORTED",
        "updatedAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return SupportedModel.construct(**body)


def _cli_config(client: Any) -> CLIConfig:
    return CLIConfig(client=client, non_interactive=True, json=True, project_id="proj_mine")


@pytest.mark.asyncio
async def test_raw_model_id_resolves_via_configs() -> None:
    retrieved = _private_model(
        id="ml_base",
        projectId="proj_public",
        name="together/some-named-model",
        baseModelId=None,
    )
    client = MagicMock()
    client.beta.models.configs.list = AsyncMock(
        return_value=MagicMock(data=[_config()]),
    )
    client.beta.models.retrieve = AsyncMock(return_value=retrieved)
    client.whoami = AsyncMock()

    model, config = await resolve_model_and_config(_cli_config(client), "ml_base", config_id=None)

    client.beta.models.configs.list.assert_awaited_once_with(reference_model_id="ml_base")
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_base", project_id="proj_public")
    client.whoami.assert_not_awaited()
    assert model.name == "together/some-named-model"
    assert construct_model_path(model) == "projects/proj_public/models/ml_base"
    assert construct_config_path(config) == "projects/proj_public/configs/cr_1"


@pytest.mark.asyncio
async def test_full_model_path_parses_id_then_configs() -> None:
    client = MagicMock()
    client.beta.models.configs.list = AsyncMock(
        return_value=MagicMock(data=[_config()]),
    )
    client.beta.models.retrieve = AsyncMock(
        return_value=_private_model(id="ml_base", projectId="proj_public", name="together/base"),
    )

    model, config = await resolve_model_and_config(
        _cli_config(client),
        "projects/proj_public/models/ml_base/revisions/rev_9",
        config_id="cr_1",
    )

    client.beta.models.configs.list.assert_awaited_once_with(reference_model_id="ml_base")
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_base", project_id="proj_public")
    assert model.id == "ml_base"
    assert model.name == "together/base"
    assert config.id == "cr_1"


@pytest.mark.asyncio
async def test_private_named_model_uses_base_model_id_for_config_but_custom_path() -> None:
    private = _private_model()

    async def _list_models() -> AsyncIterator[Model]:
        yield private

    client = MagicMock()
    client.whoami = AsyncMock(return_value=MagicMock(project_slug="my-slug"))
    client.beta.models.list = MagicMock(return_value=_list_models())
    client.beta.models.configs.list = AsyncMock(
        return_value=MagicMock(data=[_config()]),
    )
    client.beta.models.retrieve = AsyncMock(
        return_value=_private_model(id="ml_base", projectId="proj_public", name="together/base"),
    )

    model, config = await resolve_model_and_config(
        _cli_config(client),
        "my-slug/custom-model",
        config_id=None,
    )

    client.beta.models.configs.list.assert_awaited_once_with(reference_model_id="ml_base")
    client.beta.models.retrieve.assert_awaited_once_with(id="ml_base", project_id="proj_public")
    assert construct_model_path(model) == "projects/proj_mine/models/ml_custom"
    assert construct_config_path(config) == "projects/proj_public/configs/cr_1"
    assert model.name == "my-slug/custom-model"


@pytest.mark.asyncio
async def test_public_named_model_uses_deployment_profile() -> None:
    client = MagicMock()
    client.whoami = AsyncMock(return_value=MagicMock(project_slug="my-slug"))
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(data=[_supported_model()]),
    )

    model, config = await resolve_model_and_config(
        _cli_config(client),
        "meta-llama/Llama-3-8b",
        config_id=None,
    )

    client.beta.models.list_supported.assert_awaited_once_with(search="meta-llama/Llama-3-8b")
    assert construct_model_path(model) == "projects/proj_public/models/ml_pub"
    assert construct_config_path(config) == "projects/proj_public/configs/cr_pub"
    assert model.name == "meta-llama/Llama-3-8b"


@pytest.mark.asyncio
async def test_public_model_requires_exactly_one_supported_match() -> None:
    client = MagicMock()
    client.whoami = AsyncMock(return_value=MagicMock(project_slug="my-slug"))
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(data=[_supported_model(), _supported_model(id="sm_2")]),
    )

    with pytest.raises(ValueError, match="Multiple models found"):
        await resolve_model_and_config(_cli_config(client), "meta-llama/Llama")


@pytest.mark.asyncio
async def test_public_model_selects_profile_by_config_id() -> None:
    profiles = [
        _profile(certifiedConfigRevisionId="cr_a", config="projects/proj_public/configs/cr_a", profileId="cr_a"),
        _profile(
            certifiedConfigRevisionId="cr_b",
            config="projects/proj_public/configs/cr_b",
            profileId="cr_b",
            model="projects/proj_public/models/ml_pub_b",
        ),
    ]
    client = MagicMock()
    client.whoami = AsyncMock(return_value=MagicMock(project_slug="my-slug"))
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(data=[_supported_model(deploymentProfiles=profiles)]),
    )

    model, config = await resolve_model_and_config(
        _cli_config(client),
        "meta-llama/Llama-3-8b",
        config_id="cr_b",
    )

    assert config.id == "cr_b"
    assert construct_model_path(model) == "projects/proj_public/models/ml_pub_b"


@pytest.mark.asyncio
async def test_public_model_multiple_profiles_requires_flags(capsys: pytest.CaptureFixture[str]) -> None:
    profiles = [
        _profile(
            certifiedConfigRevisionId="cr_a",
            config="projects/proj_public/configs/cr_a",
            profileId="cr_a",
            quantization="BF16",
            model="projects/proj_public/models/ml_a/revisions/rv_1",
        ),
        _profile(
            certifiedConfigRevisionId="cr_b",
            config="projects/proj_public/configs/cr_b",
            profileId="cr_b",
            quantization="FP8",
            model="projects/proj_public/models/ml_b/revisions/rv_2",
        ),
    ]
    client = MagicMock()
    client.whoami = AsyncMock(return_value=MagicMock(project_slug="my-slug"))
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(data=[_supported_model(deploymentProfiles=profiles)]),
    )

    with pytest.raises(ValueError, match="Multiple configs found"):
        await resolve_model_and_config(_cli_config(client), "meta-llama/Llama-3-8b")

    output = capsys.readouterr().out
    assert "Available configs for meta-llama/Llama-3-8b" in output
    assert "cr_a" in output
    assert "cr_b" in output
    assert "ml_a" in output
    assert "ml_b" in output
    assert "--model ml_a --config cr_a" in output


@pytest.mark.asyncio
async def test_raw_model_rejects_mismatched_config_id() -> None:
    client = MagicMock()
    client.beta.models.configs.list = AsyncMock(
        return_value=MagicMock(data=[_config()]),
    )

    with pytest.raises(ValueError, match="Config cr_other is not valid"):
        await resolve_model_and_config(_cli_config(client), "ml_base", config_id="cr_other")
