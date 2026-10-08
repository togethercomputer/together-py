from __future__ import annotations

import os
import json
import importlib
from types import SimpleNamespace
from typing import Any, cast
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

_fp4_utils = importlib.import_module("together.lib.cli.api.training.prepare_for_fp4_inference._utils")

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

_ADAPTER_ID = "ml_adapter"
_JOB_ID = "shp-quant-1"

_ESTIMATE_BODY = {
    "allowed_to_proceed": True,
    "credit_limit": 100.0,
    "price_usd": 12.5,
    "time_hours": 1.5,
}

_EVENT = {
    "created_at": "2026-01-01T00:01:00Z",
    "level": "Info",
    "message": "Quantization job started",
    "object": "shaping",
    "type": "QUANTIZATION_JOB_START",
    "hash": "h1",
}


def _job(status: str, events: list[dict[str, Any]] | None = None, **extra: Any) -> dict[str, Any]:
    return {
        "id": _JOB_ID,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "events": events or [],
        "job_type": "quantization",
        "status": status,
        "user_id": "user-1",
        "params": {
            "inputs": {"adapter_object_id": _ADAPTER_ID},
            "configuration": {
                "adapter_model_name": "proj/my-adapter",
                "adapter_project_id": "proj",
                "adapter_revision_id": "rv_adapter",
                "base_model_name": "org/base",
                "base_object_id": "ml_base",
                "base_revision_id": "rv_base",
                "user_id": "user-1",
            },
        },
        **extra,
    }


class TestEstimate:
    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        ("calibration_args", "expected_calibration"),
        [([], None), (["-c", "file-calib"], "file-calib"), (["-c", "LOCAL_PATH"], "file-uploaded")],
    )
    def test_estimate_sends_inputs(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
        calibration_args: list[str],
        expected_calibration: str | None,
    ) -> None:
        local_path = tmp_path / "calib.jsonl"
        local_path.write_text('{"messages": [{"role": "user", "content": "hi"}]}\n')
        args = [str(local_path) if arg == "LOCAL_PATH" else arg for arg in calibration_args]
        route = respx_mock.post("/shaping/prepare-for-fp4-inference/estimate").mock(
            return_value=httpx.Response(200, json=_ESTIMATE_BODY)
        )
        upload = AsyncMock(return_value=SimpleNamespace(id="file-uploaded"))
        with patch.object(_fp4_utils, "upload_file_with_progress", upload):
            result = cli_runner.invoke(["training", "fp4", "estimate", _ADAPTER_ID, "-r", "rv_1", *args, "--json"])

        assert result.exit_code == 0
        expected_inputs = {"adapter_object_id": _ADAPTER_ID, "adapter_revision_id": "rv_1"}
        if expected_calibration is not None:
            expected_inputs["calibration_file_id"] = expected_calibration
        assert json.loads(cast(Call, route.calls[0]).request.content) == {"inputs": expected_inputs}
        assert upload.await_count == (1 if expected_calibration == "file-uploaded" else 0)
        if upload.await_count:
            assert upload.await_args is not None
            assert upload.await_args.kwargs["purpose"] == "calibration"
        assert json.loads(result.output)["price_usd"] == 12.5


class TestCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_estimates_then_submits(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/shaping/prepare-for-fp4-inference/estimate").mock(
            return_value=httpx.Response(200, json=_ESTIMATE_BODY)
        )
        create = respx_mock.post("/shaping/prepare-for-fp4-inference").mock(
            return_value=httpx.Response(200, json=_job("pending"))
        )
        result = cli_runner.invoke(["training", "fp4", "create", _ADAPTER_ID, "--non-interactive"])
        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "$12.50" in output
        assert create.called
        assert json.loads(cast(Call, create.calls[0]).request.content) == {"inputs": {"adapter_object_id": _ADAPTER_ID}}
        assert f"tg training fp4 get {_JOB_ID} --watch" in output

    @pytest.mark.respx(base_url=base_url)
    def test_create_json_emits_only_the_job(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/shaping/prepare-for-fp4-inference/estimate").mock(
            return_value=httpx.Response(200, json=_ESTIMATE_BODY)
        )
        respx_mock.post("/shaping/prepare-for-fp4-inference").mock(
            return_value=httpx.Response(200, json=_job("pending"))
        )
        result = cli_runner.invoke(["training", "fp4", "create", _ADAPTER_ID, "--json"])
        assert result.exit_code == 0
        assert json.loads(result.out_out)["id"] == _JOB_ID

    @pytest.mark.respx(base_url=base_url)
    def test_create_warns_but_submits_when_estimate_not_allowed(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.post("/shaping/prepare-for-fp4-inference/estimate").mock(
            return_value=httpx.Response(200, json={**_ESTIMATE_BODY, "allowed_to_proceed": False})
        )
        create = respx_mock.post("/shaping/prepare-for-fp4-inference").mock(
            return_value=httpx.Response(200, json=_job("pending"))
        )
        result = cli_runner.invoke(["training", "fp4", "create", _ADAPTER_ID, "-c", "file-calib", "--non-interactive"])
        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "exceeds your available credit (limit $100.00)" in output
        assert "Calibration file: file-calib" in output
        assert json.loads(cast(Call, create.calls[0]).request.content) == {
            "inputs": {"adapter_object_id": _ADAPTER_ID, "calibration_file_id": "file-calib"}
        }

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_create_rejects_missing_local_calibration_file(
        self, respx_mock: MockRouter, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        estimate = respx_mock.post("/shaping/prepare-for-fp4-inference/estimate")
        result = cli_runner.invoke(
            ["training", "fp4", "create", _ADAPTER_ID, "-c", str(tmp_path / "missing.jsonl"), "-y"]
        )
        assert result.exit_code != 0
        assert "does not exist" in " ".join(result.output.split())
        assert not estimate.called

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(("final_status", "exit_code"), [("completed", 0), ("error", 1)])
    def test_create_watch_follows_to_terminal_status(
        self, respx_mock: MockRouter, cli_runner: CliRunner, final_status: str, exit_code: int
    ) -> None:
        respx_mock.post("/shaping/prepare-for-fp4-inference/estimate").mock(
            return_value=httpx.Response(200, json=_ESTIMATE_BODY)
        )
        respx_mock.post("/shaping/prepare-for-fp4-inference").mock(
            return_value=httpx.Response(200, json=_job("pending"))
        )
        results = {"model_object_id": "ml_prepared", "model_revision_id": "rv_prepared"}
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                httpx.Response(200, json=_job("running", [_EVENT])),
                httpx.Response(200, json=_job(final_status, [_EVENT], results=results)),
            ]
        )
        result = cli_runner.invoke(
            ["training", "fp4", "create", _ADAPTER_ID, "-y", "--watch", "--poll-interval", "0.01"]
        )
        assert result.exit_code == exit_code
        assert result.output.count("Quantization job started") == 1
        assert f"Status: {final_status}" in result.output
        assert ("ml_prepared" in result.output) == (final_status == "completed")


