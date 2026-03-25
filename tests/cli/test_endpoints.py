# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call
from click.testing import CliRunner

from together.lib.cli import main

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"
_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}

model_data = {
    "data": [
        {
            "id": "2x_nvidia_a100_80gb_sxm",
            "object": "hardware",
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
            },
        },
        {
            "id": "1x_nvidia_a100_80gb_sxm",
            "object": "hardware",
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
            },
        },
    ],
    "object": "list",
}

hardware_list_unfiltered = {
    "object": "list",
    "data": [model_data["data"][0]],
}

DEDICATED_EP = {
    "id": "endpoint-123",
    "object": "endpoint",
    "type": "dedicated",
    "name": "sys-name",
    "display_name": "My Endpoint",
    "hardware": "2x_nvidia_a100_80gb_sxm",
    "model": "deepseek-ai/DeepSeek-R1",
    "owner": "user",
    "state": "STARTED",
    "created_at": "2024-01-01T00:00:00Z",
    "autoscaling": {"min_replicas": 1, "max_replicas": 4},
}

ENDPOINT_LIST_ITEM = {
    "id": "ep-list-1",
    "object": "endpoint",
    "type": "dedicated",
    "name": "n1",
    "model": "m1",
    "owner": "o1",
    "state": "STARTED",
    "created_at": "2024-01-01T00:00:00Z",
}


class TestEndpointsCreate:
    # Test for endpoint create requiring the model
    def test_requires_model(self) -> None:
        runner = CliRunner(env=_ENV)
        assert runner.invoke(main, ["endpoints", "create"]).exit_code == 2

    # Test for when the API returns an error saying hardware is required
    @pytest.mark.respx(base_url=base_url)
    def test_invalid_hardware(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/endpoints").mock(
            return_value=httpx.Response(400, json={"error": {"message": "Hardware is required", "type": "bad_request"}})
        )
        runner = CliRunner(env=_ENV)
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
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "create", "--model", "deepseek-ai/DeepSeek-R1"])
        assert result.exit_code == 1
        assert (
            "Model 'deepseek-ai/DeepSeek-R1' was not found or is not available for dedicated endpoints."
            in result.output
        )


class TestEndpointsHardware:
    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=hardware_list_unfiltered))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "hardware"])
        assert result.exit_code == 0
        assert (
            result.output.strip()
            == """
Hardware ID              GPU    Memory    Count    Price (per minute)
-----------------------  -----  --------  -------  --------------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05               
""".strip()
        )

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1"])
        assert result.exit_code == 0
        assert (
            result.output.strip()
            == """
Hardware ID              GPU    Memory    Count    Price (per minute)    availability
-----------------------  -----  --------  -------  --------------------  --------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05                 ✓ available
1x_nvidia_a100_80gb_sxm  a100   80GB      1        $0.05                 ✗ unavailable
""".strip()
        )

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available"])
        assert result.exit_code == 0
        assert (
            result.output.strip()
            == """
Hardware ID              GPU    Memory    Count    Price (per minute)    availability
-----------------------  -----  --------  -------  --------------------  --------------
2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05                 ✓ available
""".strip()
        )

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main, ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available", "--json"]
        )

        data = json.loads(result.output)

        for item in data:
            assert item["availability"]["status"] == "available"


