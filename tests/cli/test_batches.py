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

_BATCH_JOB = {
    "id": "batch_job_newer",
    "status": "COMPLETED",
    "endpoint": "/v1/chat/completions",
    "model_id": "Qwen/Qwen3.5-9B",
    "input_file_id": "file-abc123",
    "output_file_id": "file-out",
    "progress": 100.0,
    "file_size_bytes": 2048,
    "created_at": "2024-06-02T12:00:00Z",
    "completed_at": "2024-06-02T13:00:00Z",
}

_BATCH_JOB_OLDER = {
    "id": "batch_job_older",
    "status": "IN_PROGRESS",
    "endpoint": "/v1/audio/transcriptions",
    "model_id": "openai/whisper-large-v3",
    "input_file_id": "file-xyz",
    "progress": 42.5,
    "file_size_bytes": 512,
    "created_at": "2024-01-01T12:00:00Z",
}

_BATCH_CREATE = {
    "job": {
        "id": "batch_job_created",
        "status": "VALIDATING",
        "endpoint": "/v1/chat/completions",
        "model_id": "Qwen/Qwen3.5-9B",
        "input_file_id": "file-abc123",
        "progress": 0.0,
        "created_at": "2024-06-02T12:00:00Z",
    },
    "warning": None,
}


def _file_response(**kwargs: Any) -> FileResponse:
    defaults: dict[str, Any] = {
        "id": "file-up",
        "bytes": 10,
        "created_at": 1,
        "filename": "x.jsonl",
        "FileType": "jsonl",
        "object": "file",
        "Processed": True,
        "purpose": "batch-api",
    }
    defaults.update(kwargs)
    if hasattr(FileResponse, "model_validate"):
        return FileResponse.model_validate(defaults)
    return FileResponse.parse_obj(defaults)  # pyright: ignore[reportDeprecated]


class TestBatchesSubmit:
    def test_submit_help_describes_api_types(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["batches", "submit", "--help"])
        assert result.exit_code == 0
        assert "--api" in result.output
        assert "--model" not in result.output
        assert "-M" not in result.output
        assert "chat.completions" in result.output
        assert "audio.transcriptions" in result.output
        assert "audio.translations" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_submit_positional_args(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/batches").mock(return_value=httpx.Response(200, json=_BATCH_CREATE))
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "chat.completions"])
        assert result.exit_code == 0
        assert "batch_job_created" in result.output
        payload = json.loads(cast(Call, route.calls[0]).request.content)
        assert payload["endpoint"] == "/v1/chat/completions"
        assert payload["input_file_id"] == "file-abc123"
        assert "model_id" not in payload

    @pytest.mark.respx(base_url=base_url)
    def test_submit_flag_args(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/batches").mock(return_value=httpx.Response(200, json=_BATCH_CREATE))
        result = cli_runner.invoke(
            [
                "batches",
                "submit",
                "file-abc123",
                "--api",
                "audio.transcriptions",
            ]
        )
        assert result.exit_code == 0
        payload = json.loads(cast(Call, route.calls[0]).request.content)
        assert payload["endpoint"] == "/v1/audio/transcriptions"
        assert "model_id" not in payload

    @pytest.mark.respx(base_url=base_url)
    def test_submit_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/batches").mock(return_value=httpx.Response(200, json=_BATCH_CREATE))
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "chat.completions", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["job"]["id"] == "batch_job_created"

    @pytest.mark.respx(base_url=base_url)
    def test_submit_uploads_local_file(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        sample = tmp_path / "requests.jsonl"
        sample.write_text('{"custom_id": "1"}\n', encoding="utf-8")
        create = respx_mock.post("/batches").mock(return_value=httpx.Response(200, json=_BATCH_CREATE))
        with patch("together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock) as upload_mock:
            upload_mock.return_value = _file_response(id="file-uploaded")
            result = cli_runner.invoke(["batches", "submit", str(sample), "chat.completions"])
        assert result.exit_code == 0
        upload_mock.assert_called_once()
        assert upload_mock.call_args.kwargs["purpose"] == "batch-api"
        assert upload_mock.call_args.kwargs["check"] is False
        payload = json.loads(cast(Call, create.calls[0]).request.content)
        assert payload["input_file_id"] == "file-uploaded"

    def test_submit_rejects_directory(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["batches", "submit", str(tmp_path), "chat.completions"])
        assert result.exit_code == 1
        assert "directory" in result.output.lower()

    def test_submit_rejects_invalid_api(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "not.an.api"])
        assert result.exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_submit_null_job_exits_nonzero(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/batches").mock(
            return_value=httpx.Response(200, json={"job": None, "warning": "validation failed: missing [/close] tag"})
        )
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "chat.completions"])
        assert result.exit_code == 1
        assert "was not created" in result.output
        assert "MarkupError" not in result.output
        assert "[/close]" in result.output or "close" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_submit_null_job_json_exits_nonzero(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/batches").mock(return_value=httpx.Response(200, json={"job": None, "warning": "nope"}))
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "chat.completions", "--json"])
        assert result.exit_code == 1
        body = json.loads(result.output)
        assert body["job"] is None
        assert body["warning"] == "nope"

    @pytest.mark.respx(base_url=base_url)
    def test_submit_does_not_print_x_model_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/batches").mock(return_value=httpx.Response(200, json=_BATCH_CREATE))
        result = cli_runner.invoke(["batches", "submit", "file-abc123", "chat.completions"])
        assert result.exit_code == 0
        assert "X Model Id" not in result.output
        assert "Qwen/Qwen3.5-9B" in result.output


