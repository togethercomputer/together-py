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


def _endpoint_body(endpoint_id: str = "ep_1", name: str = "my-project/my-endpoint", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": endpoint_id,
        "projectId": "proj",
        "name": name,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "visibility": "VISIBILITY_PRIVATE",
        "endpointType": "ENDPOINT_TYPE_DEDICATED",
        "etag": "etag-1",
        "trafficSplit": [],
        "deployments": [],
    }
    body.update(overrides)
    return body


def _deployment_body(
    deployment_id: str = "dep_1",
    name: str = "my-dep",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": deployment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": name,
        "modelId": "ml_1",
        "configId": "cr_1",
        "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
        "createdAt": "2026-01-01T00:00:00Z",
        "status": {
            "state": "DEPLOYMENT_STATE_READY",
            "readyReplicas": 1,
            "message": "ready",
        },
    }
    body.update(overrides)
    return body


def _model_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ml_1",
        "projectId": "proj",
        "organizationId": "org-1",
        "name": "my-project/my-model",
        "baseModelId": "ml_base",
        "visibility": "VISIBILITY_PRIVATE",
        "weights": {"architecture": "llama", "type": "WEIGHTS_TYPE_DEFAULT"},
    }
    body.update(overrides)
    return body


def _config_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj",
        "referenceModel": "projects/proj/models/ml_1",
        "referenceModelId": "ml_1",
        "selectors": [{"key": "gpu", "value": "H100"}],
        "certifications": [],
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


def _mock_model_and_config(respx_mock: MockRouter) -> None:
    respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
    respx_mock.get("/projects/proj/configs").mock(
        return_value=httpx.Response(
            200,
            json={"object": "list", "data": [_config_body()], "next_cursor": None},
        )
    )


class TestBetaEndpointsDeploy:
    @pytest.mark.respx(base_url=base_url)
    def test_deploy_creates_endpoint_deployment_and_traffic_split(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        create_endpoint_route = respx_mock.post("/projects/proj/endpoints").mock(
            return_value=httpx.Response(200, json=_endpoint_body())
        )
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        update_endpoint_route = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[{"deploymentId": "dep_1", "weight": 1}],
                    deployments=[
                        {
                            "id": "dep_1",
                            "name": "my-dep",
                            "model": "projects/proj/models/ml_1/revisions/latest",
                            "modelId": "ml_1",
                            "hardware": "1x-h100",
                            "state": "DEPLOYMENT_STATE_READY",
                            "readyReplicas": 1,
                            "desiredReplicas": 1,
                            "createdAt": "2026-01-01T00:00:00Z",
                            "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                        }
                    ],
                ),
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "deploy",
                "--project",
                "proj",
                "--endpoint",
                "fresh-endpoint",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--deployment-name",
                "my-dep",
                "--traffic-weight",
                "1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert create_endpoint_route.call_count == 1
        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body["name"] == "my-dep"
        assert deployment_body["model"] == "projects/proj/models/ml_1"
        assert deployment_body["config"] == "projects/proj/configs/cr_1"
        assert deployment_body["autoscaling"] == {"minReplicas": 1, "maxReplicas": 1}
        update_body = json.loads(cast(Call, update_endpoint_route.calls[0]).request.content.decode())
        assert update_body["trafficSplit"] == [{"deploymentId": "dep_1", "weight": 1.0}]

    @pytest.mark.respx(base_url=base_url)
    def test_deploy_onto_existing_endpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "deploy",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--deployment-name",
                "my-dep",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert create_deployment_route.call_count == 1


class TestBetaEndpointsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_sends_cursor_pagination(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            ["beta", "endpoints", "ls", "--project", "proj", "--limit", "10", "--after", "tok", "--json"]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=10" in url
        assert "after=tok" in url
        assert json.loads(result.output)["next_cursor"] == "next"

    @pytest.mark.respx(base_url=base_url)
    def test_list_org_scoped(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        route = respx_mock.get("/organizations/org-1/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "ls", "--project", "proj", "--org", "--json"])

        assert result.exit_code == 0, result.output
        assert route.call_count == 1
        assert json.loads(result.output)["data"][0]["id"] == "ep_1"
