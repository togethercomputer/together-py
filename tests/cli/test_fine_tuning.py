from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from click.testing import CliRunner

from together.lib.cli import main

# Real module; package attribute `download` is the Click command and shadows this name.
_ft_download_mod = sys.modules["together.lib.cli.api.fine_tuning.download"]

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"

_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}

_FT_LIST_ITEM = {
    "id": "ft-newer",
    "created_at": "2024-06-02T12:00:00Z",
    "updated_at": "2024-06-02T12:00:00Z",
    "status": "completed",
    "total_price": 200,
    "model": "meta-llama/Llama-3-8b",
    "suffix": "my-run",
}

_FT_LIST_ITEM_OLDER = {
    "id": "ft-older",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "status": "running",
    "total_price": 50,
    "model": "meta-llama/Llama-3-8b",
    "suffix": "",
    "progress": {"estimate_available": True, "seconds_remaining": 120},
}

_FT_RETRIEVE_BODY = {
    "id": "ft-1",
    "status": "completed",
    "training_type": {"type": "Full"},
    "model_output_name": "weights.tar",
    "created_at": "2024-01-01T00:00:00Z",
    "started_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T01:00:00Z",
}

_FT_EVENT = {
    "checkpoint_path": "/ckpt",
    "created_at": "2024-01-01T00:00:00Z",
    "hash": "abc",
    "message": "training started",
    "model_path": "/m",
    "object": "fine-tune-event",
    "param_count": 7,
    "step": 0,
    "token_count": 0,
    "total_steps": 10,
    "training_offset": 0,
    "type": "training_start",
    "wandb_url": "",
}

_FT_CHECKPOINT = {
    "checkpoint_type": "intermediate",
    "created_at": "2024-01-01T00:00:00Z",
    "path": "/p",
    "step": 5,
}


class TestFineTuningList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes").mock(
            return_value=httpx.Response(200, json={"data": [_FT_LIST_ITEM_OLDER, _FT_LIST_ITEM]})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "list"])
        assert result.exit_code == 0
        assert "ft-newer" in result.output
        assert "ft-older" in result.output
        assert result.output.index("ft-newer") < result.output.index("ft-older")

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes").mock(
            return_value=httpx.Response(200, json={"data": [_FT_LIST_ITEM_OLDER, _FT_LIST_ITEM]})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert [x["id"] for x in parsed] == ["ft-newer", "ft-older"]


class TestFineTuningRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=_FT_RETRIEVE_BODY))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "retrieve", "ft-1", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["id"] == "ft-1"
        assert body["status"] == "completed"


class TestFineTuningCancel:
    @pytest.mark.respx(base_url=base_url)
    def test_cancel_not_cancellable(self, respx_mock: MockRouter) -> None:
        body = {**_FT_RETRIEVE_BODY, "status": "completed"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "cancel", "ft-1", "--quiet"])
        assert result.exit_code == 0
        assert "not currently cancellable" in result.output
        assert "completed" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_quiet_calls_api(self, respx_mock: MockRouter) -> None:
        running = {**_FT_RETRIEVE_BODY, "status": "running"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=running))
        respx_mock.post("/fine-tunes/ft-1/cancel").mock(
            return_value=httpx.Response(200, json={**running, "status": "cancel_requested"})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "cancel", "ft-1", "--quiet"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_json_requires_quiet(self, respx_mock: MockRouter) -> None:
        running = {**_FT_RETRIEVE_BODY, "status": "running"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=running))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "cancel", "ft-1", "--json"])
        assert result.exit_code != 0
        assert "quiet" in result.output.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_not_cancellable_json(self, respx_mock: MockRouter) -> None:
        body = {**_FT_RETRIEVE_BODY, "status": "completed"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        try:
            runner = CliRunner(env=_ENV, mix_stderr=False)
        except Exception:
            # Python 3.14 doesnt have the mix_stderr parameter
            runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "cancel", "ft-1", "--quiet", "--json"])
        assert result.exit_code == 0
        assert result.stdout_bytes.decode("utf-8") == ""
        assert result.stderr_bytes is not None
        assert len(result.stderr_bytes) > 0
        assert "Training is not currently cancellable" in result.stderr_bytes.decode("utf-8")


class TestFineTuningDelete:
    def test_delete_json_requires_force(self) -> None:
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "delete", "ft-1", "--json"])
        assert result.exit_code != 0
        assert "force" in result.output.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_delete_force(self, respx_mock: MockRouter) -> None:
        respx_mock.delete("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json={"message": "deleted"}))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "delete", "ft-1", "--force"])
        assert result.exit_code == 0
        assert "Deleted" in result.output


class TestFineTuningEventsAndCheckpoints:
    @pytest.mark.respx(base_url=base_url)
    def test_list_events_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes/ft-1/events").mock(return_value=httpx.Response(200, json={"data": [_FT_EVENT]}))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "list-events", "ft-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)[0]["message"] == "training started"

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_table(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(
            return_value=httpx.Response(200, json={"data": [_FT_CHECKPOINT]})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "ft-1:5" in result.output
        assert "intermediate" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_empty_message(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(return_value=httpx.Response(200, json={"data": []}))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "No checkpoints found" in result.output


class TestFineTuningDownload:
    @pytest.mark.respx(base_url=base_url)
    def test_download_invokes_download_manager(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        respx_mock.get("/fine-tunes/ft-abcd-12").mock(return_value=httpx.Response(200, json=_FT_RETRIEVE_BODY))
        out_file = tmp_path / "weights.tar"
        out_file.write_bytes(b"x")

        class _DM:
            def __init__(self, _client: object) -> None:
                pass

            def download(self, **kwargs: object) -> tuple[str, int]:
                assert "ft_id=ft-abcd-12" in str(kwargs.get("url", ""))
                assert "checkpoint=model_output_path" in str(kwargs.get("url", ""))
                return str(out_file), 1

        with patch.object(_ft_download_mod, "DownloadManager", _DM):
            runner = CliRunner(env=_ENV)
            # Full fine-tunes require explicit --checkpoint-type default (CLI default is merged for LoRA).
            result = runner.invoke(
                main,
                [
                    "fine-tuning",
                    "download",
                    "ft-abcd-12",
                    "--checkpoint-type",
                    "default",
                    "--output_dir",
                    str(tmp_path),
                ],
            )
        assert result.exit_code == 0
        payload = json.loads(result.output.strip())
        assert payload["id"] == "ft-abcd-12"
        assert payload["size"] == 1