class TestEndpointsStart:
    def test_start_requires_id(self) -> None:
        runner = CliRunner(env=_ENV)
        assert runner.invoke(main, ["endpoints", "start"]).exit_code == 2

    @pytest.mark.respx(base_url=base_url)
    def test_start_endpoint(self, respx_mock: MockRouter) -> None:
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "start", "endpoint-123"])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully marked endpoint as starting\nendpoint-123"

    @pytest.mark.respx(base_url=base_url)
    def test_start_json(self, respx_mock: MockRouter) -> None:
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "start", "endpoint-123", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["id"] == "endpoint-123"
        assert body["state"] == "STARTED"

    @pytest.mark.respx(base_url=base_url)
    def test_start_wait(self, respx_mock: MockRouter) -> None:
        from unittest.mock import patch

        starting = {**DEDICATED_EP, "state": "STARTING"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        respx_mock.get("/endpoints/endpoint-123").mock(
            side_effect=[
                httpx.Response(200, json=starting),
                httpx.Response(200, json=DEDICATED_EP),
            ]
        )
        runner = CliRunner(env=_ENV)
        with patch("time.sleep"):
            result = runner.invoke(main, ["endpoints", "start", "endpoint-123", "--wait"])
        assert result.exit_code == 0
        assert "Endpoint started" in result.output
        assert "endpoint-123" in result.output


class TestEndpointsStop:
    def test_stop_requires_id(self) -> None:
        runner = CliRunner(env=_ENV)
        assert runner.invoke(main, ["endpoints", "stop"]).exit_code == 2

    @pytest.mark.respx(base_url=base_url)
    def test_stop_endpoint(self, respx_mock: MockRouter) -> None:
        stopped = {**DEDICATED_EP, "state": "STOPPED"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=stopped))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "stop", "endpoint-123"])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully marked endpoint as stopping\nendpoint-123"

    @pytest.mark.respx(base_url=base_url)
    def test_stop_json(self, respx_mock: MockRouter) -> None:
        stopped = {**DEDICATED_EP, "state": "STOPPED"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=stopped))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "stop", "endpoint-123", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["message"] == "Successfully marked endpoint as stopping"

    @pytest.mark.respx(base_url=base_url)
    def test_stop_wait(self, respx_mock: MockRouter) -> None:
        from unittest.mock import patch

        stopping = {**DEDICATED_EP, "state": "STOPPING"}
        stopped = {**DEDICATED_EP, "state": "STOPPED"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=stopping))
        respx_mock.get("/endpoints/endpoint-123").mock(
            side_effect=[
                httpx.Response(200, json=stopping),
                httpx.Response(200, json=stopped),
            ]
        )
        runner = CliRunner(env=_ENV)
        with patch("time.sleep"):
            result = runner.invoke(main, ["endpoints", "stop", "endpoint-123", "--wait"])
        assert result.exit_code == 0
        assert "Endpoint stopped" in result.output


class TestEndpointsListRetrieveDeleteUpdateAz:
    @pytest.mark.respx(base_url=base_url)
    def test_list_type_and_mine_query(self, respx_mock: MockRouter) -> None:
        list_body = {"object": "list", "data": [ENDPOINT_LIST_ITEM]}
        route = respx_mock.get("/endpoints").mock(return_value=httpx.Response(200, json=list_body))
        runner = CliRunner(env=_ENV)
        assert (
            runner.invoke(
                main,
                ["endpoints", "list", "--type", "dedicated", "--mine", "--usage-type", "on-demand"],
            ).exit_code
            == 0
        )
        url = str(cast(Call, route.calls[0]).request.url)
        assert "type=dedicated" in url
        assert "mine=true" in url
        assert "usage_type=on-demand" in url or "usage-type" in url

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter) -> None:
        list_body = {"object": "list", "data": [ENDPOINT_LIST_ITEM]}
        respx_mock.get("/endpoints").mock(return_value=httpx.Response(200, json=list_body))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)[0]["id"] == "ep-list-1"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/endpoints/ep-1").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "retrieve", "ep-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["display_name"] == "My Endpoint"

    @pytest.mark.respx(base_url=base_url)
    def test_delete_json(self, respx_mock: MockRouter) -> None:
        respx_mock.delete("/endpoints/ep-del").mock(return_value=httpx.Response(200))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "delete", "ep-del", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["message"] == "Successfully deleted endpoint"

    def test_update_requires_option(self) -> None:
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "update", "ep-1"])
        assert result.exit_code == 1
        assert "At least one update option" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_update_min_max_replicas(self, respx_mock: MockRouter) -> None:
        patch_route = respx_mock.patch("/endpoints/ep-1").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            ["endpoints", "update", "ep-1", "--min-replicas", "1", "--max-replicas", "3"],
        )
        assert result.exit_code == 0
        assert "ep-1" in result.output
        req = cast(Call, patch_route.calls[0]).request
        body = json.loads(req.content.decode())
        assert body["autoscaling"] == {"min_replicas": 1, "max_replicas": 3}

    @pytest.mark.respx(base_url=base_url)
    def test_availability_zones_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/clusters/availability-zones").mock(
            return_value=httpx.Response(200, json={"avzones": ["us-east-1a", "us-west-2b"]})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["endpoints", "availability-zones", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["avzones"] == ["us-east-1a", "us-west-2b"]