class TestRetrieveAndList:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(return_value=httpx.Response(200, json=_job("running", [_EVENT])))
        result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["status"] == "running"

    @pytest.mark.respx(base_url=base_url)
    def test_list_sorts_newest_first(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        older = {**_job("completed"), "id": "shp-quant-old", "created_at": "2025-01-01T00:00:00Z"}
        respx_mock.get("/shaping").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [older, _job("running")]})
        )
        result = cli_runner.invoke(["training", "fp4", "list", "--json"])
        assert result.exit_code == 0
        assert [job["id"] for job in json.loads(result.output)] == [_JOB_ID, "shp-quant-old"]

    @pytest.mark.respx(base_url=base_url)
    def test_list_events_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}/events").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [_EVENT]})
        )
        result = cli_runner.invoke(["training", "fp4", "list-events", _JOB_ID, "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)[0]["type"] == "QUANTIZATION_JOB_START"


class TestWatch:
    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize("json_mode", [False, True])
    def test_watch_retries_transient_errors(
        self, respx_mock: MockRouter, cli_runner: CliRunner, json_mode: bool
    ) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                httpx.Response(503, json={"error": {"message": "unavailable"}}),
                httpx.Response(200, json=_job("completed")),
            ]
        )
        args = ["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"]
        result = cli_runner.invoke([*args, "--json"] if json_mode else args)
        assert result.exit_code == 0
        assert "retrying" in result.err_out
        if json_mode:
            assert json.loads(result.out_out)["status"] == "completed"
        else:
            assert "Status: completed" in result.output

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        ("retry_after_ms", "expected_wait"),
        [("20", "0.02s"), ("3600000", "0.05s")],
        ids=["honored", "capped"],
    )
    def test_watch_honors_retry_after(
        self, respx_mock: MockRouter, cli_runner: CliRunner, retry_after_ms: str, expected_wait: str
    ) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                httpx.Response(
                    429, headers={"retry-after-ms": retry_after_ms}, json={"error": {"message": "slow down"}}
                ),
                httpx.Response(200, json=_job("completed")),
            ]
        )
        with patch.object(_fp4_utils, "_MAX_RETRY_DELAY_SECONDS", 0.05):
            result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"])
        assert result.exit_code == 0
        assert f"retrying in {expected_wait}" in result.err_out

    @pytest.mark.respx(base_url=base_url)
    def test_watch_resets_failure_streak_after_success(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        unavailable = httpx.Response(503, json={"error": {"message": "unavailable"}})
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                unavailable,
                unavailable,
                httpx.Response(200, json=_job("running")),
                unavailable,
                httpx.Response(200, json=_job("completed")),
            ]
        )
        # Each failure reads the clock once, 100s apart: failures at 0, 100 and 200.
        # A 150s budget only survives the third failure if the success reset the streak.
        clock = SimpleNamespace(monotonic=iter([0.0, 100.0, 200.0]).__next__)
        with patch.object(_fp4_utils, "time", clock), patch.object(_fp4_utils, "_MAX_TRANSIENT_FAILURE_SECONDS", 150.0):
            result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"])
        assert result.exit_code == 0
        assert "Status: completed" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_watch_prints_resume_hint_on_fatal_error(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                httpx.Response(200, json=_job("running")),
                httpx.Response(403, json={"error": {"message": "forbidden"}}),
            ]
        )
        result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"])
        assert result.exit_code != 0
        assert f"tg training fp4 get {_JOB_ID} --watch" in " ".join(result.output.split())

    @pytest.mark.respx(base_url=base_url)
    def test_watch_omits_resume_hint_when_job_never_read(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            return_value=httpx.Response(404, json={"error": {"message": "not found"}})
        )
        result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"])
        assert result.exit_code != 0
        assert "Resume with" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_watch_gives_up_after_sustained_transient_errors(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(
            side_effect=[
                httpx.Response(200, json=_job("running")),
                httpx.Response(503, json={"error": {"message": "unavailable"}}),
            ]
        )
        with patch.object(_fp4_utils, "_MAX_TRANSIENT_FAILURE_SECONDS", 0.0):
            result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0.01"])
        assert result.exit_code != 0
        assert f"tg training fp4 get {_JOB_ID} --watch" in " ".join(result.output.split())

    def test_watch_rejects_non_positive_poll_interval(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["training", "fp4", "get", _JOB_ID, "--watch", "--poll-interval", "0"])
        assert result.exit_code != 0
        assert "poll-interval" in result.output


class TestCancel:
    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_cancel_not_cancellable(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(return_value=httpx.Response(200, json=_job("completed")))
        cancel = respx_mock.post(f"/shaping/{_JOB_ID}/cancel")
        result = cli_runner.invoke(["training", "fp4", "cancel", _JOB_ID, "-y"])
        assert result.exit_code == 1
        assert "not currently cancellable" in result.output
        assert not cancel.called

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_force_calls_api(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"/shaping/{_JOB_ID}").mock(return_value=httpx.Response(200, json=_job("running")))
        cancel = respx_mock.post(f"/shaping/{_JOB_ID}/cancel").mock(
            return_value=httpx.Response(200, json=_job("cancel_requested"))
        )
        result = cli_runner.invoke(["training", "fp4", "cancel", _JOB_ID, "-y"])
        assert result.exit_code == 0
        assert cancel.called
        assert "Cancellation requested" in result.output
