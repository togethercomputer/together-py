from __future__ import annotations

import os
import json
import importlib
from typing import Any
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner
from together.types.file_response import FileResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

API_KEY = "0000000000000000000000000000000000000000"

# Load upload submodule explicitly (importing `together.lib.cli.api.files` may not load it).
_files_upload_cli = importlib.import_module("together.lib.cli.api.files.upload")

FILE_ROW_NEWER = {
    "id": "file-newer",
    "bytes": 2048,
    "created_at": 1700000000,
    "filename": "newer.jsonl",
    "FileType": "jsonl",
    "object": "file",
    "Processed": True,
    "purpose": "fine-tune",
}

FILE_ROW_OLDER = {
    "id": "file-older",
    "bytes": 512,
    "created_at": 1600000000,
    "filename": "older.jsonl",
    "FileType": "jsonl",
    "object": "file",
    "Processed": False,
    "purpose": "eval",
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
        "purpose": "fine-tune",
    }
    defaults.update(kwargs)
    if hasattr(FileResponse, "model_validate"):
        return FileResponse.model_validate(defaults)
    return FileResponse.parse_obj(defaults)  # pyright: ignore[reportDeprecated]


class TestFilesCheck:
    def test_check(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        sample = tmp_path / "ok.jsonl"
        sample.write_text('{"text": "hello"}\n', encoding="utf-8")
        result = cli_runner.invoke(["files", "check", str(sample)])
        assert result.exit_code == 0


class TestFilesDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/files/file-to-delete").mock(
            return_value=httpx.Response(200, json={"id": "file-to-delete", "deleted": True})
        )
        result = cli_runner.invoke(["files", "delete", "file-to-delete"])
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()


class TestFilesList:
    @pytest.mark.respx(base_url=base_url)
    def test_list(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/files").mock(return_value=httpx.Response(200, json={"data": [FILE_ROW_OLDER, FILE_ROW_NEWER]}))
        result = cli_runner.invoke(["files", "list"])
        assert result.exit_code == 0
        assert "file-newer" in result.output
        assert "file-older" in result.output
        newer_pos = result.output.index("file-newer")
        older_pos = result.output.index("file-older")
        assert newer_pos < older_pos

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/files").mock(return_value=httpx.Response(200, json={"data": [FILE_ROW_OLDER, FILE_ROW_NEWER]}))
        result = cli_runner.invoke(["files", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert [row["id"] for row in parsed] == ["file-newer", "file-older"]


class TestFilesRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/files/file-meta").mock(return_value=httpx.Response(200, json=FILE_ROW_NEWER))
        result = cli_runner.invoke(["files", "retrieve", "file-meta"])
        assert result.exit_code == 0
        assert "newer.jsonl" in result.output
        assert "fine-tune" in result.output


class TestFilesRetrieveContent:
    def test_retrieve_content_no_options(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["files", "retrieve-content", "file-1"])
        assert result.exit_code == 1
        assert "Either --output" in result.output or "must be specified" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_output(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"line1\nline2\n"))
        out = tmp_path / "saved.jsonl"
        result = cli_runner.invoke(["files", "retrieve-content", "file-1", "--output", str(out)])
        assert result.exit_code == 0
        assert out.read_bytes() == b"line1\nline2\n"
        # Rich may soft-wrap long paths across lines
        assert str(out) in result.output.replace("\n", "")

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_stdout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"stdout-bytes"))
        result = cli_runner.invoke(["files", "retrieve-content", "file-1", "--stdout"])
        assert result.exit_code == 0
        assert result.output == "stdout-bytes\n"

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_both_output_and_stdout(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"to-stdout"))
        out = tmp_path / "should-not-exist.bin"
        result = cli_runner.invoke(["files", "retrieve-content", "file-1", "--stdout", "--output", str(out)])
        assert result.exit_code == 0
        assert result.output.startswith("to-stdout\n")
        assert "File saved to" in result.output
        assert str(out) in result.output.replace("\n", "")
        assert out.exists()


class TestFilesUpload:
    def test_upload_with_invalid_purpose(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        f = tmp_path / "empty.jsonl"
        f.write_text("{}\n")
        invalid_purpose = "not-a-real-purpose"
        with patch("together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock) as upload_mock:
            result = cli_runner.invoke(["files", "upload", str(f), "--purpose", invalid_purpose])
            assert result.exit_code == 1
            assert invalid_purpose in result.output
            assert "--purpose" in result.output
        upload_mock.assert_not_called()

    def test_upload_does_check_by_default(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock
        ) as upload_mock:
            check_mock.return_value = {"is_check_passed": False, "message": "failed validation"}
            result = cli_runner.invoke(["files", "upload", str(f)])
        assert result.exit_code == 1
        check_mock.assert_called_once()
        upload_mock.assert_not_called()

    def test_upload_does_not_check_if_disabled(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        uploaded = _file_response(id="uploaded-id", purpose="fine-tune")
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock
        ) as upload_mock:
            upload_mock.return_value = uploaded
            result = cli_runner.invoke(["files", "upload", str(f), "--no-check"])
        assert result.exit_code == 0
        check_mock.assert_not_called()
        upload_mock.assert_called_once()
        call_kw = upload_mock.call_args.kwargs
        assert call_kw["check"] is False
        assert "uploaded-id" in result.output

    def test_upload_does_check_if_enabled(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        uploaded = _file_response()
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock
        ) as upload_mock:
            upload_mock.return_value = uploaded
            check_mock.return_value = {"is_check_passed": True, "message": "Checks passed"}
            result = cli_runner.invoke(["files", "upload", str(f), "--check"])
        assert result.exit_code == 0
        check_mock.assert_called_once()
        upload_mock.assert_called_once()
