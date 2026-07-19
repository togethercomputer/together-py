from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.types.beta import AbMember
from together.lib.cli.api.beta.endpoints.rm import _members_without_deployment

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
                "name": "control",
                "model": "projects/proj/models/model-control/revisions/latest",
                "modelId": "model-control",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "trafficMode": "TRAFFIC_MODE_LIVE",
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
            {
                "id": "dep_variant",
                "name": "variant",
                "model": "projects/proj/models/model-variant/revisions/latest",
                "modelId": "model-variant",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "trafficMode": "TRAFFIC_MODE_LIVE",
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
            {
                "id": "dep_shadow",
                "name": "shadow",
                "model": "projects/proj/models/model-shadow/revisions/latest",
                "modelId": "model-shadow",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "trafficMode": "TRAFFIC_MODE_SHADOW",
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
        ],
        "createdAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _ab_experiment_body(
    experiment_id: str = "abx_1",
    members: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": experiment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "control-ab",
        "members": members
        or [
            {
                "deploymentId": "dep_control",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                "percent": 90,
            },
            {
                "deploymentId": "dep_variant",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 10,
            },
        ],
        "createdAt": "2026-01-01T00:00:00Z",
        "etag": "etag-ab",
    }
    body.update(overrides)
    return body


def _shadow_experiment_body(
    experiment_id: str = "exp_1",
    targets: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": experiment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "shadow-rate-0.1",
        "source": {"endpoint": {"sampling": {"uniform": {"rate": 0.1}}}},
        "targets": targets
        if targets is not None
        else [
            {
                "id": "target_1",
                "experimentId": experiment_id,
                "name": "shadow-target",
                "targetDeploymentId": "dep_shadow",
                "createdAt": "2026-01-01T00:00:00Z",
                "etag": "etag-target",
            }
        ],
        "createdAt": "2026-01-01T00:00:00Z",
        "state": "SHADOW_EXPERIMENT_STATE_ACTIVE",
        "etag": "etag-shadow",
    }
    body.update(overrides)
    return body


def _rm_args(resource_id: str, *extra: str) -> list[str]:
    return ["beta", "endpoints", "rm", "--project", "proj", resource_id, "--json", *extra]


class TestMembersWithoutDeployment:
    def test_returns_percent_to_control(self) -> None:
        members = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=90,
            ),
            AbMember.construct(
                deploymentId="dep_variant",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=10,
            ),
        ]
        assert _members_without_deployment(members, "dep_variant") == [
            {"deployment_id": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 100},
        ]


