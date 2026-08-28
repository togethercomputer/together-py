from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from together import APIError
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.api.endpoints.create import create


def _config() -> MagicMock:
    config = MagicMock()
    config.json = False
    return config


async def test_create_preserves_replica_validation_diagnostic() -> None:
    with pytest.raises(
        CliDiagnosticExit,
        match="^Endpoint minimum replicas cannot exceed maximum replicas$",
    ):
        await create("model", min_replicas=2, max_replicas=1, config=_config())


async def test_create_preserves_availability_zone_diagnostic() -> None:
    config = _config()
    config.client.endpoints.list_avzones = AsyncMock(return_value=SimpleNamespace(avzones=["zone-a"]))

    with pytest.raises(CliDiagnosticExit, match="^Endpoint availability zone is invalid$"):
        await create("model", availability_zone="zone-b", config=config)


@pytest.mark.parametrize(
    ("hardware", "message", "diagnostic"),
    [
        (None, "Hardware is required", "Endpoint hardware is required"),
        ("invalid-hardware", "Invalid hardware provided", "Endpoint hardware is invalid"),
    ],
)
async def test_create_preserves_hardware_diagnostic(
    hardware: str | None,
    message: str,
    diagnostic: str,
) -> None:
    config = _config()
    config.client.endpoints.create = AsyncMock(
        side_effect=APIError(message, httpx.Request("POST", "https://api.together.ai/v1/endpoints"), body=None)
    )

    with patch(
        "together.lib.cli.api.endpoints.create.list_hardware",
        new_callable=AsyncMock,
    ) as list_hardware:
        with pytest.raises(CliDiagnosticExit, match=f"^{diagnostic}$"):
            await create("model", hardware=hardware, config=config)

    list_hardware.assert_awaited_once_with(model="model", config=config, available=True)


async def test_create_preserves_unavailable_model_diagnostic() -> None:
    config = _config()
    config.client.endpoints.create = AsyncMock(
        side_effect=APIError(
            "Model not found",
            httpx.Request("POST", "https://api.together.ai/v1/endpoints"),
            body=None,
        )
    )

    with pytest.raises(CliDiagnosticExit, match="^Endpoint model is unavailable$"):
        await create("model", config=config)
