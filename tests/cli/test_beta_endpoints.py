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
        "selectors": [
            {"key": "accelerator_count", "value": "1"},
            {"key": "accelerator_type", "value": "nvidia-h100-80gb"},
        ],
        "certifications": [],
    }
    body.update(overrides)
    return body


def _hardware_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "it_h100",
        "name": "1xnvidia-h100-80gb",
        "description": "1x NVIDIA H100 80GB",
        "gpuCount": 1,
        "gpuMemoryGib": 80,
        "gpuType": "NVIDIA-H100-80GB-HBM3",
        "priceCentsPerHour": 2400,
        "regions": [],
    }
    body.update(overrides)
    return body


def _mock_hardware_catalog(respx_mock: MockRouter) -> None:
    # Tests override TOGETHER_BASE_URL, so the SDK hits the relative public path.
    respx_mock.get("/public/inference-instance-types").mock(
        return_value=httpx.Response(
            200,
            json={"object": "list", "data": [_hardware_body()], "next_cursor": None},
        )
    )


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


def _event_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "evt_1",
        "createdAt": "2026-01-01T00:00:00Z",
        "endpointId": "ep_1",
        "level": "LEVEL_INFO",
        "source": "endpoint-controller",
        "sourceKind": "SOURCE_KIND_ENDPOINT",
        "type": "endpoint.updated",
        "message": "Endpoint updated",
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
    @pytest.mark.parametrize("model_revision", ["rev_in_path", "rev_from_flag"])
    def test_deploy_rejects_model_path_and_revision_flag(
        self,
        cli_runner: CliRunner,
        model_revision: str,
    ) -> None:
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
                "projects/proj/models/ml_1/revisions/rev_in_path",
                "--model-revision",
                model_revision,
                "--config",
                "cr_1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        assert "Do not pass --model-revision when --model already includes a revision" in result.output

    def test_deploy_help_omits_scale_to_zero_window(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "deploy", "--help"])

        output = " ".join(result.output.replace("│", " ").split())
        assert result.exit_code == 0
        assert "--scale-up-window" in output
        assert "--scale-down-window" in output
        assert "--scale-to-zero-window" not in output

    def test_deploy_rejects_scale_to_zero_window(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "deploy", "--scale-to-zero-window"])

        assert result.exit_code != 0
        assert "Unknown option" in result.output
        assert "--scale-to-zero-window" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_deploy_ignores_leftover_scale_to_zero_window(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
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
                "--scale-to-zero-window",
                "300s",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert "scaleToZeroWindow" not in deployment_body.get("autoscaling", {})
        assert "scale_to_zero_window" not in deployment_body.get("autoscaling", {})

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
                            "estimatedEffectiveTrafficShare": 1,
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
    def test_deploy_preview_shows_gpu_and_estimated_price_before_project_confirm(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # Interactive project confirm only runs when --project / env are omitted.
        cli_runner.env.pop("TOGETHER_PROJECT_ID", None)
        _mock_model_and_config(respx_mock)
        _mock_hardware_catalog(respx_mock)
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "deploy",
                "--endpoint",
                "fresh-endpoint",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--deployment-name",
                "my-dep",
                "--min-replicas",
                "1",
                "--max-replicas",
                "2",
                "--non-interactive",
            ]
        )

        # Non-interactive mode without an explicit project aborts at confirm —
        # after the deploy preview has already shown GPU + estimated price.
        # Collapse Rich line-wrap whitespace so phrase checks stay stable.
        output = " ".join(result.output.split())
        assert result.exit_code != 0
        assert "Deploy" in output
        assert "preview" in output
        assert "This deployment will utilize 1x H100" in output
        assert "estimated to cost approximately" in output
        assert "$24.00/hr - $48.00/hr" in output
        assert "Project argument is required" in output
        assert not any(call.request.method == "POST" for call in cast(list[Call], respx_mock.calls))

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

    @pytest.mark.respx(base_url=base_url)
    def test_deploy_reuses_endpoint_when_name_already_exists(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        _mock_model_and_config(respx_mock)
        respx_mock.post("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                409,
                json={
                    "code": 6,
                    "message": "Already Exists",
                    "details": [
                        {
                            "@type": "type.googleapis.com/common.errors.v1.ProblemDetail",
                            "type": "https://api.together.ai/problems/already-exists",
                            "title": "Already Exists",
                            "status": 409,
                            "detail": "Already Exists",
                        }
                    ],
                },
            )
        )
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        list_route = respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_endpoint_body(name="my-project/test")],
                    "next_cursor": None,
                },
            )
        )
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
                "test",
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
        assert "filter=name%3D%22test%22" in str(cast(Call, list_route.calls[0]).request.url)


