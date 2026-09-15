from __future__ import annotations

import os
import json
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

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
        "trafficSplit": [],
        "deployments": [],
        "createdAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _rollout_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "rol_1",
        "createdAt": "2026-01-01T00:00:00Z",
        "endpointId": "ep_1",
        "sourceDeploymentId": "dep_source",
        "targetDeploymentId": "dep_target",
        "state": "ROLLOUT_STATE_PENDING",
        "strategy": "ROLLOUT_STRATEGY_TYPE_CANARY",
        "status": {
            "steps": [
                {
                    "stepIndex": 0,
                    "targetTrafficPercent": 25,
                    "state": "ROLLOUT_STEP_STATE_PENDING",
                }
            ],
            "totalSteps": 4,
            "updatedAt": "2026-01-01T00:00:00Z",
        },
        "etag": "etag-1",
    }
    body.update(overrides)
    return body


def _preview_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "sourceReplicas": 2,
        "targetMinReplicas": 0,
        "targetMaxReplicas": 4,
        "targetReplicas": 0,
        "warnings": [],
        "spec": {
            "sourceDeploymentId": "dep_source",
            "targetDeploymentId": "dep_target",
            "canary": {
                "stepInterval": "300s",
                "steps": [
                    {"traffic": 25, "replicas": 1},
                    {"traffic": 100, "replicas": 2},
                ],
            },
            "finalSourceReplicas": 0,
            "finalTargetReplicas": 2,
        },
        "estimatedEffectiveSteps": [
            {"traffic": 25, "replicas": 1},
            {"traffic": 100, "replicas": 2},
        ],
    }
    body.update(overrides)
    return body


class TestBetaEndpointRollouts:
    def test_rollouts_help_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "--help"])

        assert result.exit_code == 0
        assert "rollouts" in result.output
        assert "Manage endpoint deployment rollouts" in " ".join(result.output.split())

    @pytest.mark.respx(base_url=base_url)
    def test_create_sends_rollout_request_body(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "rollouts",
                "create",
                "ep_1",
                "--project",
                "proj",
                "--source-deployment",
                "dep_source",
                "--target-deployment",
                "dep_target",
                "--canary-step",
                "25:1",
                "--canary-step",
                "100:2",
                "--step-interval",
                "300s",
                "--final-source-replicas",
                "0",
                "--final-target-replicas",
                "2",
                "--metric",
                json.dumps(
                    {
                        "name": "router_latency",
                        "stat": "METRIC_STAT_TYPE_PERCENTILE",
                        "percentile": 95,
                        "thresholdCheck": {"operator": "THRESHOLD_OPERATOR_LT", "value": 30000},
                    }
                ),
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["id"] == "rol_1"
        request_body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert request_body == {
            "sourceDeploymentId": "dep_source",
            "targetDeploymentId": "dep_target",
            "canary": {
                "stepInterval": "300s",
                "steps": [
                    {"traffic": 25, "replicas": 1},
                    {"traffic": 100, "replicas": 2},
                ],
            },
            "finalSourceReplicas": 0,
            "finalTargetReplicas": 2,
            "metrics": [
                {
                    "name": "router_latency",
                    "stat": "METRIC_STAT_TYPE_PERCENTILE",
                    "percentile": 95,
                    "thresholdCheck": {"operator": "THRESHOLD_OPERATOR_LT", "value": 30000},
                }
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_create_can_start_rollout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )
        start_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_RUNNING"))
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "rollouts",
                "create",
                "ep_1",
                "--project",
                "proj",
                "--source-deployment",
                "dep_source",
                "--target-deployment",
                "dep_target",
                "--strategy",
                "blue-green",
                "--start",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert start_route.called
        assert json.loads(result.output)["state"] == "ROLLOUT_STATE_RUNNING"

    @pytest.mark.respx(base_url=base_url)
    def test_preview_defaults_uses_rollout_request_params(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        preview_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/preview-defaults").mock(
            return_value=httpx.Response(200, json=_preview_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "rollouts",
                "preview-defaults",
                "ep_1",
                "--project",
                "proj",
                "--source-deployment",
                "dep_source",
                "--target-deployment",
                "dep_target",
                "--strategy",
                "rolling",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["targetMaxReplicas"] == 4
        request_body = json.loads(cast(Call, preview_route.calls[0]).request.content.decode())
        assert request_body == {
            "sourceDeploymentId": "dep_source",
            "targetDeploymentId": "dep_target",
            "rolling": {},
        }

    @pytest.mark.respx(base_url=base_url)
    def test_list_sends_filter_and_pagination(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        list_route = respx_mock.get("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_rollout_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "rollouts",
                "ls",
                "ep_1",
                "--project",
                "proj",
                "--filter",
                "active",
                "--limit",
                "10",
                "--after",
                "tok",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        query = parse_qs(urlparse(str(cast(Call, list_route.calls[0]).request.url)).query)
        assert query["filter"] == ["ROLLOUT_FILTER_ACTIVE"]
        assert query["limit"] == ["10"]
        assert query["after"] == ["tok"]
        assert json.loads(result.output)["next_cursor"] == "next"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_rollout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        retrieve_route = respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(
            ["beta", "endpoints", "rollouts", "get", "ep_1", "rol_1", "--project", "proj", "--json"]
        )

        assert result.exit_code == 0, result.output
        assert retrieve_route.called
        assert json.loads(result.output)["id"] == "rol_1"

    @pytest.mark.respx(base_url=base_url)
    def test_pause_sends_reason_and_etag(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        pause_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/pause").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PAUSING"))
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "rollouts",
                "pause",
                "ep_1",
                "rol_1",
                "--project",
                "proj",
                "--reason",
                "checking metrics",
                "--etag",
                "etag-1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        request_body = json.loads(cast(Call, pause_route.calls[0]).request.content.decode())
        assert request_body == {"reason": "checking metrics", "etag": "etag-1"}
        assert json.loads(result.output)["state"] == "ROLLOUT_STATE_PAUSING"

    @pytest.mark.parametrize(
        ("command", "method", "path_suffix", "body"),
        [
            ("start", "POST", "start", None),
            ("resume", "POST", "resume", {"etag": "etag-1"}),
            ("promote", "POST", "promote", {"etag": "etag-1"}),
            ("cancel", "POST", "cancel", {"reason": "rollback", "disposition": "CANCEL_DISPOSITION_FREEZE"}),
            ("delete", "DELETE", "", None),
        ],
    )
    @pytest.mark.respx(base_url=base_url)
    def test_rollout_lifecycle_commands(
        self,
        command: str,
        method: str,
        path_suffix: str,
        body: dict[str, Any] | None,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        path = "/projects/proj/endpoints/ep_1/rollouts/rol_1"
        if path_suffix:
            path = f"{path}/{path_suffix}"
        route = respx_mock.request(method, path).mock(return_value=httpx.Response(200, json=_rollout_body()))

        args = ["beta", "endpoints", "rollouts", command, "ep_1", "rol_1", "--project", "proj", "--json"]
        if command in {"resume", "promote", "delete"}:
            args.extend(["--etag", "etag-1"])
        elif command == "cancel":
            args.extend(["--reason", "rollback", "--disposition", "freeze"])

        result = cli_runner.invoke(args)

        assert result.exit_code == 0, result.output
        assert route.called
        if body is not None:
            request_body = json.loads(cast(Call, route.calls[0]).request.content.decode())
            assert request_body == body
