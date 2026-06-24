from __future__ import annotations

import os
import json
import importlib
from typing import cast
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

_ft_download_mod = importlib.import_module("together.lib.cli.api.fine_tuning.download")

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

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

_FT_METRICS_BODY = {
    "metrics": [
        {
            "global_step": 0,
            "train_loss": 1.25,
            "logged_at": "2024-01-01T00:00:00Z",
        }
    ]
}

_MODEL_LIMITS_BODY = {
    "max_num_epochs": 10,
    "max_learning_rate": 1,
    "min_learning_rate": 0,
    "min_max_seq_length": 1,
    "max_seq_length_sft": 4096,
    "max_seq_length_dpo": 4096,
}

_FT_CREATE_BODY = {
    "id": "ft-created",
    "status": "pending",
}


class TestFineTuningCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_handles_unavailable_price_estimation(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(
            return_value=httpx.Response(200, json={**_MODEL_LIMITS_BODY, "supports_vision": True})
        )
        estimate = respx_mock.post("/fine-tunes/estimate-price").mock(
            return_value=httpx.Response(
                200,
                json={
                    "estimation_available": False,
                    "unavailable_reason": "multimodal_dataset",
                },
            )
        )
        create = respx_mock.post("/fine-tunes").mock(return_value=httpx.Response(200, json=_FT_CREATE_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "create",
                "--training-file",
                "file-train",
                "--model",
                "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            ],
            input="y\n",
        )

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "not available for multimodal datasets" in output
        assert "Do you want to proceed?" in result.output
        assert "ft-created" in result.output
        assert estimate.calls
        assert create.calls

    @pytest.mark.respx(base_url=base_url)
    def test_create_warns_when_estimated_price_exceeds_funds(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY))
        respx_mock.post("/fine-tunes/estimate-price").mock(
            return_value=httpx.Response(
                200,
                json={
                    "estimated_total_price": 123.45,
                    "allowed_to_proceed": False,
                },
            )
        )
        create = respx_mock.post("/fine-tunes").mock(return_value=httpx.Response(200, json=_FT_CREATE_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "create",
                "--training-file",
                "file-train",
                "--model",
                "meta-llama/Llama-3-8b",
            ],
            input="y\n",
        )

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "The estimated price of this job is $123.45." in output
        assert "insufficient funds" in result.output
        assert create.calls

    @pytest.mark.xfail(
        reason="early_stopping_* create params reach the request only once the generated create() is "
        "regenerated from the OpenAPI spec (openapi -> sdk -> cli flow); xpasses once that lands.",
        strict=False,
    )
    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_create_early_stopping_sends_params(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY))
        respx_mock.post("/fine-tunes/estimate-price").mock(
            return_value=httpx.Response(200, json={"estimated_total_price": 1.0, "allowed_to_proceed": True})
        )
        create = respx_mock.post("/fine-tunes").mock(return_value=httpx.Response(200, json=_FT_CREATE_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "create",
                "--training-file",
                "file-train",
                "--validation-file",
                "file-val",
                "--model",
                "meta-llama/Llama-3-8b",
                "--n-evals",
                "10",
                "--early-stopping-enabled",
                "--early-stopping-patience",
                "3",
                "--early-stopping-warmup-evals",
                "2",
                "--early-stopping-min-delta",
                "0.01",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        assert create.calls
        body = json.loads(create.calls.last.request.content)
        assert body["early_stopping_enabled"] is True
        assert body["early_stopping_patience"] == 3
        assert body["early_stopping_warmup_evals"] == 2
        assert body["early_stopping_min_delta"] == 0.01

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_create_early_stopping_invalid_fails_before_create(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY))
        create = respx_mock.post("/fine-tunes").mock(return_value=httpx.Response(200, json=_FT_CREATE_BODY))

        # default patience(2) + warmup(1) + 1 = 4 > n_evals=3, so this must fail before any create call.
        result = cli_runner.invoke(
            [
                "fine-tuning",
                "create",
                "--training-file",
                "file-train",
                "--validation-file",
                "file-val",
                "--model",
                "meta-llama/Llama-3-8b",
                "--n-evals",
                "3",
                "--early-stopping-enabled",
            ],
            input="y\n",
        )

        assert result.exit_code == 1
        assert "n_evals >= patience" in result.output
        assert not create.calls


class TestFineTuningList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes").mock(
            return_value=httpx.Response(200, json={"data": [_FT_LIST_ITEM_OLDER, _FT_LIST_ITEM]})
        )
        result = cli_runner.invoke(["fine-tuning", "list"])
        assert result.exit_code == 0
        assert "ft-newer" in result.output
        assert "ft-older" in result.output
        assert result.output.index("ft-newer") < result.output.index("ft-older")

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes").mock(
            return_value=httpx.Response(200, json={"data": [_FT_LIST_ITEM_OLDER, _FT_LIST_ITEM]})
        )
        result = cli_runner.invoke(["fine-tuning", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert [x["id"] for x in parsed] == ["ft-newer", "ft-older"]

    @pytest.mark.respx(base_url=base_url)
    def test_ft_alias_list(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes").mock(
            return_value=httpx.Response(200, json={"data": [_FT_LIST_ITEM_OLDER, _FT_LIST_ITEM]})
        )
        result = cli_runner.invoke(["ft", "list"])
        assert result.exit_code == 0
        assert "ft-newer" in result.output


class TestFineTuningRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=_FT_RETRIEVE_BODY))
        result = cli_runner.invoke(["fine-tuning", "retrieve", "ft-1", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["id"] == "ft-1"
        assert body["status"] == "completed"

    @pytest.mark.respx(base_url=base_url)
    def test_implicit_retrieve_bare_job_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=_FT_RETRIEVE_BODY))
        result = cli_runner.invoke(["ft", "ft-1", "--json"])
        assert result.exit_code == 0
        body = json.loads(result.output)
        assert body["id"] == "ft-1"


