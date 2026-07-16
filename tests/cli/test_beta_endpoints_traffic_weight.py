from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.types.beta import EndpointTrafficSplitEntry
from together.lib.cli.api.beta.endpoints._utils._traffic_split import upsert_traffic_weight

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _endpoint_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ep_1",
        "projectId": "proj",
        "name": "my-project/my-endpoint",
        "trafficSplit": [{"deploymentId": "dep_existing", "weight": 2.0}],
        "deployments": [
            {
                "id": "dep_existing",
                "name": "existing",
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
        "createdAt": "2026-01-01T00:00:00Z",
        "etag": "etag-1",
    }
    body.update(overrides)
    return body


def _deployment_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "dep_new",
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "new-dep",
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
        "name": "my-project/my-model",
        "baseModelId": "base-model",
        "visibility": "VISIBILITY_PRIVATE",
    }
    body.update(overrides)
    return body


def _config_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj",
        "referenceModelId": "ml_1",
        "selectors": [{"key": "gpu", "value": "H100"}],
    }
    body.update(overrides)
    return body


def _entry(deployment_id: str, weight: float) -> EndpointTrafficSplitEntry:
    return EndpointTrafficSplitEntry.construct(deploymentId=deployment_id, weight=weight)


class TestUpsertTrafficWeight:
    def test_adds_to_empty_split(self) -> None:
        assert upsert_traffic_weight(None, deployment_id="dep_a", weight=1.0) == [
            {"deployment_id": "dep_a", "weight": 1.0}
        ]
        assert upsert_traffic_weight([], deployment_id="dep_a", weight=1.0) == [
            {"deployment_id": "dep_a", "weight": 1.0}
        ]

    def test_preserves_existing_weights_when_adding(self) -> None:
        existing = [_entry("dep_a", 2.0), _entry("dep_b", 3.0)]
        assert upsert_traffic_weight(existing, deployment_id="dep_c", weight=1.0) == [
            {"deployment_id": "dep_a", "weight": 2.0},
            {"deployment_id": "dep_b", "weight": 3.0},
            {"deployment_id": "dep_c", "weight": 1.0},
        ]

    def test_updates_existing_deployment_weight(self) -> None:
        existing = [_entry("dep_a", 2.0), _entry("dep_b", 3.0)]
        assert upsert_traffic_weight(existing, deployment_id="dep_b", weight=5.0) == [
            {"deployment_id": "dep_a", "weight": 2.0},
            {"deployment_id": "dep_b", "weight": 5.0},
        ]

    def test_allows_zero_weight(self) -> None:
        existing = [_entry("dep_a", 2.0)]
        assert upsert_traffic_weight(existing, deployment_id="dep_a", weight=0.0) == [
            {"deployment_id": "dep_a", "weight": 0.0}
        ]

    def test_rejects_negative_weight(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            upsert_traffic_weight([], deployment_id="dep_a", weight=-1.0)


def _mock_model_and_config(respx_mock: MockRouter) -> None:
    respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
    respx_mock.get("/projects/proj/configs").mock(
        return_value=httpx.Response(
            200,
            json={"object": "list", "data": [_config_body()], "next_cursor": None},
        )
    )


class TestDeployTrafficWeight:
    @pytest.mark.respx(base_url=base_url)
    def test_deploy_new_endpoint_sets_traffic_weight(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.post("/projects/proj/endpoints").mock(
            return_value=httpx.Response(200, json=_endpoint_body(trafficSplit=[], deployments=[], etag="etag-new"))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        update_route = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[{"deploymentId": "dep_new", "weight": 1.0}],
                    deployments=[_deployment_body()],
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
                "new-dep",
                "--traffic-weight",
                "1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        req = cast(Call, update_route.calls[0]).request
        assert "updateMask=trafficSplit" in str(req.url)
        assert json.loads(req.content.decode()) == {
            "etag": "etag-new",
            "trafficSplit": [{"deploymentId": "dep_new", "weight": 1.0}],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_deploy_existing_endpoint_preserves_other_weights(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        update_route = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[
                        {"deploymentId": "dep_existing", "weight": 2.0},
                        {"deploymentId": "dep_new", "weight": 1.0},
                    ]
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
                "ep_1",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--deployment-name",
                "new-dep",
                "--traffic-weight",
                "1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, update_route.calls[0]).request.content.decode()) == {
            "etag": "etag-1",
            "trafficSplit": [
                {"deploymentId": "dep_existing", "weight": 2.0},
                {"deploymentId": "dep_new", "weight": 1.0},
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_deploy_without_traffic_weight_skips_traffic_update(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
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
                "new-dep",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output


class TestUpdateTrafficWeight:
    @pytest.mark.respx(base_url=base_url)
    def test_update_traffic_weight_preserves_other_deployments(
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
                                {"deploymentId": "dep_existing", "weight": 2.0},
                                {"deploymentId": "dep_new", "weight": 1.0},
                            ],
                            deployments=[
                                {
                                    "id": "dep_existing",
                                    "name": "existing",
                                    "model": "projects/proj/models/ml_1/revisions/latest",
                                    "modelId": "ml_1",
                                    "hardware": "1x-h100",
                                    "state": "DEPLOYMENT_STATE_READY",
                                    "readyReplicas": 1,
                                    "desiredReplicas": 1,
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                                },
                                {
                                    "id": "dep_new",
                                    "name": "new-dep",
                                    "model": "projects/proj/models/ml_1/revisions/latest",
                                    "modelId": "ml_1",
                                    "hardware": "1x-h100",
                                    "state": "DEPLOYMENT_STATE_READY",
                                    "readyReplicas": 1,
                                    "desiredReplicas": 1,
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                                },
                            ],
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )
        update_route = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[
                        {"deploymentId": "dep_existing", "weight": 2.0},
                        {"deploymentId": "dep_new", "weight": 4.0},
                    ]
                ),
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "update",
                "--project",
                "proj",
                "dep_new",
                "--traffic-weight",
                "4",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        req = cast(Call, update_route.calls[0]).request
        assert "updateMask=trafficSplit" in str(req.url)
        assert json.loads(req.content.decode()) == {
            "etag": "etag-1",
            "trafficSplit": [
                {"deploymentId": "dep_existing", "weight": 2.0},
                {"deploymentId": "dep_new", "weight": 4.0},
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_update_traffic_weight_can_add_missing_deployment(
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
                            trafficSplit=[{"deploymentId": "dep_existing", "weight": 2.0}],
                            deployments=[
                                {
                                    "id": "dep_existing",
                                    "name": "existing",
                                    "model": "projects/proj/models/ml_1/revisions/latest",
                                    "modelId": "ml_1",
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
                                    "model": "projects/proj/models/ml_1/revisions/latest",
                                    "modelId": "ml_1",
                                    "hardware": "1x-h100",
                                    "state": "DEPLOYMENT_STATE_READY",
                                    "readyReplicas": 0,
                                    "desiredReplicas": 0,
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "autoscaling": {"minReplicas": 0, "maxReplicas": 0},
                                },
                            ],
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )
        update_route = respx_mock.patch("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    trafficSplit=[
                        {"deploymentId": "dep_existing", "weight": 2.0},
                        {"deploymentId": "dep_idle", "weight": 1.0},
                    ]
                ),
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "update",
                "--project",
                "proj",
                "dep_idle",
                "--traffic-weight",
                "1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, update_route.calls[0]).request.content.decode()) == {
            "etag": "etag-1",
            "trafficSplit": [
                {"deploymentId": "dep_existing", "weight": 2.0},
                {"deploymentId": "dep_idle", "weight": 1.0},
            ],
        }

    def test_update_traffic_weight_counts_as_update_option(self, cli_runner: CliRunner) -> None:
        # Without mocks this still needs an option; traffic-weight alone should pass arg validation.
        # It will fail later looking up the deployment — that's fine, proves the option is accepted.
        result = cli_runner.invoke(
            ["beta", "endpoints", "update", "--project", "proj", "dep_missing", "--traffic-weight", "1"]
        )
        assert "At least one update option must be specified" not in result.output
