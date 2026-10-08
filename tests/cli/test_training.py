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


def _meta(*, has_more: bool = False, next_cursor: str | None = None, limit: int = 20) -> dict[str, Any]:
    return {"has_more": has_more, "limit": limit, "next_cursor": next_cursor or ""}


def _resource_body(resource_id: str = "res-1", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": resource_id,
        "base_model": "Qwen/Qwen3-0.6B",
        "compute_config": {"num_generator_replicas": 1, "gpu_type": "H100-80GB"},
        "created_at": "2026-01-01T00:00:00Z",
        "created_by": "user-1",
        "lora_enabled": True,
        "optimizer_config": {"adam": {}},
        "status": "MODEL_RESOURCES_STATUS_READY",
        "status_details": {},
        "updated_at": "2026-01-01T01:00:00Z",
    }
    body.update(overrides)
    return body


def _inference_checkpoint(checkpoint_id: str = "ckpt-inf-1", *, step: int = 4) -> dict[str, Any]:
    return {
        "id": checkpoint_id,
        "created_at": "2026-01-02T00:00:00Z",
        "step": step,
        "registration": {
            "model": {"id": "ml_model", "revision_id": "rev-1"},
        },
    }


def _training_checkpoint(checkpoint_id: str = "ckpt-train-1") -> dict[str, Any]:
    return {
        "id": checkpoint_id,
        "created_at": "2026-01-02T00:00:00Z",
        "step": 4,
    }


def _session_body(session_id: str = "sess-1", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": session_id,
        "base_model": "Qwen/Qwen3-0.6B",
        "created_at": "2026-01-01T00:00:00Z",
        "created_by": "user-1",
        "display_name": "run-a",
        "inference_checkpoints": [],
        "metadata": {},
        "model_resources_id": "res-1",
        "policy_state": {
            "applied_weights_version": 1,
            "pending_publish": False,
            "target_weights_version": 1,
            "trainer_step": 4,
        },
        "status": "TRAINING_SESSION_STATUS_RUNNING",
        "step": 4,
        "training_checkpoints": [],
        "updated_at": "2026-01-01T01:00:00Z",
    }
    body.update(overrides)
    return body


def _checkpoint_body(
    checkpoint_id: str = "ckpt-inf-1",
    *,
    checkpoint_type: str = "CHECKPOINT_TYPE_INFERENCE",
) -> dict[str, Any]:
    return {
        "id": checkpoint_id,
        "base_model": "Qwen/Qwen3-0.6B",
        "created_at": "2026-01-02T00:00:00Z",
        "session_id": "sess-1",
        "step": 12,
        "type": checkpoint_type,
        "lora_rank": 16,
    }


def _not_found() -> httpx.Response:
    return httpx.Response(404, json={"error": {"message": "not found", "type": "not_found"}})


def _mock_get_misses(respx_mock: MockRouter, object_id: str, *, hit: str) -> None:
    routes = {
        "resource": f"/rl/model-resources/{object_id}",
        "session": f"/rl/training-sessions/{object_id}",
        "checkpoint": f"/rl/checkpoints/{object_id}",
    }
    for kind, path in routes.items():
        if kind == hit:
            continue
        respx_mock.get(path).mock(return_value=_not_found())


class TestTrainingHelp:
    @pytest.mark.usefixtures("plain_cli_help")
    def test_training_help_lists_commands(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["training", "--help"])

        assert result.exit_code == 0, result.output
        assert "ls-resources" in result.output
        assert "ls-sessions" in result.output
        assert "ls-checkpoints" in result.output
        assert "List inference checkpoints" in result.output
        assert "get" in result.output
        assert "prepare-for-fp4-inference" in result.output

    @pytest.mark.usefixtures("plain_cli_help")
    def test_beta_help_omits_training_commands(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "--help"])

        assert result.exit_code == 0, result.output
        assert "ls-resources" not in result.output


