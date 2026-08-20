from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from together.lib.cli.utils.config import CLIConfig
from together.types.beta.models.config import Config
from together.types.beta.endpoints.inference_instance_type import InferenceInstanceType
from together.lib.cli.api.beta.endpoints._utils._hardware_pricing import (
    format_gpu_label,
    prettify_hardware,
    find_instance_type,
    format_estimated_price,
    hardware_from_selectors,
    resolve_hardware_pricing,
)


def _config(**overrides: Any) -> Config:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj",
        "referenceModel": "projects/proj/models/ml_1",
        "referenceModelId": "ml_1",
        "selectors": [
            {"key": "accelerator_count", "value": "1"},
            {"key": "accelerator_type", "value": "nvidia-h100-80gb"},
        ],
        "certifications": [],
    }
    body.update(overrides)
    return Config.construct(**body)


def _instance(**overrides: Any) -> InferenceInstanceType:
    body: dict[str, Any] = {
        "id": "it_h100",
        "name": "1xnvidia-h100-80gb",
        "description": "1x H100",
        "gpuCount": 1,
        "gpuMemoryGib": 80,
        "gpuType": "NVIDIA-H100-80GB-HBM3",
        "priceCentsPerHour": 2400,
        "regions": [],
    }
    body.update(overrides)
    return InferenceInstanceType.construct(**body)


def test_hardware_from_selectors() -> None:
    assert hardware_from_selectors(_config()) == "1xnvidia-h100-80gb"
    assert hardware_from_selectors(_config(selectors=[])) is None


def test_prettify_hardware() -> None:
    assert prettify_hardware("1xnvidia-h100-80gb") == "1x H100 80GB"
    assert prettify_hardware("8xnvidia-b200-180gb") == "8x B200 180GB"


def test_format_gpu_label() -> None:
    assert format_gpu_label(_instance()) == "1x H100 80GB"
    assert format_gpu_label(_instance(name="", gpuType="NVIDIA-H100-80GB-HBM3", gpuCount=2)) == "2x H100 80GB HBM3"


def test_format_estimated_price_single_and_range() -> None:
    assert format_estimated_price(2400, min_replicas=1, max_replicas=1) == "$24.00/hr"
    assert format_estimated_price(2400, min_replicas=1, max_replicas=2) == "$24.00/hr - $48.00/hr"
    assert format_estimated_price(2400, min_replicas=0, max_replicas=1) == "$0.00/hr - $24.00/hr"


def test_find_instance_type_exact_and_normalized() -> None:
    catalog = [_instance()]
    assert find_instance_type(catalog, hardware_id="1xnvidia-h100-80gb") is catalog[0]
    assert find_instance_type(catalog, hardware_id="1xh100-80gb") is catalog[0]
    assert find_instance_type(catalog, hardware_id="missing") is None


@pytest.mark.asyncio
async def test_resolve_hardware_pricing_happy_path() -> None:
    client = MagicMock()
    client.beta.endpoints.hardware.list = AsyncMock(
        return_value=MagicMock(data=[_instance()]),
    )
    cli = CLIConfig(client=client, non_interactive=True, json=False, project_id="proj")

    pricing = await resolve_hardware_pricing(cli, _config(), min_replicas=1, max_replicas=2)

    assert pricing is not None
    assert pricing.hardware_id == "1xnvidia-h100-80gb"
    assert pricing.gpu_label == "1x H100 80GB"
    assert pricing.estimated_price_label == "$24.00/hr - $48.00/hr"
    client.beta.endpoints.hardware.list.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_hardware_pricing_fetches_config_when_selectors_missing() -> None:
    client = MagicMock()
    client.beta.models.configs.retrieve = AsyncMock(return_value=_config())
    client.beta.endpoints.hardware.list = AsyncMock(
        return_value=MagicMock(data=[_instance()]),
    )
    cli = CLIConfig(client=client, non_interactive=True, json=False, project_id="proj")
    stub = _config(selectors=[])

    pricing = await resolve_hardware_pricing(cli, stub, min_replicas=1, max_replicas=1)

    assert pricing is not None
    assert pricing.estimated_price_label == "$24.00/hr"
    client.beta.models.configs.retrieve.assert_awaited_once_with("cr_1", project_id="proj")


@pytest.mark.asyncio
async def test_resolve_hardware_pricing_returns_none_without_hardware_selectors() -> None:
    client = MagicMock()
    client.beta.models.configs.retrieve = AsyncMock(
        return_value=_config(selectors=[{"key": "optimization", "value": "balanced"}]),
    )
    cli = CLIConfig(client=client, non_interactive=True, json=False, project_id="proj")

    pricing = await resolve_hardware_pricing(cli, _config(selectors=[]), min_replicas=1, max_replicas=1)

    assert pricing is None
    client.beta.endpoints.hardware.list.assert_not_called()
