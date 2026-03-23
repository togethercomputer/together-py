# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import os

import click
import httpx
import pytest
from respx import MockRouter
from click.testing import CliRunner

from together.lib.cli import main

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

model_data = {
    "data": [
        {
            "id": "2x_nvidia_a100_80gb_sxm",
            "specs": {
                "gpu_type": "a100",
                "gpu_memory": 80,
                "gpu_count": 2,
                "gpu_link": "sxm",
            },
            "pricing": {
                "cents_per_minute": 5,
            },
            "updated_at": "2026-03-23T12:00:00Z",
            "availability": {
                "status": "available",
            }
        },
        {
            "id": "1x_nvidia_a100_80gb_sxm",
            "specs": {
                "gpu_type": "a100",
                "gpu_memory": 80,
                "gpu_count": 1,
                "gpu_link": "sxm",
            },
            "pricing": {
                "cents_per_minute": 5,
            },
            "updated_at": "2026-03-23T12:00:00Z",
            "availability": {
                "status": "unavailable",
            }
        }
    ],
    "object": "list"
}

class TestEndpointsCreate:
    # Test for endpoint create requiring the model
    def test_requires_model(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        assert runner.invoke(main, ["endpoints", "create"]).exit_code == 2

    # Test for when the API returns an error saying hardware is required
    @pytest.mark.respx(base_url=base_url)
    def test_invalid_hardware(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/endpoints").mock(
            return_value=httpx.Response(400, json={"error": {"message": "Hardware is required", "type": "bad_request"}})
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(
            main, ["endpoints", "create", "--model", "deepseek-ai/DeepSeek-R1", "--hardware", "foooooooo"]
        )
        assert result.exit_code == 1
        assert "Invalid hardware selected." in result.output

    
    # Test for when the API returns an error saying model not found
    @pytest.mark.respx(base_url=base_url)
    def test_invalid_model(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/endpoints").mock(
            return_value=httpx.Response(400, json={"error": {"message": "Model not found", "type": "bad_request"}})
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["endpoints", "create", "--model", "deepseek-ai/DeepSeek-R1"])
        assert result.exit_code == 1
        assert (
            "Model 'deepseek-ai/DeepSeek-R1' was not found or is not available for dedicated endpoints."
            in result.output
        )

class TestEndpointsHardware:
    def test_hardware_list(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["endpoints", "hardware"])
        assert result.exit_code == 0
        assert result.output.strip() == """
Hardware ID              GPU    Memory    Count    Price (per minute)
-----------------------  -----  --------  -------  --------------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05               
""".strip()

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(
            return_value=httpx.Response(200, json=model_data)
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1"])
        assert result.exit_code == 0
        assert result.output.strip() == """
Hardware ID              GPU    Memory    Count    Price (per minute)    availability
-----------------------  -----  --------  -------  --------------------  --------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05                 ✓ available
1x_nvidia_a100_80gb_sxm  a100   80GB      1        $0.05                 ✗ unavailable
""".strip()

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(
            return_value=httpx.Response(200, json=model_data)
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available"])
        assert result.exit_code == 0
        assert result.output.strip() == """
Hardware ID              GPU    Memory    Count    Price (per minute)    availability
-----------------------  -----  --------  -------  --------------------  --------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05                 ✓ available
""".strip()

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(
            return_value=httpx.Response(200, json=model_data)
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})
        result = runner.invoke(main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available", "--json"])

        data = json.loads(result.output)

        for item in data:
            assert item["availability"]["status"] == "available"


class TestEndpointsStart:
    # TODO: add tests for the --wait
    def test_start_endpoint(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})

        # raises argument error without an endpoint id
        assert runner.invoke(main, ["endpoints", "start"]).exit_code == 2

        # starts the endpoint
        result = runner.invoke(main, ["endpoints", "start", "endpoint-123"])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully marked endpoint as starting\nendpoint-123"

class TestEndpointsStop:
    # TODO: add tests for the --wait
    def test_stop_endpoint(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url})

        # raises argument error without an endpoint id
        assert runner.invoke(main, ["endpoints", "stop"]).exit_code == 2

        # starts the endpoint
        result = runner.invoke(main, ["endpoints", "stop", "endpoint-123"])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully marked endpoint as stopping\nendpoint-123"