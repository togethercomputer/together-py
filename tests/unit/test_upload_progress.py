from __future__ import annotations

from typing import Any
from pathlib import Path

import pytest

from together.lib import FileTypeError
from together.lib.cli.components.upload_progress import upload_file_with_progress


async def test_upload_file_with_progress_validates_before_upload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file = tmp_path / "data.jsonl"
    file.write_text('{"text": "hello"}\n')
    order: list[str] = []

    def fake_check_file(*_args: object, **_kwargs: object) -> dict[str, Any]:
        order.append("check")
        return {"is_check_passed": True, "message": "Checks passed"}

    async def fake_upload(**kwargs: object) -> str:
        order.append("upload")
        assert kwargs["check"] is False
        return "ok"

    monkeypatch.setattr("together.lib.cli.components.upload_progress.check_file", fake_check_file)

    result = await upload_file_with_progress(fake_upload, file, enabled=False, description="Uploading")
    assert result == "ok"
    assert order == ["check", "upload"]


async def test_upload_file_with_progress_skips_check_when_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file = tmp_path / "data.jsonl"
    file.write_text('{"text": "hello"}\n')

    def fake_check_file(*_args: object, **_kwargs: object) -> dict[str, Any]:
        raise AssertionError("check_file should not run when check=False")

    async def fake_upload(**kwargs: object) -> str:
        assert kwargs["check"] is False
        return "ok"

    monkeypatch.setattr("together.lib.cli.components.upload_progress.check_file", fake_check_file)

    result = await upload_file_with_progress(fake_upload, file, enabled=False, check=False)
    assert result == "ok"


async def test_upload_file_with_progress_failed_check_does_not_upload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file = tmp_path / "data.jsonl"
    file.write_text("{}\n")
    uploaded = False

    def fake_check_file(*_args: object, **_kwargs: object) -> dict[str, Any]:
        return {"is_check_passed": False, "message": "nope"}

    async def fake_upload(**_kwargs: object) -> str:
        nonlocal uploaded
        uploaded = True
        return "ok"

    monkeypatch.setattr("together.lib.cli.components.upload_progress.check_file", fake_check_file)

    with pytest.raises(FileTypeError, match="nope"):
        await upload_file_with_progress(fake_upload, file, enabled=False)
    assert uploaded is False


def test_upload_progress_tracker_skips_render_when_not_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from together.lib.cli.components import upload_progress as upload_progress_mod
    from together.lib.cli.components.upload_progress import UploadProgressTracker

    class _NonTerminalConsole:
        is_terminal = False

    monkeypatch.setattr(upload_progress_mod, "console", _NonTerminalConsole())
    file = tmp_path / "data.jsonl"
    file.write_text("{}\n")
    with UploadProgressTracker.for_single_file(file, enabled=True) as tracker:
        assert tracker._progress is None
        assert tracker.as_callback() is not None


async def test_upload_progress_prints_completion_under_debug(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from together.lib.cli.utils import _debug
    from together.lib.cli.components import upload_progress as upload_progress_mod
    from together.lib.cli.components.upload_progress import UploadProgressTracker

    monkeypatch.setattr(_debug, "_enabled", True)
    printed: list[str] = []

    class _TerminalConsole:
        is_terminal = True

        def print(self, message: object, *_args: object, **_kwargs: object) -> None:
            printed.append(str(message))

    monkeypatch.setattr(upload_progress_mod, "console", _TerminalConsole())
    file = tmp_path / "weights.bin"
    file.write_bytes(b"x" * 8)
    tracker = UploadProgressTracker(
        total_bytes=8,
        total_parts=1,
        total_files=1,
        enabled=True,
    )
    with tracker:
        assert tracker._progress is None
        await tracker.part_completed(
            file_path="weights.bin",
            part_number=1,
            total_file_parts=1,
            bytes_count=8,
        )
        await tracker.file_completed("weights.bin")
    assert any("weights.bin part 1/1" in line for line in printed)
    assert any("weights.bin complete" in line for line in printed)


async def test_download_progress_prints_completion_under_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    from together.lib.cli.utils import _debug
    from together.lib.cli.components import download_progress as download_progress_mod
    from together.lib.cli.components.download_progress import DownloadProgressTracker

    monkeypatch.setattr(_debug, "_enabled", True)
    printed: list[str] = []

    class _TerminalConsole:
        is_terminal = True

        def print(self, message: object, *_args: object, **_kwargs: object) -> None:
            printed.append(str(message))

    monkeypatch.setattr(download_progress_mod, "console", _TerminalConsole())
    tracker = DownloadProgressTracker(total_bytes=10, total_files=2, enabled=True)
    with tracker:
        assert tracker._progress is None
        await tracker.file_completed("a.bin")
        await tracker.file_completed("b.bin", skipped=True)
    assert any("a.bin complete" in line for line in printed)
    assert any("b.bin skipped" in line for line in printed)


def test_download_progress_tracker_skips_render_when_not_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    from together.lib.cli.components import download_progress as download_progress_mod
    from together.lib.cli.components.download_progress import DownloadProgressTracker

    class _NonTerminalConsole:
        is_terminal = False

    monkeypatch.setattr(download_progress_mod, "console", _NonTerminalConsole())
    with DownloadProgressTracker.for_single_file(enabled=True, total_bytes=10) as tracker:
        assert tracker._progress is None
        assert tracker.as_callback() is not None
