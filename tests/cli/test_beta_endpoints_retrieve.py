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


def _rollout_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "rol_1",
        "projectId": "proj",
        "endpointId": "ep_1",
        "sourceDeploymentId": "dep_control",
        "targetDeploymentId": "dep_target",
        "state": "ROLLOUT_STATE_RUNNING",
        "strategy": "ROLLOUT_STRATEGY_TYPE_CANARY",
        "createdAt": "2026-01-01T00:00:00Z",
        "startedAt": "2026-01-01T00:01:00Z",
        "currentStep": 1,
        "currentTrafficPercent": 50,
        "etag": "etag-rol",
        "status": {"totalSteps": 3, "steps": []},
    }
    body.update(overrides)
    return body


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
    def test_retrieve_endpoint_includes_active_rollout(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(activeRolloutId="rol_1")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(200, json=_endpoint_body(activeRolloutId="rol_1"))
        )
        _mock_endpoint_get_side_resources(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "my-endpoint", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "ep_1"
        assert payload["rollout"]["id"] == "rol_1"
        assert payload["rollout"]["currentStep"] == 1
        assert payload["rollout"]["currentTrafficPercent"] == 50

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_rollout_id(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(activeRolloutId="rol_1")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "rol_1", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "rol_1"
        assert payload["endpointId"] == "ep_1"
        assert payload["currentStep"] == 1

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_rollout_surfaces_system_pause_reason(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        paused = _rollout_body(
            state="ROLLOUT_STATE_SYSTEM_PAUSED",
            status={
                "totalSteps": 3,
                "steps": [],
                "condition": {
                    "category": "ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
                    "message": "latency p99 breached",
                    "atStep": 1,
                    "metrics": [
                        {
                            "name": "request_latency",
                            "stat": "METRIC_STAT_TYPE_PERCENTILE",
                            "percentile": 99,
                            "check": "METRIC_CHECK_TYPE_REGRESSION",
                            "sourceValue": 120.0,
                            "targetValue": 150.0,
                            "maxRegressionPercent": 10.0,
                            "verdict": "METRIC_VERDICT_BREACHED",
                        }
                    ],
                },
            },
            pauseInfo={"pausedAt": "2026-01-01T00:02:00Z", "reason": "System paused after metric gate failed"},
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(activeRolloutId="rol_1")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(200, json=paused)
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "rol_1", "--project", "proj"])

        assert result.exit_code == 0, result.output
        assert "System Paused" in result.output
        assert "Metric Regression" in result.output
        assert "latency p99 breached" in result.output
        assert "request_latency p99" in result.output
        assert "Breached" in result.output
        assert "System paused after metric gate failed" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_rollout_surfaces_step_metric_gate(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        failed = _rollout_body(
            state="ROLLOUT_STATE_CANCELED",
            strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
            currentStep=1,
            currentTrafficPercent=100,
            status={
                "totalSteps": 2,
                "steps": [
                    {"stepIndex": 0, "state": "ROLLOUT_STEP_STATE_PASSED", "targetTrafficPercent": 10},
                    {
                        "stepIndex": 1,
                        "state": "ROLLOUT_STEP_STATE_FAILED",
                        "targetTrafficPercent": 100,
                        "failureReason": (
                            "metrics-unavailable: serving_latency target: insufficient samples (87 < 100)"
                        ),
                        "metrics": [
                            {
                                "name": "serving_latency",
                                "stat": "METRIC_STAT_TYPE_AVG",
                                "check": "METRIC_CHECK_TYPE_THRESHOLD",
                                "sourceValue": 80.0,
                                "targetValue": 95.0,
                                "threshold": 100.0,
                                "operator": "THRESHOLD_OPERATOR_LT",
                                "verdict": "METRIC_VERDICT_UNAVAILABLE",
                            }
                        ],
                    },
                ],
            },
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(activeRolloutId="rol_1")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(200, json=failed)
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "rol_1", "--project", "proj"])

        assert result.exit_code == 0, result.output
        # Rich wraps long lines; collapse whitespace so `87 < 100` still matches.
        output = " ".join(result.output.split())
        assert "Canceled" in output
        assert "2/2" in output
        assert "Failed" in output
        assert "Passed" in output
        assert "insufficient samples (87 < 100)" in output
        assert "serving_latency" in output
        assert "source=80" in output
        assert "value=95" in output
        assert "threshold < 100" in output
        assert "Unavailable" in output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_rollout_falls_back_to_find_rollout(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # Completed/stale rollout: no activeRolloutId match, full endpoint×rollout scan.
        stale = _rollout_body(id="rol_stale", state="ROLLOUT_STATE_COMPLETED", currentStep=2)
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [stale], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "get", "rol_stale", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "rol_stale"
        assert payload["state"] == "ROLLOUT_STATE_COMPLETED"

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