class TestBetaEndpointsList:
    def test_list_alias_is_hidden_from_help(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "--help"])

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        # Agent formatter: "ls: …"; human/Rich formatter: "ls …" (no colon).
        assert "List project, organization, or public endpoints" in output
        assert (
            "ls: List project, organization, or public endpoints" in output
            or "ls List project, organization, or public endpoints" in output
        )
        assert "list: List project, organization, or public endpoints" not in output
        assert "list List project, organization, or public endpoints" not in output

    @pytest.mark.parametrize("command", ["list", "ls"])
    @pytest.mark.respx(base_url=base_url)
    def test_list_sends_cursor_pagination(self, command: str, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            ["beta", "endpoints", command, "--project", "proj", "--limit", "10", "--after", "tok", "--json"]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=10" in url
        assert "after=tok" in url
        assert json.loads(result.output)["next_cursor"] == "next"

    @pytest.mark.respx(base_url=base_url)
    def test_list_handles_deployment_without_hardware(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        # List only resolves model display names; it does not fetch configs.
        respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _endpoint_body(
                            deployments=[
                                {
                                    "id": "dep_1",
                                    "name": "my-project/my-endpoint/my-dep",
                                    "model": "projects/proj/models/ml_1/revisions/latest",
                                    "modelId": "ml_1",
                                    "estimatedEffectiveTrafficShare": 1,
                                    "state": "DEPLOYMENT_STATE_READY",
                                    "readyReplicas": 1,
                                    "desiredReplicas": 1,
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                                }
                            ],
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "ls", "--project", "proj"])

        assert result.exit_code == 0, result.output

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


class TestBetaEndpointsListEvents:
    @pytest.mark.respx(base_url=base_url)
    def test_events_sends_sdk_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))
        route = respx_mock.get("/projects/proj/endpoints/ep_1/events").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_event_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "events",
                "ep_1",
                "--project",
                "proj",
                "--limit",
                "10000",
                "--after",
                "tok",
                "--deployment-ids",
                "dep_1,dep_2",
                "--min-level",
                "warn",
                "--since",
                "2026-01-01T00:00:00+00:00",
                "--subject-id",
                "rollout_1",
                "--types",
                "deployment.scaled,condition.set",
                "--until",
                "2026-01-02T00:00:00+00:00",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        query = parse_qs(urlparse(str(cast(Call, route.calls[0]).request.url)).query)
        assert query["limit"] == ["10000"]
        assert query["after"] == ["tok"]
        assert query["deploymentIds"] == ["dep_1,dep_2"]
        assert query["minLevel"] == ["LEVEL_WARN"]
        assert query["since"] == ["2026-01-01T00:00:00+00:00"]
        assert "sourceKinds" not in query
        assert query["subjectId"] == ["rollout_1"]
        assert query["types"] == ["deployment.scaled,condition.set"]
        assert query["until"] == ["2026-01-02T00:00:00+00:00"]
        payload = json.loads(result.output)
        assert payload["data"][0]["id"] == "evt_1"
        assert payload["next_cursor"] == "next"

    def test_events_help_mentions_current_limit(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "endpoints", "events", "--help"])

        # Rich help wraps table cells across panel borders and can interleave the
        # type/description columns; strip borders and assert contiguous fragments
        # that survive both agent (plain) and human (rich) formatters.
        output = " ".join(result.output.replace("│", " ").split())
        assert result.exit_code == 0
        assert "Max 10000, defaults to 50." in output
        assert "Minimum severity" in output
        assert "Omit to disable severity filtering." in output
        assert "--source-kinds" not in output

    @pytest.mark.respx(base_url=base_url)
    def test_events_table_colors_message_and_shows_deployment_name(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1/events").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _event_body(
                            id="evt_warn",
                            level="LEVEL_WARN",
                            type="deployment.status_updated",
                            sourceKind="SOURCE_KIND_DEPLOYMENT",
                            deploymentId="dep_1",
                            message="replica unhealthy",
                            subjectId="dep_1",
                        ),
                        _event_body(
                            id="evt_err",
                            level="LEVEL_ERROR",
                            type="pod.log",
                            sourceKind="SOURCE_KIND_DEPLOYMENT",
                            deploymentId="dep_1",
                            message="oom killed",
                        ),
                        _event_body(
                            id="evt_ep",
                            level="LEVEL_INFO",
                            type="endpoint.updated",
                            sourceKind="SOURCE_KIND_ENDPOINT",
                            message="Endpoint updated",
                        ),
                    ],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(
                200,
                json=_endpoint_body(
                    deployments=[
                        {
                            "id": "dep_1",
                            "name": "my-project/my-endpoint/canary",
                            "model": "projects/proj/models/ml_1/revisions/latest",
                            "modelId": "ml_1",
                            "hardware": "1x-h100",
                            "state": "DEPLOYMENT_STATE_READY",
                            "readyReplicas": 1,
                            "desiredReplicas": 1,
                            "estimatedEffectiveTrafficShare": 1.0,
                            "createdAt": "2026-01-01T00:00:00Z",
                            "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
                        }
                    ],
                ),
            )
        )

        result = cli_runner.invoke(["beta", "endpoints", "events", "ep_1", "--project", "proj"])

        assert result.exit_code == 0, result.output
        assert "canary" in result.output
        assert "my-end" in result.output  # endpoint short name; may truncate in narrow tables
        assert "replica unhealthy" in result.output
        assert "oom killed" in result.output
        assert "SOURCE_KIND_DEPLOYMENT" not in result.output
        assert "LEVEL_" not in result.output
        assert "Subject" not in result.output
