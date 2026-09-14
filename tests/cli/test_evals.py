from __future__ import annotations

import os
import json
from typing import Any, cast
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.types.file_response import FileResponse

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


def _file_response(**kwargs: Any) -> FileResponse:
    defaults: dict[str, Any] = {
        "id": "file-up",
        "bytes": 10,
        "created_at": 1,
        "filename": "eval-input.jsonl",
        "FileType": "jsonl",
        "object": "file",
        "Processed": True,
        "purpose": "eval",
    }
    defaults.update(kwargs)
    if hasattr(FileResponse, "model_validate"):
        return FileResponse.model_validate(defaults)
    return FileResponse.parse_obj(defaults)  # pyright: ignore[reportDeprecated]


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

    @pytest.mark.respx(base_url=base_url)
    def test_local_input_upload_uses_progress_callback(
        self, tmp_path: Path, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        input_file = tmp_path / "eval-input.jsonl"
        input_file.write_text('{"prompt": "hello", "response_a": "a", "response_b": "b"}\n')
        uploaded = _file_response(id="file-uploaded")
        route = respx_mock.post("/evaluation").mock(
            return_value=httpx.Response(200, json={"workflow_id": "eval-wf-1", "status": "pending"})
        )

        with patch("together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock) as upload_mock:
            upload_mock.return_value = uploaded
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
                    str(input_file),
                    "--model-a-field",
                    "response_a",
                    "--model-b-field",
                    "response_b",
                ]
            )

        assert result.exit_code == 0
        upload_mock.assert_called_once()
        upload_kwargs = upload_mock.call_args.kwargs
        assert upload_kwargs["file"] == input_file
        assert upload_kwargs["purpose"] == "eval"
        assert upload_kwargs["check"] is False
        assert upload_kwargs["progress_callback"] is not None
        req = cast(Call, route.calls[0]).request
        payload = json.loads(req.content)
        assert payload["parameters"]["input_data_file_path"] == "file-uploaded"

    @pytest.mark.respx(base_url=base_url)
    def test_local_input_upload_json_mode_disables_progress_callback(
        self, tmp_path: Path, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        input_file = tmp_path / "eval-input.jsonl"
        input_file.write_text('{"prompt": "hello", "response_a": "a", "response_b": "b"}\n')
        uploaded = _file_response(id="file-uploaded")
        respx_mock.post("/evaluation").mock(
            return_value=httpx.Response(200, json={"workflow_id": "eval-wf-1", "status": "pending"})
        )

        with patch("together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock) as upload_mock:
            upload_mock.return_value = uploaded
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
                    str(input_file),
                    "--model-a-field",
                    "response_a",
                    "--model-b-field",
                    "response_b",
                    "--json",
                ]
            )

        assert result.exit_code == 0
        upload_mock.assert_called_once()
        assert upload_mock.call_args.kwargs["progress_callback"] is None
        assert json.loads(result.out_out.lstrip("\n"))["workflow_id"] == "eval-wf-1"
