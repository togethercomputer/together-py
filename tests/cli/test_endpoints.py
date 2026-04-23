# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

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

# Rich ListTable with expand=True uses 80-char width; title line is padded.
_HW_TITLE_80 = "Hardware" + " " * 72
_EXPECTED_HW_TABLE_MODEL = (
    _HW_TITLE_80
    + "\n"
    + (
        "╭───────────────────────────┬────────────┬────────────┬────────────┬───────────╮\n"
        "│                           │            │            │            │  Price    │\n"
        "│                           │            │            │            │  (per     │\n"
        "│  Hardware ID              │  GPU       │  Memory    │  Count     │  minute)  │\n"
        "├───────────────────────────┼────────────┼────────────┼────────────┼───────────┤\n"
        "│  2x_nvidia_a100_80gb_sxm  │  a100      │  80GB      │  2         │  $0.05    │\n"
        "├───────────────────────────┼────────────┼────────────┼────────────┼───────────┤\n"
        "│  1x_nvidia_a100_80gb_sxm  │  a100      │  80GB      │  1         │  $0.05    │\n"
        "╰───────────────────────────┴────────────┴────────────┴────────────┴───────────╯"
    )
)
_EXPECTED_HW_TABLE_AVAILABLE = (
    _HW_TITLE_80
    + "\n"
    + (
        "╭───────────────────────────┬──────────┬─────────┬─────────┬─────────┬─────────╮\n"
        "│                           │          │         │         │  Price  │         │\n"
        "│                           │          │         │         │  (per   │         │\n"
        "│  Hardware ID              │  GPU     │  Memo…  │  Count  │  minu…  │  Avai…  │\n"
        "├───────────────────────────┼──────────┼─────────┼─────────┼─────────┼─────────┤\n"
        "│  2x_nvidia_a100_80gb_sxm  │  a100    │  80GB   │  2      │  $0.05  │  ✓      │\n"
        "│                           │          │         │         │         │  avai…  │\n"
        "╰───────────────────────────┴──────────┴─────────┴─────────┴─────────┴─────────╯"
    )
)

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


# class TestEndpointsCreate:
#     # Test for endpoint create requiring the model
#     def test_requires_model(self, cli_runner: CliRunner) -> None:
#         assert cli_runner.invoke(["endpoints", "create"]).exit_code == 1

#     # Test for when the API returns an error saying hardware is required
#     @pytest.mark.respx(base_url=base_url)
#     def test_invalid_hardware(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
#         respx_mock.post("/endpoints").mock(
#             return_value=httpx.Response(400, json={"error": {"message": "Hardware is required", "type": "bad_request"}})
#         )
#         result = cli_runner.invoke(["endpoints", "create", "--model", "deepseek-ai/DeepSeek-R1", "--hardware", "foooooooo"])
#         assert "Invalid hardware selected." in result.output
#         assert result.exit_code == 1

#     # Test for when the API returns an error saying model not found
#     @pytest.mark.respx(base_url=base_url)
#     def test_invalid_model(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
#         import together.lib.cli.utils._console
#         from rich.console import Console
#         monkeypatch.setattr(together.lib.cli.utils._console, "console", Console(width=200))
#         respx_mock.post("/endpoints").mock(
#             return_value=httpx.Response(400, json={"error": {"message": "Model not found", "type": "bad_request"}})
#         )
#         result = cli_runner.invoke(["endpoints", "create", "--model", "deepseek-ai/DeepSeek-R1"])
#         print('--------------------------------')
#         print(result.output)
#         print('--------------------------------')
#         assert (
#             "Model 'deepseek-ai/DeepSeek-R1' was not found or is not available for dedicated endpoints."
#             in result.out_out
#         )
#         assert result.exit_code == 1


class TestEndpointsHardware:
    #     @pytest.mark.respx(base_url=base_url)
    #     def test_hardware_list(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
    #         respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=hardware_list_unfiltered))
    #         result = cli_runner.invoke(["endpoints", "hardware"])
    #         assert (
    #             result.output.strip()
    #             == dedent(
    #         """\
    # Hardware ID              GPU    Memory    Count    Price (per minute)
    # -----------------------  -----  --------  -------  --------------------
    # 2x_nvidia_a100_80gb_sxm  a100   80GB      2        $0.05
    # """)
    #         )
    #         assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        result = cli_runner.invoke(["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1"])
        assert result.out_out.strip() == _EXPECTED_HW_TABLE_MODEL
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        result = cli_runner.invoke(["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available"])
        assert result.out_out.strip() == _EXPECTED_HW_TABLE_AVAILABLE
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_hardware_list_with_model_and_available_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/hardware").mock(return_value=httpx.Response(200, json=model_data))
        result = cli_runner.invoke(
            ["endpoints", "hardware", "--model", "deepseek-ai/DeepSeek-R1", "--available", "--json"]
        )

        data = json.loads(result.output)

        for item in data:
            assert item["availability"]["status"] == "available"


