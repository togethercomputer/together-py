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
from together.types.beta.endpoint import Endpoint
from together.lib.cli.api.beta.endpoints.ab import (
    calculate_ab_members,
    build_ab_experiment_name,
    verify_control_receiving_traffic,
)

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
                "name": "my-project/my-endpoint/control",
                "model": "projects/proj/models/ml_control/revisions/latest",
                "modelId": "ml_control",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "trafficMode": "TRAFFIC_MODE_LIVE",
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            }
        ],
    }
    body.update(overrides)
    return body


def _deployment_body(
    deployment_id: str = "dep_variant",
    name: str = "variant-dep",
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


def _ab_experiment_body(
    experiment_id: str = "abx_1",
    name: str = "my-project-my-endpoint-control-ab",
    members: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": experiment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": name,
        "members": members
        or [
            {
                "deploymentId": "dep_control",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                "percent": 95,
            },
            {
                "deploymentId": "dep_variant",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 5,
            },
        ],
        "createdAt": "2026-01-01T00:00:00Z",
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


def _ab_cli_args(**overrides: str) -> list[str]:
    args = [
        "beta",
        "endpoints",
        "ab",
        "--project",
        "proj",
        "--control",
        "dep_control",
        "--model",
        "ml_1",
        "--config",
        "cr_1",
        "--name",
        "variant-dep",
        "--percent",
        "5",
        "--json",
    ]
    for key, value in overrides.items():
        flag = f"--{key.replace('_', '-')}"
        if flag in args:
            index = args.index(flag)
            args[index + 1] = value
        else:
            args.extend([flag, value])
    return args


class TestBuildAbExperimentName:
    def test_replaces_slashes(self) -> None:
        assert build_ab_experiment_name("my-project/my-endpoint/control") == "my-project-my-endpoint-control-ab"


class TestCalculateAbMembers:
    def test_first_variant(self) -> None:
        members = calculate_ab_members(
            control_deployment_id="dep_control",
            new_deployment_id="dep_variant",
            new_percent=5,
        )
        assert members == [
            {"deployment_id": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 95},
            {"deployment_id": "dep_variant", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 5},
        ]

    def test_adds_second_variant(self) -> None:
        existing = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=95,
            ),
            AbMember.construct(
                deploymentId="dep_variant_1",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=5,
            ),
        ]
        members = calculate_ab_members(
            control_deployment_id="dep_control",
            new_deployment_id="dep_variant_2",
            new_percent=10,
            existing_members=existing,
        )
        assert members == [
            {"deployment_id": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 85},
            {"deployment_id": "dep_variant_1", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 5},
            {"deployment_id": "dep_variant_2", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 10},
        ]

    def test_rejects_control_below_minimum(self) -> None:
        existing = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=90,
            ),
            AbMember.construct(
                deploymentId="dep_variant_1",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=10,
            ),
        ]
        with pytest.raises(ValueError, match="minimum 1%"):
            calculate_ab_members(
                control_deployment_id="dep_control",
                new_deployment_id="dep_variant_2",
                new_percent=90,
                existing_members=existing,
            )


class TestVerifyControlReceivingTraffic:
    def test_accepts_control_in_traffic_split(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body())
        verify_control_receiving_traffic(endpoint, "dep_control")

    def test_rejects_missing_traffic_split(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body(trafficSplit=[]))
        with pytest.raises(ValueError, match="not receiving traffic"):
            verify_control_receiving_traffic(endpoint, "dep_control")

    def test_rejects_control_not_in_split(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body(trafficSplit=[{"deploymentId": "dep_other", "weight": 1.0}]))
        with pytest.raises(ValueError, match="not in the endpoint traffic split"):
            verify_control_receiving_traffic(endpoint, "dep_control")


class TestEndpointsAb:
    @pytest.mark.respx(base_url=base_url)
    def test_ab_creates_deployment_and_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(
                200,
                json=_deployment_body(deployment_id="dep_control", name="my-project/my-endpoint/control"),
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        create_experiment_route = respx_mock.post("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json=_ab_experiment_body(name="my-project-my-endpoint-control-ab"),
            )
        )

        result = cli_runner.invoke(_ab_cli_args())

        assert result.exit_code == 0, result.output

        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body == {
            "name": "variant-dep",
            "model": "projects/proj/models/ml_1",
            "config": "projects/proj/configs/cr_1",
            "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            "enableLora": False,
        }

        experiment_body = json.loads(cast(Call, create_experiment_route.calls[0]).request.content.decode())
        assert experiment_body == {
            "name": "my-project-my-endpoint-control-ab",
            "members": [
                {"deploymentId": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 95},
                {"deploymentId": "dep_variant", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 5},
            ],
        }

        output = json.loads(result.output)
        assert output["deployment"]["id"] == "dep_variant"
        assert output["ab_experiment"]["id"] == "abx_1"

    @pytest.mark.respx(base_url=base_url)
    def test_ab_updates_existing_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(
                200,
                json=_deployment_body(deployment_id="dep_control", name="my-project/my-endpoint/control"),
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _ab_experiment_body(
                            name="my-project-my-endpoint-control-ab",
                            etag="etag-1",
                            members=[
                                {
                                    "deploymentId": "dep_control",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                                    "percent": 95,
                                },
                                {
                                    "deploymentId": "dep_variant_1",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                                    "percent": 5,
                                },
                            ],
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body(deployment_id="dep_variant_2"))
        )
        update_experiment_route = respx_mock.patch("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(
                200,
                json=_ab_experiment_body(
                    members=[
                        {
                            "deploymentId": "dep_control",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                            "percent": 85,
                        },
                        {
                            "deploymentId": "dep_variant_1",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 5,
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

        result = cli_runner.invoke(_ab_cli_args(percent="10", name="variant-dep-2"))

        assert result.exit_code == 0, result.output
        update_url = str(cast(Call, update_experiment_route.calls[0]).request.url)
        assert "updateMask=members" in update_url
        experiment_body = json.loads(cast(Call, update_experiment_route.calls[0]).request.content.decode())
        assert experiment_body["members"] == [
            {"deploymentId": "dep_control", "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "percent": 85},
            {"deploymentId": "dep_variant_1", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 5},
            {"deploymentId": "dep_variant_2", "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT", "percent": 10},
        ]

    @pytest.mark.respx(base_url=base_url)
    def test_ab_rejects_control_without_traffic(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(trafficSplit=[])],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/deployments/dep_control").mock(
            return_value=httpx.Response(
                200,
                json=_deployment_body(deployment_id="dep_control", name="my-project/my-endpoint/control"),
            )
        )

        result = cli_runner.invoke(_ab_cli_args())

        assert result.exit_code != 0
        assert "not receiving traffic" in result.output
