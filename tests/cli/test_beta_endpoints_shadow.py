from __future__ import annotations

import os
import json
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.api.beta.endpoints.shadow import build_shadow_name, resolve_rate_or_target_qps

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
        "deployments": [],
    }
    body.update(overrides)
    return body


def _shadow_experiment_body(
    experiment_id: str = "exp_1",
    name: str = "shadow-rate-0.1",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": experiment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": name,
        "source": {"endpoint": {"sampling": {"uniform": {"rate": 0.1}}}},
        "targets": [],
        "createdAt": "2026-01-01T00:00:00Z",
        "state": "SHADOW_EXPERIMENT_STATE_INACTIVE",
    }
    body.update(overrides)
    return body


def _shadow_target_body(
    target_id: str = "target_1",
    name: str = "shadow-dep-target",
    target_deployment_id: str = "dep_shadow",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": target_id,
        "experimentId": "exp_1",
        "name": name,
        "targetDeploymentId": target_deployment_id,
        "createdAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _deployment_body(
    deployment_id: str = "dep_shadow",
    name: str = "shadow-dep",
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


def _config_body(config_id: str = "cr_1", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": config_id,
        "projectId": "proj",
        "referenceModel": "projects/proj/models/ml_1",
        "referenceModelId": "ml_1",
        "selectors": [{"key": "gpu", "value": "H100"}],
        "certifications": [],
    }
    body.update(overrides)
    return body


def _mock_model_and_config(respx_mock: MockRouter, *, configs: list[dict[str, Any]] | None = None) -> None:
    respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
    respx_mock.get("/projects/proj/configs").mock(
        return_value=httpx.Response(
            200,
            json={"object": "list", "data": configs if configs is not None else [_config_body()], "next_cursor": None},
        )
    )


def _mock_endpoint(respx_mock: MockRouter) -> None:
    respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))


