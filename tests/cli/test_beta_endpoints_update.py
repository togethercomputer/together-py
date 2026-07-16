from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _endpoint_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ep_1",
        "projectId": "proj",
        "name": "my-project/my-endpoint",
        "endpointType": "ENDPOINT_TYPE_DEDICATED",
        "etag": "etag-1",
        "visibility": "VISIBILITY_PRIVATE",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "trafficSplit": [{"deploymentId": "dep_control", "weight": 1.0}],
        "deployments": [
            {
                "id": "dep_control",
                "name": "control",
                "model": "projects/proj/models/ml_control/revisions/latest",
                "modelId": "ml_control",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
            {
                "id": "dep_idle",
                "name": "idle",
                "model": "projects/proj/models/ml_idle/revisions/latest",
                "modelId": "ml_idle",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 0,
                "desiredReplicas": 0,
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 0, "maxReplicas": 0},
            },
        ],
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


def _update_args(*extra: str) -> list[str]:
    return ["beta", "endpoints", "update", "--project", "proj", *extra, "--json"]


def _mock_endpoint_list(respx_mock: MockRouter) -> None:
    respx_mock.get("/projects/proj/endpoints").mock(
        return_value=httpx.Response(
            200,
            json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
        )
    )


class TestBetaEndpointsUpdate:
    @pytest.mark.respx(base_url=base_url)
    def test_update_by_deployment_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_endpoint_list(respx_mock)
        route = respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )

        result = cli_runner.invoke(_update_args("dep_control", "--min-replicas", "1", "--max-replicas", "2"))

        assert result.exit_code == 0, result.output
        req = cast(Call, route.calls[0]).request
        assert "updateMask=autoscaling" in str(req.url)
        assert json.loads(req.content.decode()) == {
            "autoscaling": {"minReplicas": 1, "maxReplicas": 2},
        }

    @pytest.mark.respx(base_url=base_url)
    def test_update_idle_deployment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_endpoint_list(respx_mock)
        route = respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_idle").mock(
            return_value=httpx.Response(200, json=_deployment_body(id="dep_idle", name="idle"))
        )

        result = cli_runner.invoke(_update_args("dep_idle", "--min-replicas", "0", "--max-replicas", "0"))

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {
            "autoscaling": {"minReplicas": 0, "maxReplicas": 0},
        }

    @pytest.mark.respx(base_url=base_url)
    def test_update_unknown_deployment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_endpoint_list(respx_mock)

        result = cli_runner.invoke(_update_args("dep_missing", "--min-replicas", "2"))

        assert result.exit_code != 0
        assert "Deployment dep_missing not found" in result.output

    def test_update_requires_option(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "update", "--project", "proj", "dep_control"])
        assert result.exit_code != 0
        assert "At least one update option must be specified" in result.output
