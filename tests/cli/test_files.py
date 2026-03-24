from __future__ import annotations

import os
import sys
import json
from typing import Any
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from click.testing import CliRunner

from together.lib.cli import main
from together.types.file_response import FileResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

API_KEY = "0000000000000000000000000000000000000000"

# Submodule path; package attribute `upload` is the Click command and shadows this module.
_files_upload_cli = sys.modules["together.lib.cli.api.files.upload"]

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
    def test_check(self, tmp_path: Path) -> None:
        sample = tmp_path / "ok.jsonl"
        sample.write_text('{"text": "hello"}\n', encoding="utf-8")
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "check", str(sample)])
        assert result.exit_code == 0


class TestFilesDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete(self, respx_mock: MockRouter) -> None:
        respx_mock.delete("/files/file-to-delete").mock(
            return_value=httpx.Response(200, json={"id": "file-to-delete", "deleted": True})
        )
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "delete", "file-to-delete"])
        assert result.exit_code == 0
        assert "file-to-delete" in result.output
        assert "deleted" in result.output.lower()


class TestFilesList:
    @pytest.mark.respx(base_url=base_url)
    def test_list(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/files").mock(return_value=httpx.Response(200, json={"data": [FILE_ROW_OLDER, FILE_ROW_NEWER]}))
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "list"])
        assert result.exit_code == 0
        assert "file-newer" in result.output
        assert "file-older" in result.output
        newer_pos = result.output.index("file-newer")
        older_pos = result.output.index("file-older")
        assert newer_pos < older_pos

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/files").mock(return_value=httpx.Response(200, json={"data": [FILE_ROW_OLDER, FILE_ROW_NEWER]}))
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert [row["id"] for row in parsed] == ["file-newer", "file-older"]


class TestFilesRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/file-meta").mock(return_value=httpx.Response(200, json=FILE_ROW_NEWER))
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "retrieve", "file-meta"])
        assert result.exit_code == 0
        assert "newer.jsonl" in result.output
        assert "fine-tune" in result.output


class TestFilesRetrieveContent:
    def test_retrieve_content_no_options(self) -> None:
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "retrieve-content", "file-1"])
        assert result.exit_code == 2
        assert "Either --output" in result.output or "must be specified" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_output(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"line1\nline2\n"))
        out = tmp_path / "saved.jsonl"
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "retrieve-content", "file-1", "--output", str(out)])
        assert result.exit_code == 0
        assert out.read_bytes() == b"line1\nline2\n"
        assert str(out) in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_stdout(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"stdout-bytes"))
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(main, ["files", "retrieve-content", "file-1", "--stdout"])
        assert result.exit_code == 0
        assert result.output == "stdout-bytes\n"

    @pytest.mark.respx(base_url=base_url)
    def test_specifying_both_output_and_stdout(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        respx_mock.get("/files/file-1/content").mock(return_value=httpx.Response(200, content=b"to-stdout"))
        out = tmp_path / "should-not-exist.bin"
        runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
        result = runner.invoke(
            main,
            ["files", "retrieve-content", "file-1", "--stdout", "--output", str(out)],
        )
        assert result.exit_code == 0
        assert result.output == "to-stdout\n"
        assert not out.exists()


class TestFilesUpload:
    def test_upload_with_invalid_purpose(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.jsonl"
        f.write_text("{}\n")
        with patch("together.resources.files.FilesResource.upload") as upload_mock:
            runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
            result = runner.invoke(
                main,
                ["files", "upload", str(f), "--purpose", "not-a-real-purpose"],
            )
        assert result.exit_code == 2
        upload_mock.assert_not_called()

    def test_upload_does_check_by_default(self, tmp_path: Path) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.FilesResource.upload"
        ) as upload_mock:
            check_mock.return_value = {"is_check_passed": False, "message": "failed validation"}
            runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
            result = runner.invoke(main, ["files", "upload", str(f)])
        assert result.exit_code == 1
        check_mock.assert_called_once()
        upload_mock.assert_not_called()

    def test_upload_does_not_check_if_disabled(self, tmp_path: Path) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        uploaded = _file_response(id="uploaded-id", purpose="fine-tune")
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.FilesResource.upload", return_value=uploaded
        ) as upload_mock:
            runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
            result = runner.invoke(main, ["files", "upload", str(f), "--no-check"])
        assert result.exit_code == 0
        check_mock.assert_not_called()
        upload_mock.assert_called_once()
        call_kw = upload_mock.call_args.kwargs
        assert call_kw["check"] is False
        assert "uploaded-id" in result.output

    def test_upload_does_check_if_enabled(self, tmp_path: Path) -> None:
        f = tmp_path / "data.jsonl"
        f.write_text("{}\n")
        uploaded = _file_response()
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.FilesResource.upload", return_value=uploaded
        ) as upload_mock:
            check_mock.return_value = {"is_check_passed": True, "message": "Checks passed"}
            runner = CliRunner(env={"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY})
            result = runner.invoke(main, ["files", "upload", str(f), "--check"])
        assert result.exit_code == 0
        check_mock.assert_called_once()
        upload_mock.assert_called_once()
