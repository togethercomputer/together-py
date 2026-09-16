from __future__ import annotations

import os
import json
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from together import APIError
from tests.cli.utils import CliRunner
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.api.beta.endpoints.shadow import (
    build_shadow_name,
    resolve_model_for_create,
    default_shadow_target_name,
    resolve_rate_or_target_qps,
    match_existing_shadow_target,
    maybe_resolve_existing_deployment,
    verify_shadow_target_not_receiving_live_traffic,
)
from together.types.beta.endpoints.shadow_experiments import ShadowExperimentTarget
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import AmbiguousDeploymentError

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


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


def _deployment_summary(
    deployment_id: str = "dep_existing",
    name: str = "my-project/my-endpoint/existing-shadow",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": deployment_id,
        "name": name,
        "modelId": "ml_1",
        "state": "DEPLOYMENT_STATE_READY",
        "readyReplicas": 1,
        "desiredReplicas": 1,
        "createdAt": "2026-01-01T00:00:00Z",
        "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
    }
    body.update(overrides)
    return body


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


def _rollout_body(
    *,
    rollout_id: str = "rol_1",
    source_deployment_id: str = "dep_control",
    target_deployment_id: str = "dep_target",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": rollout_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "sourceDeploymentId": source_deployment_id,
        "targetDeploymentId": target_deployment_id,
        "state": "ROLLOUT_STATE_RUNNING",
        "strategy": "ROLLOUT_STRATEGY_TYPE_BLUE_GREEN",
        "createdAt": "2026-01-01T00:00:00Z",
        "startedAt": "2026-01-01T00:01:00Z",
        "currentStep": 0,
        "currentTrafficPercent": 0,
        "etag": "etag-rol",
        "status": {"totalSteps": 1, "steps": []},
    }
    body.update(overrides)
    return body


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