class TestBatchesList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches").mock(return_value=httpx.Response(200, json=[_BATCH_JOB_OLDER, _BATCH_JOB]))
        result = cli_runner.invoke(["batches", "list"])
        assert result.exit_code == 0
        assert "batch_job_newer" in result.output
        assert "batch_job_older" in result.output
        assert result.output.index("batch_job_newer") < result.output.index("batch_job_older")
        assert "42.5%" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches").mock(return_value=httpx.Response(200, json=[_BATCH_JOB_OLDER, _BATCH_JOB]))
        result = cli_runner.invoke(["batches", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert [row["id"] for row in parsed] == ["batch_job_newer", "batch_job_older"]

    @pytest.mark.respx(base_url=base_url)
    def test_ls_alias(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches").mock(return_value=httpx.Response(200, json=[]))
        result = cli_runner.invoke(["batches", "ls"])
        assert result.exit_code == 0
        assert "tg batches submit" in result.output


class TestBatchesRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        result = cli_runner.invoke(["batches", "retrieve", "batch_job_newer", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["id"] == "batch_job_newer"
        assert body["status"] == "COMPLETED"
        assert body["model_id"] == "Qwen/Qwen3.5-9B"

    @pytest.mark.respx(base_url=base_url)
    def test_get_alias(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        result = cli_runner.invoke(["batches", "get", "batch_job_newer", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["id"] == "batch_job_newer"

    @pytest.mark.respx(base_url=base_url)
    def test_implicit_retrieve_bare_job_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        result = cli_runner.invoke(["batches", "batch_job_newer", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["id"] == "batch_job_newer"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_shows_curated_fields_and_download_hint(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        result = cli_runner.invoke(["batches", "get", "batch_job_newer"])
        assert result.exit_code == 0
        assert "Batch job details:" in result.output
        assert "Completed at" in result.output
        assert "chat.completions" in result.output
        assert "Qwen/Qwen3.5-9B" in result.output
        assert "file-out" in result.output
        assert "tg batches download batch_job_newer --output ./out" in result.output
        # Raw dump fields that shouldn't clutter the human view
        assert "file_size_bytes" not in result.output
        assert "input_file_id" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_shows_progress_when_in_progress(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_older").mock(return_value=httpx.Response(200, json=_BATCH_JOB_OLDER))
        result = cli_runner.invoke(["batches", "get", "batch_job_older"])
        assert result.exit_code == 0
        assert "In_progress" in result.output
        assert "42.5%" in result.output
        assert "audio.transcriptions" in result.output
        assert "tg batches download" not in result.output

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            ("CANCELLED", "Cancelled"),
            ("EXPIRED", "Expired"),
            ("FAILED", "Failed"),
            ("COMPLETED", "Completed"),
        ],
    )
    def test_retrieve_always_prints_status(
        self, status: str, expected: str, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        job = {**_BATCH_JOB, "status": status, "error": None, "error_file_id": None}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "get", "batch_job_newer"])
        assert result.exit_code == 0
        assert any(line.strip() == expected for line in result.output.splitlines())
        assert "█" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_prints_status_when_in_progress_without_progress(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        job = {**_BATCH_JOB_OLDER, "progress": None}
        respx_mock.get("/batches/batch_job_older").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "get", "batch_job_older"])
        assert result.exit_code == 0
        assert "In_progress" in result.output
        assert "█" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_error_header_printed_once(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        job = {
            **_BATCH_JOB,
            "status": "FAILED",
            "error": "boom",
            "error_file_id": "file-err",
        }
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "get", "batch_job_newer"])
        assert result.exit_code == 0
        assert result.output.count("An error occurred") == 1
        assert "file-err" in result.output
        assert "boom" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_escapes_error_markup(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        job = {**_BATCH_JOB, "status": "FAILED", "error": "validation failed: missing [/close] tag"}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "get", "batch_job_newer"])
        assert result.exit_code == 0
        assert "MarkupError" not in result.output
        assert "close" in result.output


class TestBatchesCancel:
    @pytest.mark.respx(base_url=base_url)
    def test_cancel(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        cancelled = {**_BATCH_JOB, "status": "CANCELLED"}
        respx_mock.post("/batches/batch_job_newer/cancel").mock(return_value=httpx.Response(200, json=cancelled))
        result = cli_runner.invoke(["batches", "cancel", "batch_job_newer"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output
        assert "X Model Id" not in result.output
        assert "Qwen/Qwen3.5-9B" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        cancelled = {**_BATCH_JOB, "status": "CANCELLED"}
        respx_mock.post("/batches/batch_job_newer/cancel").mock(return_value=httpx.Response(200, json=cancelled))
        result = cli_runner.invoke(["batches", "cancel", "batch_job_newer", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["status"] == "CANCELLED"


class TestBatchesDownload:
    @pytest.mark.respx(base_url=base_url)
    def test_download_not_ready(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_older").mock(return_value=httpx.Response(200, json=_BATCH_JOB_OLDER))
        result = cli_runner.invoke(["batches", "download", "batch_job_older", "--output", str(tmp_path)])
        assert result.exit_code == 1
        assert "not ready" in result.output.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_download_output_to_directory(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        job = {**_BATCH_JOB, "error_file_id": "file-err"}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b'{"ok":true}\n'))
        respx_mock.get("/files/file-err/content").mock(return_value=httpx.Response(200, content=b'{"err":true}\n'))
        respx_mock.get("/files/file-out").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "file-out",
                    "bytes": 12,
                    "created_at": 1,
                    "filename": "batch-output.jsonl",
                    "FileType": "jsonl",
                    "object": "file",
                    "Processed": True,
                    "purpose": "batch-api",
                },
            )
        )

        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--output", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "batch-output.jsonl").read_bytes() == b'{"ok":true}\n'
        assert (tmp_path / "batch-output.errors.jsonl").read_bytes() == b'{"err":true}\n'
        assert "Output saved" in result.output
        assert "Errors saved" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_download_directory_disambiguates_identical_filenames(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        job = {**_BATCH_JOB, "error_file_id": "file-err"}
        file_meta = {
            "bytes": 12,
            "created_at": 1,
            "filename": "batch.jsonl",
            "FileType": "jsonl",
            "object": "file",
            "Processed": True,
            "purpose": "batch-api",
        }
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b'{"ok":true}\n'))
        respx_mock.get("/files/file-err/content").mock(return_value=httpx.Response(200, content=b'{"err":true}\n'))
        respx_mock.get("/files/file-out").mock(return_value=httpx.Response(200, json={"id": "file-out", **file_meta}))

        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--output", str(tmp_path), "--json"])
        assert result.exit_code == 0
        assert (tmp_path / "batch.jsonl").read_bytes() == b'{"ok":true}\n'
        assert (tmp_path / "batch.errors.jsonl").read_bytes() == b'{"err":true}\n'
        body = json.loads(result.output)
        paths = [item["path"] for item in body["files"]]
        assert paths[0] != paths[1]
        assert Path(paths[0]).name == "batch.jsonl"
        assert Path(paths[1]).name == "batch.errors.jsonl"

    @pytest.mark.respx(base_url=base_url)
    def test_download_output_to_file(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        job = {**_BATCH_JOB, "error_file_id": "file-err"}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b'{"ok":true}\n'))
        respx_mock.get("/files/file-err/content").mock(return_value=httpx.Response(200, content=b'{"err":true}\n'))

        out = tmp_path / "results.jsonl"
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--output", str(out)])
        assert result.exit_code == 0
        assert out.read_bytes() == b'{"ok":true}\n'
        assert (tmp_path / "results.errors.jsonl").read_bytes() == b'{"err":true}\n'
        assert "Output saved" in result.output
        assert "Errors saved" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_download_defaults_to_stdout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b"stdout-batch\n"))
        result = cli_runner.invoke(["batches", "download", "batch_job_newer"])
        assert result.exit_code == 0
        assert "stdout-batch" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_download_json(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b"line\n"))
        respx_mock.get("/files/file-out").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "file-out",
                    "bytes": 5,
                    "created_at": 1,
                    "filename": "out.jsonl",
                    "FileType": "jsonl",
                    "object": "file",
                    "Processed": True,
                    "purpose": "batch-api",
                },
            )
        )
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--output", str(tmp_path), "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["batch_id"] == "batch_job_newer"
        assert body["files"][0]["kind"] == "output"
        assert body["files"][0]["id"] == "file-out"
        assert Path(body["files"][0]["path"]).read_bytes() == b"line\n"

    @pytest.mark.respx(base_url=base_url)
    def test_download_existing_suffixless_file(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        out = tmp_path / "results"
        out.write_bytes(b"stale")
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        respx_mock.get("/files/file-out/content").mock(return_value=httpx.Response(200, content=b'{"ok":true}\n'))
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--output", str(out)])
        assert result.exit_code == 0
        assert out.is_file()
        assert out.read_bytes() == b'{"ok":true}\n'

    @pytest.mark.respx(base_url=base_url)
    def test_download_not_ready_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/batches/batch_job_older").mock(return_value=httpx.Response(200, json=_BATCH_JOB_OLDER))
        result = cli_runner.invoke(["batches", "download", "batch_job_older", "--json"])
        assert result.exit_code == 1
        body = json.loads(result.output)
        assert "not ready" in body["error"].lower()

    @pytest.mark.respx(base_url=base_url)
    def test_download_no_files_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        job = {**_BATCH_JOB, "output_file_id": None, "error_file_id": None}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--json"])
        assert result.exit_code == 1
        body = json.loads(result.output)
        assert "no output or error files" in body["error"].lower()

    @pytest.mark.respx(base_url=base_url)
    def test_download_json_without_output_requires_output_flag(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=_BATCH_JOB))
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--json"])
        assert result.exit_code == 1
        body = json.loads(result.output)
        assert "--output" in body["error"]
        assert "stdout" in body["error"]

    @pytest.mark.respx(base_url=base_url)
    def test_download_stdout_no_output_file_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        job = {**_BATCH_JOB, "output_file_id": None, "error_file_id": "file-err"}
        respx_mock.get("/batches/batch_job_newer").mock(return_value=httpx.Response(200, json=job))
        result = cli_runner.invoke(["batches", "download", "batch_job_newer", "--json"])
        assert result.exit_code == 1
        body = json.loads(result.output)
        assert "no output file" in body["error"].lower()
