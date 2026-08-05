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
from together.lib.cli.api.beta.endpoints._utils._ab_experiments import build_ab_members_with_percent

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
            {
                "id": "dep_variant",
                "name": "variant",
                "model": "projects/proj/models/ml_variant/revisions/latest",
                "modelId": "ml_variant",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
            {
                "id": "dep_other",
                "name": "other",
                "model": "projects/proj/models/ml_other/revisions/latest",
                "modelId": "ml_other",
                "hardware": "1x-h100",
                "state": "DEPLOYMENT_STATE_READY",
                "readyReplicas": 1,
                "desiredReplicas": 1,
                "createdAt": "2026-01-01T00:00:00Z",
                "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            },
        ],
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
                "percent": 85,
            },
            {
                "deploymentId": "dep_variant",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 5,
            },
            {
                "deploymentId": "dep_other",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 10,
            },
        ],
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "createdBy": "user_1",
        "etag": "etag-ab",
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

    @pytest.mark.parametrize("flag", ["--min-replicas", "--max-replicas"])
    def test_update_stop_requires_both_zero_bounds(self, cli_runner: CliRunner, flag: str) -> None:
        result = cli_runner.invoke(_update_args("dep_idle", flag, "0"))

        assert result.exit_code != 0
        assert "pass both --min-replicas 0 and --max-replicas 0" in result.output.replace("\n", " ")

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

    def test_update_does_not_accept_name_option(self, cli_runner: CliRunner) -> None:
        help_result = cli_runner.invoke(["beta", "endpoints", "update", "--help"])
        assert help_result.exit_code == 0, help_result.output
        assert "--name" not in help_result.output

        result = cli_runner.invoke(_update_args("dep_control", "--name", "renamed"))
        assert result.exit_code != 0

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_counts_as_update_option(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # Prove --ab-percent clears the "at least one option" guard by reaching
        # deployment lookup (not by asserting the absence of an error string).
        _mock_endpoint_list(respx_mock)

        result = cli_runner.invoke(_update_args("dep_missing", "--ab-percent", "20"))

        assert result.exit_code != 0
        assert "At least one update option must be specified" not in result.output
        assert "Deployment dep_missing not found" in result.output


class TestUpdateAbMemberPercent:
    def test_increase_takes_from_control_only(self) -> None:
        members = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=85,
            ),
            AbMember.construct(
                deploymentId="dep_variant",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=5,
            ),
            AbMember.construct(
                deploymentId="dep_other",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=10,
            ),
        ]

        updated = build_ab_members_with_percent(members, "dep_variant", 20)

        assert updated == [
            {
                "deployment_id": "dep_control",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                "percent": 70,
            },
            {
                "deployment_id": "dep_variant",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 20,
            },
            {
                "deployment_id": "dep_other",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 10,
            },
        ]

    def test_decrease_returns_to_control_only(self) -> None:
        members = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=85,
            ),
            AbMember.construct(
                deploymentId="dep_variant",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=10,
            ),
            AbMember.construct(
                deploymentId="dep_other",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=5,
            ),
        ]

        updated = build_ab_members_with_percent(members, "dep_variant", 2)

        assert updated == [
            {
                "deployment_id": "dep_control",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                "percent": 93,
            },
            {
                "deployment_id": "dep_variant",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 2,
            },
            {
                "deployment_id": "dep_other",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 5,
            },
        ]

    def test_rejects_control_member(self) -> None:
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

        with pytest.raises(ValueError, match="can only update variant deployments"):
            build_ab_members_with_percent(members, "dep_control", 80)

    def test_rejects_control_below_minimum(self) -> None:
        members = [
            AbMember.construct(
                deploymentId="dep_control",
                role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                percent=10,
            ),
            AbMember.construct(
                deploymentId="dep_variant",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=80,
            ),
            AbMember.construct(
                deploymentId="dep_other",
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=10,
            ),
        ]

        with pytest.raises(ValueError, match="control would be 0%"):
            build_ab_members_with_percent(members, "dep_variant", 90)