def _shadow_existing_deployment_cli_args(**overrides: str) -> list[str]:
    args = [
        "beta",
        "endpoints",
        "shadow",
        "--project",
        "proj",
        "--endpoint",
        "dep_existing",
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


def _mock_existing_deployment_lookup(
    respx_mock: MockRouter,
    *,
    deployment_id: str = "dep_existing",
    endpoint_id: str = "ep_1",
    deployment_name: str = "my-project/my-endpoint/existing-shadow",
    retrieve: bool = True,
    traffic_split: list[dict[str, Any]] | None = None,
    active_rollout_id: str | None = None,
) -> None:
    endpoint_overrides: dict[str, Any] = {
        "id": endpoint_id,
        "deployments": [_deployment_summary(deployment_id=deployment_id, name=deployment_name)],
    }
    if traffic_split is not None:
        endpoint_overrides["trafficSplit"] = traffic_split
    if active_rollout_id is not None:
        endpoint_overrides["activeRolloutId"] = active_rollout_id
    data = [_endpoint_body(**endpoint_overrides)]
    respx_mock.get("/projects/proj/endpoints").mock(
        return_value=httpx.Response(
            200,
            json={
                "object": "list",
                "data": data,
                "next_cursor": None,
            },
        )
    )
    if retrieve:
        respx_mock.get(f"/projects/proj/endpoints/{endpoint_id}/deployments/{deployment_id}").mock(
            return_value=httpx.Response(
                200,
                json=_deployment_body(
                    deployment_id=deployment_id,
                    name=deployment_name,
                    **({"endpointId": endpoint_id} if endpoint_id != "ep_1" else {}),
                ),
            )
        )


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


class TestMaybeResolveExistingDeployment:
    def _config(self, client: MagicMock | None = None) -> CLIConfig:
        return CLIConfig(client=client or MagicMock(), non_interactive=True, json=False, project_id="proj")

    @pytest.mark.asyncio
    async def test_endpoint_id_is_not_existing_deployment(self) -> None:
        assert (
            await maybe_resolve_existing_deployment(
                self._config(),
                "ep_1",
                model=None,
                config_id=None,
                enable_lora=False,
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_endpoint_plus_model_is_create_path(self) -> None:
        assert (
            await maybe_resolve_existing_deployment(
                self._config(),
                "my-endpoint",
                model="ml_1",
                config_id=None,
                enable_lora=False,
            )
            is None
        )

    @pytest.mark.asyncio
    async def test_dep_id_resolves_existing_deployment(self) -> None:
        endpoint = MagicMock(id="ep_1")
        with patch(
            "together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id",
            AsyncMock(return_value=(endpoint, "dep_existing")),
        ):
            result = await maybe_resolve_existing_deployment(
                self._config(),
                "dep_existing",
                model=None,
                config_id=None,
                enable_lora=False,
            )
        assert result == (endpoint, "dep_existing")

    @pytest.mark.asyncio
    async def test_rejects_model_with_dep_id_before_lookup(self) -> None:
        resolve = AsyncMock()
        with patch("together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id", resolve):
            with pytest.raises(ValueError, match="Do not pass MODEL when ENDPOINT is an existing deployment"):
                await maybe_resolve_existing_deployment(
                    self._config(),
                    "dep_existing",
                    model="ml_1",
                    config_id=None,
                    enable_lora=False,
                )
        resolve.assert_not_called()

    @pytest.mark.asyncio
    async def test_rejects_config_with_dep_id_before_lookup(self) -> None:
        resolve = AsyncMock()
        with patch("together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id", resolve):
            with pytest.raises(ValueError, match="Do not pass --config when ENDPOINT is an existing deployment"):
                await maybe_resolve_existing_deployment(
                    self._config(),
                    "dep_existing",
                    model=None,
                    config_id="cr_1",
                    enable_lora=False,
                )
        resolve.assert_not_called()

    @pytest.mark.asyncio
    async def test_rejects_enable_lora_with_dep_id_before_lookup(self) -> None:
        resolve = AsyncMock()
        with patch("together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id", resolve):
            with pytest.raises(ValueError, match="Do not pass --enable-lora when ENDPOINT is an existing deployment"):
                await maybe_resolve_existing_deployment(
                    self._config(),
                    "dep_existing",
                    model=None,
                    config_id=None,
                    enable_lora=True,
                )
        resolve.assert_not_called()

    @pytest.mark.asyncio
    async def test_bare_name_raises_when_neither_endpoint_nor_deployment(self) -> None:
        with patch(
            "together.lib.cli.api.beta.endpoints.shadow.resolve_endpoint",
            AsyncMock(side_effect=ValueError("Endpoint my-endpoint not found.")),
        ):
            with patch(
                "together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id",
                AsyncMock(side_effect=ValueError("Deployment my-endpoint not found in any endpoint.")),
            ):
                with pytest.raises(ValueError, match="Endpoint my-endpoint not found"):
                    await maybe_resolve_existing_deployment(
                        self._config(),
                        "my-endpoint",
                        model=None,
                        config_id=None,
                        enable_lora=False,
                    )

    @pytest.mark.asyncio
    async def test_bare_name_prefers_endpoint_over_deployment(self) -> None:
        endpoint = MagicMock(id="ep_1")
        resolve_deployment = AsyncMock()
        with patch(
            "together.lib.cli.api.beta.endpoints.shadow.resolve_endpoint",
            AsyncMock(return_value=endpoint),
        ):
            with patch("together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id", resolve_deployment):
                result = await maybe_resolve_existing_deployment(
                    self._config(),
                    "my-endpoint",
                    model=None,
                    config_id=None,
                    enable_lora=True,
                )
        assert result == (endpoint, None)
        resolve_deployment.assert_not_called()

    @pytest.mark.asyncio
    async def test_bare_name_raises_on_ambiguous_deployment(self) -> None:
        with patch(
            "together.lib.cli.api.beta.endpoints.shadow.resolve_endpoint",
            AsyncMock(side_effect=ValueError("Endpoint candidate not found.")),
        ):
            with patch(
                "together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id",
                AsyncMock(
                    side_effect=AmbiguousDeploymentError(
                        'Multiple deployments found for "candidate".\n'
                        "Please specify a deployment ID (dep_...) or a fully qualified deployment name.\n"
                    )
                ),
            ):
                with pytest.raises(AmbiguousDeploymentError, match="Multiple deployments found"):
                    await maybe_resolve_existing_deployment(
                        self._config(),
                        "candidate",
                        model=None,
                        config_id=None,
                        enable_lora=False,
                    )

    @pytest.mark.asyncio
    async def test_qualified_deployment_name_skips_endpoint_lookup(self) -> None:
        endpoint = MagicMock(id="ep_1")
        resolve_endpoint_mock = AsyncMock()
        with patch("together.lib.cli.api.beta.endpoints.shadow.resolve_endpoint", resolve_endpoint_mock):
            with patch(
                "together.lib.cli.api.beta.endpoints.shadow.resolve_deployment_id",
                AsyncMock(return_value=(endpoint, "dep_existing")),
            ):
                result = await maybe_resolve_existing_deployment(
                    self._config(),
                    "my-project/my-endpoint/existing-shadow",
                    model=None,
                    config_id=None,
                    enable_lora=False,
                )
        assert result == (endpoint, "dep_existing")
        resolve_endpoint_mock.assert_not_called()


class TestResolveModelForCreate:
    def _config(self, *, non_interactive: bool = False) -> CLIConfig:
        return CLIConfig(client=MagicMock(), non_interactive=non_interactive, json=False, project_id="proj")

    @pytest.mark.asyncio
    async def test_passthrough_model(self) -> None:
        assert await resolve_model_for_create("ml_1", config=self._config()) == "ml_1"

    @pytest.mark.asyncio
    async def test_non_interactive_requires_model(self) -> None:
        with pytest.raises(ValueError, match="MODEL is required when ENDPOINT is an endpoint ID or name"):
            await resolve_model_for_create(None, config=self._config(non_interactive=True))

    @pytest.mark.asyncio
    async def test_prompts_for_model(self) -> None:
        prompt = AsyncMock(return_value="ml_1")
        with patch("together.lib.cli.api.beta.endpoints.shadow.ModelPromptParameter") as ModelPromptParameter:
            ModelPromptParameter.return_value.preprompt = AsyncMock()
            ModelPromptParameter.return_value.prompt = prompt
            assert await resolve_model_for_create(None, config=self._config()) == "ml_1"

    @pytest.mark.asyncio
    async def test_preprompt_api_error_is_not_rewritten(self) -> None:
        request = httpx.Request("GET", "https://api.together.ai/v2/projects/proj/models")
        error = APIError("401 unauthorized", request, body={"error": {"message": "unauthorized", "type": "auth"}})
        with patch("together.lib.cli.api.beta.endpoints.shadow.ModelPromptParameter") as ModelPromptParameter:
            ModelPromptParameter.return_value.preprompt = AsyncMock(side_effect=error)
            with pytest.raises(APIError, match="401 unauthorized"):
                await resolve_model_for_create(None, config=self._config())

    @pytest.mark.asyncio
    async def test_missing_questionary_requires_model(self) -> None:
        with patch("together.lib.cli.api.beta.endpoints.shadow.ModelPromptParameter") as ModelPromptParameter:
            ModelPromptParameter.return_value.preprompt = AsyncMock()
            ModelPromptParameter.return_value.prompt = AsyncMock(
                side_effect=ImportError("No module named 'questionary'")
            )
            with pytest.raises(ValueError, match="MODEL is required when ENDPOINT is an endpoint ID or name"):
                await resolve_model_for_create(None, config=self._config())


class TestDefaultShadowTargetName:
    def test_strips_qualified_deployment_name(self) -> None:
        assert default_shadow_target_name("my-project/my-endpoint/existing-shadow") == "existing-shadow-target"

    def test_bare_name(self) -> None:
        assert default_shadow_target_name("existing-shadow") == "existing-shadow-target"


class TestVerifyShadowTargetNotReceivingLiveTraffic:
    def _client(self) -> MagicMock:
        client = MagicMock()
        client.beta.endpoints.rollouts.retrieve = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_allows_absent_from_split(self) -> None:
        client = self._client()
        await verify_shadow_target_not_receiving_live_traffic(
            client, Endpoint.construct(**_endpoint_body()), "dep_existing"
        )
        client.beta.endpoints.rollouts.retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_allows_zero_weight(self) -> None:
        client = self._client()
        endpoint = Endpoint.construct(**_endpoint_body(trafficSplit=[{"deploymentId": "dep_existing", "weight": 0}]))
        await verify_shadow_target_not_receiving_live_traffic(client, endpoint, "dep_existing")
        client.beta.endpoints.rollouts.retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_rejects_live_member(self) -> None:
        client = self._client()
        endpoint = Endpoint.construct(**_endpoint_body(trafficSplit=[{"deploymentId": "dep_existing", "weight": 1.0}]))
        with pytest.raises(ValueError, match="live traffic-split member"):
            await verify_shadow_target_not_receiving_live_traffic(client, endpoint, "dep_existing")
        client.beta.endpoints.rollouts.retrieve.assert_not_called()

    @pytest.mark.asyncio
    async def test_rejects_rollout_participant(self) -> None:
        client = self._client()
        client.beta.endpoints.rollouts.retrieve = AsyncMock(
            return_value=MagicMock(source_deployment_id="dep_existing", target_deployment_id="dep_target")
        )
        endpoint = Endpoint.construct(**_endpoint_body(activeRolloutId="rol_1"))
        with pytest.raises(ValueError, match="participant in active rollout"):
            await verify_shadow_target_not_receiving_live_traffic(client, endpoint, "dep_existing")

    @pytest.mark.asyncio
    async def test_allows_non_participant_when_rollout_active(self) -> None:
        client = self._client()
        client.beta.endpoints.rollouts.retrieve = AsyncMock(
            return_value=MagicMock(source_deployment_id="dep_control", target_deployment_id="dep_target")
        )
        endpoint = Endpoint.construct(**_endpoint_body(activeRolloutId="rol_1"))
        await verify_shadow_target_not_receiving_live_traffic(client, endpoint, "dep_existing")


class TestMatchExistingShadowTarget:
    def _target(self, *, name: str, target_deployment_id: str) -> ShadowExperimentTarget:
        return ShadowExperimentTarget.construct(
            **_shadow_target_body(name=name, target_deployment_id=target_deployment_id)
        )

    def test_reuses_matching_name_and_deployment(self) -> None:
        target = self._target(name="custom", target_deployment_id="dep_existing")
        assert (
            match_existing_shadow_target(
                [target],
                name="custom",
                target_deployment_id="dep_existing",
                experiment_id="exp_1",
            )
            is target
        )

    def test_name_conflict_wins_over_earlier_deployment_match(self) -> None:
        deployment_match = self._target(name="other", target_deployment_id="dep_existing")
        name_match = self._target(name="custom", target_deployment_id="dep_other")
        with pytest.raises(ValueError, match="already exists on this experiment for a different deployment"):
            match_existing_shadow_target(
                [deployment_match, name_match],
                name="custom",
                target_deployment_id="dep_existing",
                experiment_id="exp_1",
            )

    def test_rejects_same_deployment_under_a_different_name(self) -> None:
        with pytest.raises(ValueError, match="already a shadow target on this experiment as 'other'"):
            match_existing_shadow_target(
                [self._target(name="other", target_deployment_id="dep_existing")],
                name="custom",
                target_deployment_id="dep_existing",
                experiment_id="exp_1",
            )


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
    def test_shadow_reuses_existing_experiment_from_later_page(
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
            side_effect=[
                httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [_shadow_experiment_body(experiment_id="exp_other", name="shadow-rate-0.2")],
                        "next_cursor": "next-page",
                    },
                ),
                httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [_shadow_experiment_body(name="shadow-rate-0.1")],
                        "next_cursor": None,
                    },
                ),
            ]
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
        assert list_route.call_count == 2
        assert cast(Call, list_route.calls[1]).request.url.params["after"] == "next-page"
        assert create_target_route.called

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
        # Configs are resolved via the model's baseModelId; deploy target stays ml_1.
        assert "referenceModelId=ml_base" in url

        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body["config"] == "projects/proj/configs/cr_1"
        assert deployment_body["model"] == "projects/proj/models/ml_1"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_errors_on_multiple_configs(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
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

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_uses_existing_deployment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        create_experiment_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(
                    name="existing-shadow-target",
                    target_deployment_id="dep_existing",
                ),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code == 0, result.output
        assert create_experiment_route.call_count == 1

        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body == {
            "name": "existing-shadow-target",
            "targetDeploymentId": "dep_existing",
        }

        output = json.loads(result.output)
        assert output["deployment"]["id"] == "dep_existing"
        assert output["shadow_experiment"]["id"] == "exp_1"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_existing_deployment_custom_target_name(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(
                    name="candidate",
                    target_deployment_id="dep_existing",
                ),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args(name="candidate"))

        assert result.exit_code == 0, result.output
        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body == {
            "name": "candidate",
            "targetDeploymentId": "dep_existing",
        }

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_existing_deployment_reuses_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
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
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(target_deployment_id="dep_existing"),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code == 0, result.output
        assert list_route.call_count == 1
        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body["targetDeploymentId"] == "dep_existing"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_existing_deployment_not_found(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code != 0
        assert "Deployment dep_existing not found" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_rejects_model_with_deployment_id_before_lookup(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "dep_existing",
                "--model",
                "ml_1",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        assert "Do not pass MODEL when ENDPOINT is an existing deployment" in result.output
        assert respx_mock.calls.call_count == 0

    def test_shadow_requires_model_for_endpoint(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "ep_1",
                "--rate",
                "0.1",
                "--non-interactive",
            ]
        )

        assert result.exit_code != 0
        assert "MODEL is required when ENDPOINT is an endpoint ID or name" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_strips_qualified_name_for_default_target(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        create_target_route = respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(name="existing-shadow-target", target_deployment_id="dep_existing"),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code == 0, result.output
        target_body = json.loads(cast(Call, create_target_route.calls[0]).request.content.decode())
        assert target_body["name"] == "existing-shadow-target"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_ambiguous_deployment_name_keeps_disambiguation_error(
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
                    "data": [
                        _endpoint_body(
                            deployments=[
                                _deployment_summary(deployment_id="dep_a", name="my-project/my-endpoint/candidate")
                            ]
                        ),
                        _endpoint_body(
                            id="ep_2",
                            name="my-project/other-endpoint",
                            trafficSplit=[{"deploymentId": "dep_b", "weight": 1.0}],
                            deployments=[
                                _deployment_summary(deployment_id="dep_b", name="my-project/other-endpoint/candidate")
                            ],
                        ),
                    ],
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
                "candidate",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        error = json.loads(result.output)["error"]
        assert "Multiple deployments found" in error
        assert "MODEL is required" not in error

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_bare_endpoint_name_does_not_attach_matching_deployment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(
            respx_mock,
            deployment_name="my-project/my-endpoint/my-endpoint",
            retrieve=False,
        )
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "my-endpoint",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        assert "MODEL is required when ENDPOINT is an endpoint ID or name" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_bare_endpoint_name_allows_create_flags(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(
            respx_mock,
            deployment_name="my-project/my-endpoint/my-endpoint",
            retrieve=False,
        )
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "my-endpoint",
                "--enable-lora",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        assert "Do not pass --enable-lora" not in result.output
        assert "MODEL is required when ENDPOINT is an endpoint ID or name" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_rejects_live_traffic_split_member_before_creating_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(
            respx_mock,
            traffic_split=[{"deploymentId": "dep_existing", "weight": 1.0}],
            retrieve=False,
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code != 0
        assert "live traffic-split member" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_allows_zero_weight_traffic_split_member(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(
            respx_mock,
            traffic_split=[{"deploymentId": "dep_existing", "weight": 0}],
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json=_shadow_target_body(name="existing-shadow-target", target_deployment_id="dep_existing"),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code == 0, result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_reuses_existing_target_on_duplicate_name(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                409,
                json={"error": {"message": "Shadow target already exists", "type": "conflict"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_shadow_target_body(name="existing-shadow-target", target_deployment_id="dep_existing")],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code == 0, result.output
        output = json.loads(result.output)
        assert output["deployment"]["id"] == "dep_existing"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_errors_when_duplicate_target_name_points_elsewhere(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                409,
                json={"error": {"message": "Shadow target already exists", "type": "conflict"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_shadow_target_body(name="existing-shadow-target", target_deployment_id="dep_other")],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code != 0
        assert "already exists on this experiment for a different deployment" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_stray_positional_is_not_bound_to_config(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_endpoint(respx_mock)
        _mock_model_and_config(respx_mock)
        create_deployment_route = respx_mock.post("/projects/proj/endpoints/ep_1/deployments").mock(
            return_value=httpx.Response(200, json=_deployment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
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
                "ep_1",
                "ml_1",
                "stray-token",
                "--rate",
                "0.1",
                "--name",
                "shadow-dep",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        deployment_body = json.loads(cast(Call, create_deployment_route.calls[0]).request.content.decode())
        assert deployment_body["config"] == "projects/proj/configs/cr_1"

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_typoed_endpoint_name_reports_not_found(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )

        result = cli_runner.invoke(
            [
                "beta",
                "endpoints",
                "shadow",
                "--project",
                "proj",
                "--endpoint",
                "typo-endpoint",
                "--rate",
                "0.1",
                "--json",
            ]
        )

        assert result.exit_code != 0
        error = json.loads(result.output)["error"]
        assert "Endpoint typo-endpoint not found" in error
        assert "MODEL is required" not in error

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_name_conflict_not_swallowed_by_earlier_deployment_match(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock)
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json=_shadow_experiment_body())
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                409,
                json={"error": {"message": "Shadow target already exists", "type": "conflict"}},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _shadow_target_body(name="other", target_deployment_id="dep_existing"),
                        _shadow_target_body(name="custom", target_deployment_id="dep_other"),
                    ],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args(name="custom"))

        assert result.exit_code != 0
        assert "already exists on this experiment for a different deployment" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_shadow_rejects_rollout_participant_before_creating_experiment(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_existing_deployment_lookup(respx_mock, active_rollout_id="rol_1", retrieve=False)
        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts/rol_1").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(source_deployment_id="dep_existing"),
            )
        )

        result = cli_runner.invoke(_shadow_existing_deployment_cli_args())

        assert result.exit_code != 0
        assert "participant in active rollout" in result.output
