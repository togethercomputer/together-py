from __future__ import annotations

import os
import json
from typing import Any

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _endpoint_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ep_1",
        "projectId": "proj",
        "name": "my-project/my-endpoint",
        "trafficSplit": [{"deploymentId": "dep_control", "weight": 1.0}],
        "deployments": [
            {
                "id": "dep_control",
                "name": "my-project/my-endpoint/control",
                "model": "projects/proj/models/ml_control/revisions/latest",
                "modelId": "ml_control",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            }
        ],
        "createdAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _deployment_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "dep_control",
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "control",
        "modelId": "ml_control",
        "configId": "cr_1",
        "autoscaling": {"minReplicas": 1, "maxReplicas": 2},
        "createdAt": "2026-01-01T00:00:00Z",
        "status": {
            "state": "DEPLOYMENT_STATE_READY",
            "readyReplicas": 1,
            "message": "ready",
        },
    }
    body.update(overrides)
    return body


def _whoami_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "api_key_id": "key-1",
        "organization_id": "org-1",
        "organization_name": "Acme",
        "project_id": "proj",
        "project_name": "My Project",
        "project_slug": "my-project",
        "user_id": "user-1",
    }
    body.update(overrides)
    return body


def _mock_endpoint_get_side_resources(respx_mock: MockRouter) -> None:
    respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
    )
    respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
    )


class TestBetaEndpointsRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_deployment_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )

        result = cli_runner.invoke(["beta", "endpoints", "retrieve", "dep_control", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "dep_control"
        assert payload["endpointId"] == "ep_1"

    @pytest.mark.respx(base_url=base_url)
    def test_implicit_retrieve_deployment_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )

        result = cli_runner.invoke(["beta", "endpoints", "dep_control", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "dep_control"
        assert payload["endpointId"] == "ep_1"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_endpoint_by_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        _mock_endpoint_get_side_resources(respx_mock)

        result = cli_runner.invoke(["beta", "endpoints", "get", "my-endpoint", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "ep_1"
        assert payload["name"] == "my-project/my-endpoint"

    @pytest.mark.respx(base_url=base_url)
    def test_implicit_retrieve_endpoint_by_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        _mock_endpoint_get_side_resources(respx_mock)

        result = cli_runner.invoke(["beta", "endpoints", "my-endpoint", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "ep_1"
        assert payload["name"] == "my-project/my-endpoint"

    @pytest.mark.respx(base_url=base_url)
    def test_implicit_retrieve_deployment_by_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        # Name lookup as endpoint fails (no matching endpoint), then deployment name resolves.
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )

        result = cli_runner.invoke(["beta", "endpoints", "control", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "dep_control"
        assert payload["endpointId"] == "ep_1"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_deployment_by_ambiguous_name_errors(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        other = _endpoint_body(
            id="ep_2",
            name="my-project/other-endpoint",
            trafficSplit=[{"deploymentId": "dep_other", "weight": 1.0}],
            deployments=[
                {
                    "id": "dep_other",
                    "name": "my-project/other-endpoint/control",
                    "model": "projects/proj/models/ml_control/revisions/latest",
                    "modelId": "ml_control",
                    "hardware": "1x-h100",
                    "state": "DEPLOYMENT_STATE_READY",
                    "readyReplicas": 1,
                    "desiredReplicas": 1,
                    "createdAt": "2026-01-01T00:00:00Z",
                    "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                }
            ],
        )
        # Endpoint name lookup: neither endpoint is named "control".
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body(), other], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "control", "--project", "proj", "--json"])

        assert result.exit_code != 0
        assert 'Multiple deployments found for "control"' in json.loads(result.output)["error"]