class TestBetaEndpointsUpdateAbPercent:
    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_increases_variant_takes_from_control(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
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
                            "percent": 70,
                        },
                        {
                            "deploymentId": "dep_variant",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 20,
                        },
                        {
                            "deploymentId": "dep_other",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 10,
                        },
                    ]
                ),
            )
        )

        result = cli_runner.invoke(_update_args("dep_variant", "--ab-percent", "20"))

        assert result.exit_code == 0, result.output
        req = cast(Call, update_ab.calls[0]).request
        assert "updateMask=members" in str(req.url)
        assert json.loads(req.content.decode()) == {
            "etag": "etag-ab",
            "members": [
                {
                    "deploymentId": "dep_control",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                    "percent": 70,
                },
                {
                    "deploymentId": "dep_variant",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                    "percent": 20,
                },
                {
                    "deploymentId": "dep_other",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                    "percent": 10,
                },
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_decreases_variant_returns_to_control(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
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
                                    "percent": 10,
                                },
                                {
                                    "deploymentId": "dep_other",
                                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                                    "percent": 5,
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
                            "percent": 93,
                        },
                        {
                            "deploymentId": "dep_variant",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 2,
                        },
                        {
                            "deploymentId": "dep_other",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 5,
                        },
                    ]
                ),
            )
        )

        result = cli_runner.invoke(_update_args("dep_variant", "--ab-percent", "2"))

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, update_ab.calls[0]).request.content.decode()) == {
            "etag": "etag-ab",
            "members": [
                {
                    "deploymentId": "dep_control",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                    "percent": 93,
                },
                {
                    "deploymentId": "dep_variant",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                    "percent": 2,
                },
                {
                    "deploymentId": "dep_other",
                    "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                    "percent": 5,
                },
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_ignores_user_etag_for_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        update_dep = respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_variant").mock(
            return_value=httpx.Response(200, json=_deployment_body(id="dep_variant", name="renamed"))
        )
        update_ab = respx_mock.patch("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(200, json=_ab_experiment_body())
        )

        result = cli_runner.invoke(
            _update_args(
                "dep_variant",
                "--min-replicas",
                "1",
                "--max-replicas",
                "2",
                "--ab-percent",
                "20",
                "--etag",
                "user-etag",
            )
        )

        assert result.exit_code == 0, result.output
        dep_body = json.loads(cast(Call, update_dep.calls[0]).request.content.decode())
        ab_body = json.loads(cast(Call, update_ab.calls[0]).request.content.decode())
        assert dep_body["etag"] == "user-etag"
        assert ab_body["etag"] == "etag-ab"

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_errors_when_not_in_ab_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(_update_args("dep_variant", "--ab-percent", "20"))

        assert result.exit_code != 0
        assert "Deployment dep_variant is not part of an A/B experiment" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_validates_before_mutations(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [], "next_cursor": None},
            )
        )
        # Intentionally not mocking the deployment PATCH: if validation ran after
        # mutations, that call would be an unmocked request and fail the test.

        result = cli_runner.invoke(
            _update_args(
                "dep_variant",
                "--min-replicas",
                "1",
                "--max-replicas",
                "2",
                "--ab-percent",
                "20",
            )
        )

        assert result.exit_code != 0
        assert "Deployment dep_variant is not part of an A/B experiment" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_rejects_control_member(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(_update_args("dep_control", "--ab-percent", "80"))

        assert result.exit_code != 0
        assert "can only update variant deployments" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_noop_skips_patch(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        # Intentionally not mocking the AB PATCH: a no-op must not issue one.

        result = cli_runner.invoke(_update_args("dep_variant", "--ab-percent", "5"))

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["ab_experiment"]["id"] == "abx_1"
        assert "deployment" not in payload

    @pytest.mark.respx(base_url=base_url)
    def test_update_ab_percent_json_wraps_payload(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_variant").mock(
            return_value=httpx.Response(200, json=_deployment_body(id="dep_variant", name="renamed"))
        )
        respx_mock.patch("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(
                200,
                json=_ab_experiment_body(
                    members=[
                        {
                            "deploymentId": "dep_control",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                            "percent": 70,
                        },
                        {
                            "deploymentId": "dep_variant",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 20,
                        },
                        {
                            "deploymentId": "dep_other",
                            "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                            "percent": 10,
                        },
                    ]
                ),
            )
        )

        result = cli_runner.invoke(
            _update_args(
                "dep_variant",
                "--min-replicas",
                "1",
                "--max-replicas",
                "2",
                "--ab-percent",
                "20",
            )
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert set(payload.keys()) == {"deployment", "ab_experiment"}
        assert payload["deployment"]["id"] == "dep_variant"
        assert payload["ab_experiment"]["id"] == "abx_1"

    @pytest.mark.respx(base_url=base_url)
    def test_update_autoscaling_and_traffic_weight_json_keeps_unwrapped_deployment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint_list(respx_mock)
        respx_mock.patch("/projects/proj/endpoints/ep_1/deployments/dep_variant").mock(
            return_value=httpx.Response(200, json=_deployment_body(id="dep_variant", name="renamed"))
        )
        respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[
                        {"deploymentId": "dep_control", "weight": 1.0},
                        {"deploymentId": "dep_variant", "weight": 2.0},
                    ]
                ),
            )
        )

        result = cli_runner.invoke(
            _update_args(
                "dep_variant",
                "--min-replicas",
                "1",
                "--max-replicas",
                "2",
                "--traffic-weight",
                "2",
            )
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        # Pre--ab-percent precedence: bare deployment object, not a wrapped multi-key payload.
        assert payload["id"] == "dep_variant"
        assert "deployment" not in payload
        assert "endpoint" not in payload
