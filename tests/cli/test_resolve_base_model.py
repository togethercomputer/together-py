from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from together.lib.cli.utils.config import CLIConfig
from together.types.beta.supported_model import SupportedModel
from together.lib.cli.api.beta.models._resolve_base_model import resolve_base_model_id
from together.types.beta.supported_model_deployment_profile import SupportedModelDeploymentProfile


def _profile(**overrides: Any) -> SupportedModelDeploymentProfile:
    body: dict[str, Any] = {
        "certifiedConfigRevisionId": "cr_1",
        "certifiedModelRevisionId": "rev_1",
        "config": "projects/together/configs/cr_1",
        "gpuCount": 1,
        "gpuType": "H100",
        "model": "projects/together/models/ml_base",
        "modelName": "meta-llama/Llama-3-8B-FP16",
        "parallelism": "TP1",
        "performanceBenchmarks": {},
        "profileId": "cr_1",
        "quantization": "fp16",
    }
    body.update(overrides)
    return SupportedModelDeploymentProfile.construct(**body)


def _supported_model(**overrides: Any) -> SupportedModel:
    body: dict[str, Any] = {
        "id": "sm_1",
        "baseModel": "projects/together/models/ml_base",
        "baseModelId": "ml_base",
        "capabilities": [],
        "createdAt": "2026-01-01T00:00:00Z",
        "deploymentProfiles": [_profile()],
        "displayName": "Llama 3 8B",
        "displayType": "chat",
        "inputModalities": [],
        "name": "meta-llama/Llama-3-8B",
        "outputModalities": [],
        "products": [],
        "publisher": "meta-llama",
        "status": "SUPPORTED_MODEL_STATUS_SUPPORTED",
        "updatedAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return SupportedModel.construct(**body)


def _cli_config(client: Any) -> CLIConfig:
    return CLIConfig(client=client, non_interactive=True, json=True, project_id="proj")


@pytest.mark.asyncio
async def test_model_id_passes_through_without_lookup() -> None:
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock()

    assert await resolve_base_model_id(_cli_config(client), "ml_base") == "ml_base"
    client.beta.models.list_supported.assert_not_awaited()


@pytest.mark.asyncio
async def test_exact_model_name_resolves_to_profile_model_id() -> None:
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock(return_value=MagicMock(data=[_supported_model()]))

    resolved = await resolve_base_model_id(_cli_config(client), "meta-llama/Llama-3-8B-FP16")

    client.beta.models.list_supported.assert_awaited_once_with(search="meta-llama/Llama-3-8B-FP16")
    assert resolved == "ml_base"


@pytest.mark.asyncio
async def test_exact_model_name_picks_matching_profile_among_many() -> None:
    profiles = [
        _profile(
            model="projects/together/models/ml_bf16",
            modelName="meta-llama/Llama-3-8B-BF16",
            profileId="cr_a",
            certifiedConfigRevisionId="cr_a",
        ),
        _profile(
            model="projects/together/models/ml_fp8",
            modelName="meta-llama/Llama-3-8B-FP8",
            profileId="cr_b",
            certifiedConfigRevisionId="cr_b",
            quantization="fp8",
        ),
    ]
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(data=[_supported_model(deploymentProfiles=profiles)]),
    )

    resolved = await resolve_base_model_id(_cli_config(client), "meta-llama/Llama-3-8B-FP8")
    assert resolved == "ml_fp8"


@pytest.mark.asyncio
async def test_no_exact_match_lists_candidates() -> None:
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock(return_value=MagicMock(data=[_supported_model()]))

    with pytest.raises(ValueError, match="No exact match for base model") as exc:
        await resolve_base_model_id(_cli_config(client), "meta-llama/Llama-3-8B")

    assert "meta-llama/Llama-3-8B-FP16" in str(exc.value)
    assert "ml_base" in str(exc.value)


@pytest.mark.asyncio
async def test_empty_search_results_raise() -> None:
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock(return_value=MagicMock(data=[]))

    with pytest.raises(ValueError, match='Base model "missing/model" not found'):
        await resolve_base_model_id(_cli_config(client), "missing/model")


@pytest.mark.asyncio
async def test_ambiguous_exact_name_requires_model_id() -> None:
    client = MagicMock()
    client.beta.models.list_supported = AsyncMock(
        return_value=MagicMock(
            data=[
                _supported_model(
                    id="sm_1",
                    deploymentProfiles=[
                        _profile(model="projects/together/models/ml_a", modelName="shared/name"),
                    ],
                ),
                _supported_model(
                    id="sm_2",
                    deploymentProfiles=[
                        _profile(model="projects/together/models/ml_b", modelName="shared/name"),
                    ],
                ),
            ]
        )
    )

    with pytest.raises(ValueError, match="Multiple models found") as exc:
        await resolve_base_model_id(_cli_config(client), "shared/name")

    assert "ml_a" in str(exc.value)
    assert "ml_b" in str(exc.value)