def _shadow_cli_args(**overrides: str) -> list[str]:
    args = [
        "beta",
        "endpoints",
        "shadow",
        "--project",
        "proj",
        "--endpoint",
        "ep_1",
        "--model",
        "ml_1",
        "--config",
        "cr_1",
        "--name",
        "shadow-dep",
        "--rate",
        "0.1",
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


class TestBuildShadowName:
    def test_uniform_rate_only(self) -> None:
        assert build_shadow_name(0.1, None, None, None) == "shadow-rate-0.1"

    def test_key_based_sampling(self) -> None:
        assert build_shadow_name(0.25, "user_id", None, None) == "shadow-rate-0.25-key-user_id"

    def test_adaptive_target_qps_with_window(self) -> None:
        assert build_shadow_name(None, None, 5.0, "30s") == "shadow-target_qps-5.0-window-30s"

    def test_adaptive_key_based(self) -> None:
        assert build_shadow_name(None, "session", 10.0, None) == "shadow-key-session-target_qps-10.0"


class TestResolveRateOrTargetQps:
    def _config(self, *, non_interactive: bool = False) -> CLIConfig:
        return CLIConfig(client=MagicMock(), non_interactive=non_interactive, json=False, project_id="proj")

    @pytest.mark.asyncio
    async def test_passthrough_when_rate_set(self) -> None:
        assert await resolve_rate_or_target_qps(0.2, None, config=self._config()) == (0.2, None)

    @pytest.mark.asyncio
    async def test_passthrough_when_target_qps_set(self) -> None:
        assert await resolve_rate_or_target_qps(None, 5.0, config=self._config()) == (None, 5.0)

    @pytest.mark.asyncio
    async def test_non_interactive_raises(self) -> None:
        with pytest.raises(ValueError, match="Either rate or target_qps must be provided"):
            await resolve_rate_or_target_qps(None, None, config=self._config(non_interactive=True))

    @pytest.mark.asyncio
    async def test_prompts_for_rate(self) -> None:
        prompt = AsyncMock(side_effect=["rate", "0.25"])
        with patch("together.lib.cli.api.beta.endpoints.shadow.PromptParameter") as PromptParameter:
            PromptParameter.return_value.prompt = prompt
            assert await resolve_rate_or_target_qps(None, None, config=self._config()) == (0.25, None)

    @pytest.mark.asyncio
    async def test_prompts_for_target_qps(self) -> None:
        prompt = AsyncMock(side_effect=["target_qps", "10"])
        with patch("together.lib.cli.api.beta.endpoints.shadow.PromptParameter") as PromptParameter:
            PromptParameter.return_value.prompt = prompt
            assert await resolve_rate_or_target_qps(None, None, config=self._config()) == (None, 10.0)

    @pytest.mark.asyncio
    async def test_rejects_out_of_range_rate(self) -> None:
        prompt = AsyncMock(side_effect=["rate", "1.5"])
        with patch("together.lib.cli.api.beta.endpoints.shadow.PromptParameter") as PromptParameter:
            PromptParameter.return_value.prompt = prompt
            with pytest.raises(ValueError, match="Rate must be between 0.0 and 1.0"):
                await resolve_rate_or_target_qps(None, None, config=self._config())


class TestBetaEndpointShadow:
    @pytest.mark.respx(base_url=base_url)
    def test_shadow_creates_experiment_deployment_and_target(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        _mock_model_and_config(respx_mock)
        create_experiment_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(200, json=_shadow_target_body())
        )

        result = cli_runner.invoke(_shadow_cli_args())

        assert result.exit_code == 0, result.output

        experiment_body = json.loads(cast(Call, create_experiment_route.calls[0]).request.content.decode())
        assert experiment_body == {
            "name": "shadow-rate-0.1",
            "source": {"endpoint": {"sampling": {"uniform": {"rate": 0.1}}}},
            "targets": [],
        }

        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body == {
            "name": "shadow-dep",
            "model": "projects/proj/models/ml_1",
            "config": "projects/proj/configs/cr_1",
            "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
            "enableLora": False,
        }

        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body == {
            "name": "shadow-dep-target",
            "targetDeploymentId": "dep_shadow",
        }

        output = json.loads(result.output)
        assert output["deployment"]["id"] == "dep_shadow"
        assert output["shadow_experiment"]["id"] == "exp_1"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_reuses_existing_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        _mock_model_and_config(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                409,
                json={"error": {"message": "Shadow experiment already exists", "type": "conflict"}},
            )
        )
        list_route = respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_shadow_experiment_body(name="shadow-rate-0.1")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body(deployment_id="dep_shadow_2"))
        )
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(
                    target_id="target_2",
                    target_deployment_id="dep_shadow_2",
                ),
            )
        )

        result = cli_runner.invoke(_shadow_cli_args())

        assert result.exit_code == 0, result.output
        assert list_route.call_count == 1
        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body["targetDeploymentId"] == "dep_shadow_2"

        output = json.loads(result.output)
        assert output["shadow_experiment"]["name"] == "shadow-rate-0.1"
        assert output["deployment"]["id"] == "dep_shadow_2"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_errors_when_experiment_exists_but_not_on_endpoint(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        _mock_model_and_config(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                409,
                json={"error": {"message": "Shadow experiment already exists", "type": "conflict"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )

        result = cli_runner.invoke(_shadow_cli_args())

        assert result.exit_code != 0
        assert "likely a bug in the CLI" in result.output

    def test_shadow_requires_rate_or_target_qps(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--non-interactive",
            ]
        )

        assert result.exit_code != 0
        assert "Either rate or target_qps must be provided" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_resolves_single_config(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        configs_route = respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_config_body()], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(200, json=_shadow_target_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--model",
                "ml_1",
                "--name",
                "shadow-dep",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, configs_route.calls[0]).request.url)
        assert "referenceModelId=ml_1" in url

        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body["config"] == "projects/proj/configs/cr_1"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_errors_on_multiple_configs(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_config_body(), _config_body(config_id="cr_2")],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--model",
                "ml_1",
                "--rate",
                "0.1",
            ]
        )

        assert result.exit_code != 0
        assert "Multiple configs found for model" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_target_qps_posts_adaptive_sampling(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        _mock_model_and_config(respx_mock)
        create_experiment_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_experiment_body(
                    name="shadow-target_qps-5.0",
                    source={"endpoint": {"sampling": {"adaptive_uniform": {"target_qps": 5.0}}}},
                ),
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(200, json=_shadow_target_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--model",
                "ml_1",
                "--config",
                "cr_1",
                "--name",
                "shadow-dep",
                "--target-qps",
                "5",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        experiment_body = json.loads(cast(Call, create_experiment_route.calls[0]).request.content.decode())
        assert experiment_body["name"] == "shadow-target_qps-5.0"
        assert experiment_body["source"] == {
            "endpoint": {"sampling": {"adaptiveUniform": {"targetQps": 5.0}}},
        }