class TestTrainingResources:
    @pytest.mark.respx(base_url=base_url)
    def test_ls_resources_json_and_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/rl/model-resources").mock(
            return_value=httpx.Response(
                200,
                json={"data": [_resource_body()], "meta": _meta()},
            )
        )

        result = cli_runner.invoke(
            [
                "training",
                "ls-resources",
                "--limit",
                "2",
                "--after",
                "res-0",
                "--created-by",
                "me",
                "--status",
                "ready",
                "--status",
                "error",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        params = cast(Call, route.calls[0]).request.url.params
        assert params["limit"] == "2"
        assert params["after"] == "res-0"
        assert params["created_by"] == "me"
        assert params["status"] == "MODEL_RESOURCES_STATUS_READY,MODEL_RESOURCES_STATUS_ERROR"
        payload = json.loads(result.out_out)
        assert payload["data"][0]["id"] == "res-1"
        assert payload["data"][0]["status"] == "MODEL_RESOURCES_STATUS_READY"

    @pytest.mark.respx(base_url=base_url)
    def test_ls_resources_table_and_next_page(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/model-resources").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [_resource_body()],
                    "meta": _meta(has_more=True, next_cursor="res-1"),
                },
            )
        )

        result = cli_runner.invoke(["training", "ls-resources"])

        assert result.exit_code == 0, result.output
        assert "res-1" in result.output
        assert "Qwen/Qwen3-0.6B" in result.output
        assert "ready" in result.output
        assert "tg training ls-resources --after res-1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_ls_resources_empty(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/model-resources").mock(return_value=httpx.Response(200, json={"data": [], "meta": _meta()}))

        result = cli_runner.invoke(["training", "ls-resources"])

        assert result.exit_code == 0, result.output
        assert "No model resources found" in result.output

    def test_ls_resources_rejects_non_positive_limit(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["training", "ls-resources", "--limit", "0"])

        assert result.exit_code == 1
        assert "--limit must be at least 1" in result.output


class TestTrainingSessions:
    @pytest.mark.respx(base_url=base_url)
    def test_ls_sessions_filters_and_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/rl/training-sessions").mock(
            return_value=httpx.Response(
                200,
                json={"data": [_session_body()], "meta": _meta()},
            )
        )

        result = cli_runner.invoke(
            [
                "training",
                "ls-sessions",
                "--resources",
                "res-1",
                "--status",
                "running",
                "--created-by",
                "me",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        params = cast(Call, route.calls[0]).request.url.params
        assert params["model_resources_id"] == "res-1"
        assert params["created_by"] == "me"
        assert params["status"] == "TRAINING_SESSION_STATUS_RUNNING"
        payload = json.loads(result.out_out)
        assert payload["data"][0]["id"] == "sess-1"
        assert payload["data"][0]["model_resources_id"] == "res-1"

    @pytest.mark.respx(base_url=base_url)
    def test_ls_sessions_table_and_next_page(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/training-sessions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [_session_body()],
                    "meta": _meta(has_more=True, next_cursor="sess-1"),
                },
            )
        )

        result = cli_runner.invoke(["training", "ls-sessions", "--status", "running"])

        assert result.exit_code == 0, result.output
        assert "sess-1" in result.output
        assert "run-a" in result.output
        assert "running" in result.output
        assert "tg training ls-sessions --status running --after sess-1" in result.output