class TestEndpointsStart:
    # Command now loads the endpoints and lets user select the endpoint to start
    # TODO: Add a test for this
    # def test_start_requires_id(self, cli_runner: CliRunner) -> None:
    #     assert cli_runner.invoke(["endpoints", "start"]).exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_start_endpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        result = cli_runner.invoke(["endpoints", "start", "endpoint-123"])
        assert result.output.strip() == "√ Endpoint is starting.\n  This may take a few minutes."
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_start_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        result = cli_runner.invoke(["endpoints", "start", "endpoint-123", "--json"])
        body = json.loads(result.output)
        assert body["id"] == "endpoint-123"
        assert body["state"] == "STARTED"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_start_wait(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        from unittest.mock import patch

        starting = {**DEDICATED_EP, "state": "STARTING"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        respx_mock.get("/endpoints/endpoint-123").mock(
            side_effect=[
                httpx.Response(200, json=starting),
                httpx.Response(200, json=DEDICATED_EP),
            ]
        )
        with patch("time.sleep"):
            result = cli_runner.invoke(["endpoints", "start", "endpoint-123", "--wait"])
        assert "√ Endpoint started" in result.output
        assert result.exit_code == 0


class TestEndpointsStop:
    def test_stop_requires_id(self, cli_runner: CliRunner) -> None:
        assert cli_runner.invoke(["endpoints", "stop"]).exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_stop_endpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        stopped = {**DEDICATED_EP, "state": "STOPPED"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=stopped))
        result = cli_runner.invoke(["endpoints", "stop", "endpoint-123"])
        assert result.output.strip() == "√ Endpoint is stopping.\n  This may take a few minutes."
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_stop_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        stopped = {**DEDICATED_EP, "state": "STOPPED"}
        respx_mock.patch("/endpoints/endpoint-123").mock(return_value=httpx.Response(200, json=stopped))
        result = cli_runner.invoke(["endpoints", "stop", "endpoint-123", "--json"])
        assert json.loads(result.output)["message"] == "Successfully marked endpoint as stopping"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_stop_wait(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
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
        with patch("time.sleep"):
            result = cli_runner.invoke(["endpoints", "stop", "endpoint-123", "--wait"])
        assert "Endpoint stopped" in result.output
        assert result.exit_code == 0


class TestEndpointsListRetrieveDeleteUpdateAz:
    @pytest.mark.respx(base_url=base_url)
    def test_list_type_and_mine_query(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        list_body = {"object": "list", "data": [ENDPOINT_LIST_ITEM]}
        route = respx_mock.get("/endpoints").mock(return_value=httpx.Response(200, json=list_body))
        result = cli_runner.invoke(["endpoints", "list", "--type", "dedicated", "--mine", "--usage-type", "on-demand"])
        assert result.exit_code == 0
        url = str(cast(Call, route.calls[0]).request.url)
        assert "type=dedicated" in url
        assert "mine=true" in url
        assert "usage_type=on-demand" in url or "usage-type" in url

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        list_body = {"object": "list", "data": [ENDPOINT_LIST_ITEM]}
        respx_mock.get("/endpoints").mock(return_value=httpx.Response(200, json=list_body))
        result = cli_runner.invoke(["endpoints", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.out_out)[0]["id"] == "ep-list-1"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/endpoints/ep-1").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        result = cli_runner.invoke(["endpoints", "retrieve", "ep-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["display_name"] == "My Endpoint"

    @pytest.mark.respx(base_url=base_url)
    def test_delete_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/endpoints/ep-del").mock(return_value=httpx.Response(200))
        result = cli_runner.invoke(["endpoints", "delete", "ep-del", "--json", "--yes"])
        assert json.loads(result.output)["message"] == "Successfully deleted endpoint"
        assert result.exit_code == 0

    def test_update_requires_option(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["endpoints", "update", "ep-1"])
        assert "At least one update option must be specified" in result.out_out
        assert result.exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_update_min_max_replicas(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        patch_route = respx_mock.patch("/endpoints/ep-1").mock(return_value=httpx.Response(200, json=DEDICATED_EP))
        result = cli_runner.invoke(
            ["endpoints", "update", "ep-1", "--min-replicas", "1", "--max-replicas", "3"],
        )
        assert "Endpoint updated." in result.out_out
        req = cast(Call, patch_route.calls[0]).request
        body = json.loads(req.content.decode())
        assert body["autoscaling"] == {"min_replicas": 1, "max_replicas": 3}
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_availability_zones_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/clusters/availability-zones").mock(
            return_value=httpx.Response(200, json={"avzones": ["us-east-1a", "us-west-2b"]})
        )
        result = cli_runner.invoke(["endpoints", "availability-zones", "--json"])
        assert json.loads(result.output)["avzones"] == ["us-east-1a", "us-west-2b"]
        assert result.exit_code == 0
