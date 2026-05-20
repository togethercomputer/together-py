from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"

_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}

_EVAL_JOB = {
    "workflow_id": "eval-wf-1",
    "type": "classify",
    "status": "completed",
    "created_at": "2024-01-01T00:00:00Z",
    "parameters": {"model_to_evaluate": "m1", "model_a": "", "model_b": ""},
}

_EVAL_STATUS = {"status": "completed", "results": None}


class TestEvalsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_passes_status_and_limit(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/evaluation").mock(return_value=httpx.Response(200, json=[_EVAL_JOB]))
        result = cli_runner.invoke(["evals", "list", "--status", "completed", "--limit", "5"])
        assert result.exit_code == 0
        assert "eval-wf-1" in result.output
        req = cast(Call, route.calls[0]).request
        assert "status=completed" in str(req.url)
        assert "limit=5" in str(req.url)

    @pytest.mark.respx(base_url=base_url)
    def test_list_requires_nothing(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/evaluation").mock(return_value=httpx.Response(200, json=[]))
        assert cli_runner.invoke(["evals", "list"]).exit_code == 0


class TestEvalsRetrieveAndStatus:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/evaluation/eval-wf-1").mock(return_value=httpx.Response(200, json=_EVAL_JOB))
        result = cli_runner.invoke(["evals", "retrieve", "eval-wf-1", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.out_out.lstrip("\n"))
        assert payload["workflow_id"] == "eval-wf-1"

    @pytest.mark.respx(base_url=base_url)
    def test_status(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/evaluation/eval-wf-1/status").mock(return_value=httpx.Response(200, json=_EVAL_STATUS))
        result = cli_runner.invoke(["evals", "status", "eval-wf-1"])
        assert result.exit_code == 0
        assert "Status: completed" in result.output


class TestEvalsCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_compare_passes_disable_position_bias_correction(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        route = respx_mock.post("/evaluation").mock(
            return_value=httpx.Response(200, json={"workflow_id": "eval-wf-1", "status": "pending"})
        )

        result = cli_runner.invoke(
            [
                "evals",
                "create",
                "--type",
                "compare",
                "--judge-model",
                "Qwen/Qwen3.5-9B",
                "--judge-model-source",
                "serverless",
                "--judge-system-template",
                "Choose the better response.",
                "--input-data-file-path",
                "file-123",
                "--model-a-field",
                "response_a",
                "--model-b-field",
                "response_b",
                "--disable-position-bias-correction",
            ]
        )

        assert result.exit_code == 0
        req = cast(Call, route.calls[0]).request
        payload = json.loads(req.content)
        assert payload["type"] == "compare"
        assert payload["parameters"]["disable_position_bias_correction"] is True