class TestFineTuningCancel:
    @pytest.mark.respx(base_url=base_url)
    def test_cancel_not_cancellable(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        body = {**_FT_RETRIEVE_BODY, "status": "completed"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        result = cli_runner.invoke(["fine-tuning", "cancel", "ft-1", "--quiet"])
        assert result.exit_code == 1
        assert "not currently cancellable" in result.output
        assert "completed" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_quiet_calls_api(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        running = {**_FT_RETRIEVE_BODY, "status": "running"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=running))
        respx_mock.post("/fine-tunes/ft-1/cancel").mock(
            return_value=httpx.Response(200, json={**running, "status": "cancel_requested"})
        )
        result = cli_runner.invoke(["fine-tuning", "cancel", "ft-1", "--quiet", "--non-interactive"])
        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_cancel_json_requires_non_interactive(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["fine-tuning", "cancel", "ft-1", "--json"])
        assert result.exit_code == 1
        assert "To use json mode, you must use --non-interactive" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_not_cancellable_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        body = {**_FT_RETRIEVE_BODY, "status": "completed"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        result = cli_runner.invoke(["fine-tuning", "cancel", "ft-1", "--quiet", "--json"])
        assert result.exit_code == 1
        assert "Training is not currently cancellable" in result.output


class TestFineTuningDelete:
    def test_delete_json_requires_non_interactive(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["fine-tuning", "delete", "ft-1", "--json"])
        assert result.exit_code != 0
        assert "non-interactive" in result.output.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_delete_force(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json={"message": "deleted"}))
        result = cli_runner.invoke(["fine-tuning", "delete", "ft-1", "--force"])
        assert result.exit_code == 0
        assert "Deleted" in result.output


class TestFineTuningEventsAndCheckpoints:
    @pytest.mark.respx(base_url=base_url)
    def test_list_events_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1/events").mock(return_value=httpx.Response(200, json={"data": [_FT_EVENT]}))
        result = cli_runner.invoke(["fine-tuning", "list-events", "ft-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)[0]["message"] == "training started"

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(
            return_value=httpx.Response(200, json={"data": [_FT_CHECKPOINT]})
        )
        result = cli_runner.invoke(["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "ft-1:5" in result.output
        assert "intermediate" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_empty_message(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(return_value=httpx.Response(200, json={"data": []}))
        result = cli_runner.invoke(["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "No checkpoints found" in result.output


class TestFineTuningListMetrics:
    @pytest.mark.respx(base_url=base_url)
    def test_list_metrics_json_includes_zero_step_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/fine-tunes/ft-1/metrics").mock(return_value=httpx.Response(200, json=_FT_METRICS_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "list-metrics",
                "ft-1",
                "--global-step-from",
                "0",
                "--global-step-to",
                "0",
                "--logged-at-from",
                "2024-01-01T00:00:00+00:00",
                "--logged-at-to",
                "2024-01-02T00:00:00+00:00",
                "--resolution",
                "50",
                "--json",
            ]
        )

        assert result.exit_code == 0
        params = cast(Call, route.calls[0]).request.url.params
        assert params["global_step_from"] == "0"
        assert params["global_step_to"] == "0"
        assert params["logged_at_from"] == "2024-01-01T00:00:00+00:00"
        assert params["logged_at_to"] == "2024-01-02T00:00:00+00:00"
        assert params["resolution"] == "50"
        assert json.loads(result.output) == _FT_METRICS_BODY["metrics"]


class TestFineTuningDownload:
    @pytest.mark.respx(base_url=base_url)
    def test_download_invokes_download_manager(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/fine-tunes/ft-abcd-12").mock(return_value=httpx.Response(200, json=_FT_RETRIEVE_BODY))
        out_file = tmp_path / "weights.tar"
        out_file.write_bytes(b"x")

        class _DM:
            def __init__(self, _client: object) -> None:
                pass

            async def download(self, **kwargs: object) -> tuple[str, int]:
                assert "ft_id=ft-abcd-12" in str(kwargs.get("url", ""))
                assert "checkpoint=model_output_path" in str(kwargs.get("url", ""))
                return str(out_file), 1

        with patch.object(_ft_download_mod, "AsyncDownloadManager", _DM):
            # Full fine-tunes require explicit --checkpoint-type default (CLI default is merged for LoRA).
            result = cli_runner.invoke(
                [
                    "fine-tuning",
                    "download",
                    "ft-abcd-12",
                    "--checkpoint-type",
                    "default",
                    "--output-dir",
                    str(tmp_path),
                    "--json",
                ],
            )
        assert result.exit_code == 0
        payload = json.loads(result.output.strip())
        assert payload["id"] == "ft-abcd-12"
        assert payload["size"] == 1