class TestTrainingCheckpoints:
    @pytest.mark.respx(base_url=base_url)
    def test_ls_checkpoints_flattens_inference_checkpoints_across_session_pages(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        def respond(request: httpx.Request) -> httpx.Response:
            if request.url.params.get("after") == "sess-1":
                body = {
                    "data": [
                        _session_body(
                            "sess-2",
                            inference_checkpoints=[_inference_checkpoint("ckpt-inf-2")],
                        )
                    ],
                    "meta": _meta(),
                }
            else:
                body = {
                    "data": [
                        _session_body(
                            "sess-1",
                            inference_checkpoints=[],
                            training_checkpoints=[_training_checkpoint()],
                        )
                    ],
                    "meta": _meta(has_more=True, next_cursor="sess-1", limit=100),
                }
            return httpx.Response(200, json=body)

        route = respx_mock.get("/rl/training-sessions").mock(side_effect=respond)

        result = cli_runner.invoke(["training", "ls-checkpoints", "--json"])

        assert result.exit_code == 0, result.output
        assert route.call_count == 2
        assert cast(Call, route.calls[0]).request.url.params["limit"] == "100"
        payload = json.loads(result.out_out)
        assert [item["id"] for item in payload["data"]] == ["ckpt-inf-2"]
        assert payload["data"][0]["session_id"] == "sess-2"
        assert payload["data"][0]["registration"]["model"]["id"] == "ml_model"
        assert "ckpt-train-1" not in result.out_out

    @pytest.mark.respx(base_url=base_url)
    def test_ls_checkpoints_session_flag_does_not_list_sessions(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/rl/training-sessions/sess-1").mock(
            return_value=httpx.Response(
                200,
                json=_session_body(
                    inference_checkpoints=[
                        _inference_checkpoint("ckpt-a", step=1),
                        _inference_checkpoint("ckpt-b", step=2),
                    ]
                ),
            )
        )

        result = cli_runner.invoke(["training", "ls-checkpoints", "--session", "sess-1", "--limit", "1", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert [item["id"] for item in payload["data"]] == ["ckpt-a"]
        assert payload["meta"]["has_more"] is True
        assert payload["meta"]["next_cursor"] == "ckpt-a"

    @pytest.mark.respx(base_url=base_url)
    def test_ls_checkpoints_after_skips_to_the_next_checkpoint(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/rl/training-sessions/sess-1").mock(
            return_value=httpx.Response(
                200,
                json=_session_body(
                    inference_checkpoints=[
                        _inference_checkpoint("ckpt-a", step=1),
                        _inference_checkpoint("ckpt-b", step=2),
                    ]
                ),
            )
        )

        result = cli_runner.invoke(["training", "ls-checkpoints", "--session-id", "sess-1", "--after", "ckpt-a"])

        assert result.exit_code == 0, result.output
        assert "ckpt-b" in result.output
        assert "ckpt-a" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_ls_checkpoints_unknown_cursor(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/training-sessions").mock(
            return_value=httpx.Response(200, json={"data": [_session_body()], "meta": _meta()})
        )

        result = cli_runner.invoke(["training", "ls-checkpoints", "--after", "missing-ckpt"])

        assert result.exit_code == 0, result.output
        assert "missing-ckpt" in result.output
        assert "was not found" in result.output
        assert "No inference checkpoints found" in result.output


class TestTrainingGet:
    @pytest.mark.respx(base_url=base_url)
    def test_get_model_resource(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/model-resources/res-1").mock(
            return_value=httpx.Response(200, json=_resource_body(base_weights_ref="ml_weights"))
        )
        _mock_get_misses(respx_mock, "res-1", hit="resource")

        result = cli_runner.invoke(["training", "get", "res-1", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["kind"] == "model_resource"
        assert payload["data"]["id"] == "res-1"
        assert payload["data"]["base_weights_ref"] == "ml_weights"

    @pytest.mark.respx(base_url=base_url)
    def test_get_training_session(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/training-sessions/sess-1").mock(return_value=httpx.Response(200, json=_session_body()))
        _mock_get_misses(respx_mock, "sess-1", hit="session")

        result = cli_runner.invoke(["training", "get", "sess-1"])

        assert result.exit_code == 0, result.output
        assert "Training session" in result.output
        assert "sess-1" in result.output
        assert "run-a" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_get_inference_checkpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/checkpoints/ckpt-inf-1").mock(return_value=httpx.Response(200, json=_checkpoint_body()))
        _mock_get_misses(respx_mock, "ckpt-inf-1", hit="checkpoint")

        result = cli_runner.invoke(["training", "get", "ckpt-inf-1", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["kind"] == "inference_checkpoint"
        assert payload["data"]["id"] == "ckpt-inf-1"
        assert payload["data"]["session_id"] == "sess-1"
        assert payload["data"]["type"] == "CHECKPOINT_TYPE_INFERENCE"

    @pytest.mark.respx(base_url=base_url)
    def test_get_training_checkpoint(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/checkpoints/ckpt-train-1").mock(
            return_value=httpx.Response(
                200,
                json=_checkpoint_body("ckpt-train-1", checkpoint_type="CHECKPOINT_TYPE_TRAINING"),
            )
        )
        _mock_get_misses(respx_mock, "ckpt-train-1", hit="checkpoint")

        result = cli_runner.invoke(["training", "get", "ckpt-train-1"])

        assert result.exit_code == 0, result.output
        assert "Training checkpoint" in result.output
        assert "ckpt-train-1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_get_prefers_a_hit_over_an_error_from_another_type(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/rl/model-resources/sess-1").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"message": "model resources unavailable", "type": "server_error"}},
            )
        )
        respx_mock.get("/rl/training-sessions/sess-1").mock(return_value=httpx.Response(200, json=_session_body()))
        respx_mock.get("/rl/checkpoints/sess-1").mock(return_value=_not_found())

        result = cli_runner.invoke(["training", "get", "sess-1", "--json"])

        assert result.exit_code == 0, result.output
        assert json.loads(result.out_out)["kind"] == "training_session"

    @pytest.mark.respx(base_url=base_url)
    def test_get_missing_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_get_misses(respx_mock, "missing", hit="")

        result = cli_runner.invoke(["training", "get", "missing", "--json"])

        assert result.exit_code == 1
        payload = json.loads(result.out_out)
        assert "missing" in payload["error"]

    @pytest.mark.respx(base_url=base_url)
    def test_get_surfaces_non_404_when_nothing_matches(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/rl/model-resources/missing").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"message": "model resources unavailable", "type": "server_error"}},
            )
        )
        respx_mock.get("/rl/training-sessions/missing").mock(return_value=_not_found())
        respx_mock.get("/rl/checkpoints/missing").mock(return_value=_not_found())

        result = cli_runner.invoke(["training", "get", "missing"])

        assert result.exit_code == 1
        assert "model resources unavailable" in result.output
        assert "No model resource" not in result.output