class TestBetaEndpointsRm:
    @pytest.mark.respx(base_url=base_url)
    def test_rm_endpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        delete_route = respx_mock.delete("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(200, json={"id": "ep_1"})
        )

        result = cli_runner.invoke(_rm_args("ep_1"))

        assert result.exit_code == 0, result.output
        assert delete_route.called
        payload = json.loads(result.out_out)
        assert payload["type"] == "endpoint"
        assert payload["id"] == "ep_1"

    @pytest.mark.respx(base_url=base_url)
    def test_rm_endpoint_blocked_by_deployments_prints_instructions(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.delete("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                400,
                json={"error": {"message": "endpoint has running deployments", "type": "invalid_request_error"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))

        result = cli_runner.invoke(["beta", "endpoints", "rm", "--project", "proj", "ep_1"])

        assert result.exit_code == 1
        assert "tg beta endpoints rm dep_control" in result.output
        assert "tg beta endpoints rm dep_variant" in result.output
        assert "tg beta endpoints rm dep_shadow" in result.output
        assert "tg beta endpoints rm ep_1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rm_endpoint_blocked_by_deployments_json(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.delete("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                400,
                json={"error": {"message": "endpoint has running deployments", "type": "invalid_request_error"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))

        result = cli_runner.invoke(_rm_args("ep_1"))

        assert result.exit_code == 1
        payload = json.loads(result.out_out)
        assert payload["id"] == "ep_1"
        assert {d["id"] for d in payload["deployments"]} == {"dep_control", "dep_variant", "dep_shadow"}
        assert all(d["command"].startswith("tg beta endpoints rm dep_") for d in payload["deployments"])

    @pytest.mark.respx(base_url=base_url)
    def test_rm_ab_experiment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        delete_route = respx_mock.delete("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(200, json={"id": "abx_1"})
        )

        result = cli_runner.invoke(_rm_args("abx_1"))

        assert result.exit_code == 0, result.output
        assert delete_route.called
        payload = json.loads(result.out_out)
        assert payload["type"] == "ab_experiment"

    @pytest.mark.respx(base_url=base_url)
    def test_rm_shadow_experiment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_shadow_experiment_body()], "next_cursor": None},
            )
        )
        delete_route = respx_mock.delete("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1").mock(
            return_value=httpx.Response(200, json={"id": "exp_1"})
        )

        result = cli_runner.invoke(_rm_args("exp_1"))

        assert result.exit_code == 0, result.output
        assert delete_route.called
        payload = json.loads(result.out_out)
        assert payload["type"] == "shadow_experiment"

    @pytest.mark.respx(base_url=base_url)
    def test_rm_shadow_deployment_deletes_empty_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_shadow_experiment_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        delete_target = respx_mock.delete(
            "/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets/target_1"
        ).mock(return_value=httpx.Response(200, json={"id": "target_1"}))
        delete_shadow = respx_mock.delete("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1").mock(
            return_value=httpx.Response(200, json={"id": "exp_1"})
        )
        delete_deployment = respx_mock.delete("/projects/proj/endpoints/ep_1/deployments/dep_shadow").mock(
            return_value=httpx.Response(200, json={"id": "dep_shadow"})
        )

        result = cli_runner.invoke(_rm_args("dep_shadow"))

        assert result.exit_code == 0, result.output
        assert delete_target.called
        assert delete_shadow.called
        assert delete_deployment.called
        payload = json.loads(result.out_out)
        assert payload["type"] == "deployment"
        assert any("deleted empty shadow experiment" in action for action in payload["actions"])

    @pytest.mark.respx(base_url=base_url)
    def test_rm_ab_variant_updates_members(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _endpoint_body(
                            trafficSplit=[
                                {"deploymentId": "dep_control", "weight": 1.0},
                                {"deploymentId": "dep_variant", "weight": 0.0},
                            ]
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _ab_experiment_body(
                            members=[
                                {
                                    "deploymentId": "dep_control",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                                    "percent": 85,
                                },
                                {
                                    "deploymentId": "dep_variant",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                                    "percent": 5,
                                },
                                {
                                    "deploymentId": "dep_variant_2",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                                    "percent": 10,
                                },
                            ]
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )
        update_ab = respx_mock.patch("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(
                200,
                json=_ab_experiment_body(
                    members=[
                        {
                            "deploymentId": "dep_control",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                            "percent": 90,
                        },
                        {
                            "deploymentId": "dep_variant_2",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 10,
                        },
                    ]
                ),
            )
        )
        update_endpoint = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(200, json=_endpoint_body())
        )
        delete_deployment = respx_mock.delete("/projects/proj/endpoints/ep_1/deployments/dep_variant").mock(
            return_value=httpx.Response(200, json={"id": "dep_variant"})
        )

        result = cli_runner.invoke(_rm_args("dep_variant"))

        assert result.exit_code == 0, result.output
        assert update_ab.called
        assert update_endpoint.called
        assert delete_deployment.called
        body = json.loads(cast(Call, update_ab.calls[0]).request.content.decode())
        assert body["members"] == [
            {"deploymentId": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 90},
            {"deploymentId": "dep_variant_2", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 10},
        ]
        payload = json.loads(result.out_out)
        assert any("removed from A/B experiment" in action for action in payload["actions"])

    @pytest.mark.respx(base_url=base_url)
    def test_rm_last_ab_variant_deletes_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        delete_ab = respx_mock.delete("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(200, json={"id": "abx_1"})
        )
        delete_deployment = respx_mock.delete("/projects/proj/endpoints/ep_1/deployments/dep_variant").mock(
            return_value=httpx.Response(200, json={"id": "dep_variant"})
        )

        result = cli_runner.invoke(_rm_args("dep_variant"))

        assert result.exit_code == 0, result.output
        assert delete_ab.called
        assert delete_deployment.called
        payload = json.loads(result.out_out)
        assert any("deleted A/B experiment" in action for action in payload["actions"])

    @pytest.mark.respx(base_url=base_url)
    def test_rm_deployment_scales_down_when_delete_requires_stop(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(200, json=_endpoint_body(trafficSplit=[]))
        )
        respx_mock.delete("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": {
                        "message": "deployment must be stopped before it can be deleted",
                        "type": "invalid_request_error",
                    }
                },
            )
        )
        update_route = respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "dep_control",
                    "projectId": "proj",
                    "endpointId": "ep_1",
                    "name": "control",
                    "modelId": "model-control",
                    "configId": "config-1",
                    "autoscaling": {"minReplicas": 0, "maxReplicas": 0},
                    "createdAt": "2026-01-01T00:00:00Z",
                    "status": {
                        "state": "DEPLOYMENT_STATE_STOPPING",
                        "readyReplicas": 1,
                        "message": "scaling down",
                    },
                },
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "rm", "--project", "proj", "dep_control"])

        assert result.exit_code == 1, result.output
        assert update_route.called
        body = json.loads(cast(Call, update_route.calls[0]).request.content.decode())
        assert body["autoscaling"] == {"minReplicas": 0, "maxReplicas": 0}
        assert "Scaled min/max replicas to 0" in result.output
        assert "tg beta endpoints rm dep_control" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rm_rejects_unknown_prefix(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rm_args("unknown_1"))
        assert result.exit_code != 0
        assert "Unrecognized resource ID" in result.output
