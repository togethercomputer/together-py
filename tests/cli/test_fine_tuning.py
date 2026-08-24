from __future__ import annotations

import os
import re
import json
import time
import importlib
from typing import cast
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _normalize_cli_help(output: str) -> str:
    # Rich help wraps table cells across panel borders and can interleave the
    # type/description columns with ANSI padding; normalize for both agent
    # (plain) and human (rich) formatters.
    return " ".join(_ANSI_RE.sub("", output).replace("│", " ").split())


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
    "checkpoint": "model",
    "created_at": "2024-01-01T00:00:00Z",
    "object_id": "ml-checkpoint",
    "object_name": "project-slug/model-checkpoint",
    "object_revision_id": "rv-checkpoint",
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

_FT_PREVIEW_BODY = {
    "dataset_format": "conversation",
    "max_seq_length": 4096,
    "model": "meta-llama/Llama-3-8b",
    "train_on_inputs": False,
    "rows": [
        {
            "input_ids": [1, 2, 3],
            "labels": [-100, 2, 3],
            "num_tokens": 3,
            "num_trained_tokens": 2,
            "tokens": ["<s>", " hello", " world"],
            "trained_spans": [[1, 3]],
            "truncated": False,
        }
    ],
}

_FT_TOKENIZED_DATASET_URL = "https://download.example/tokenized-dataset.tar.gz"

_FT_TOKENIZED_DATASET_BODY = {
    "content_type": "application/gzip",
    "expires_at": "2024-01-01T01:00:00Z",
    "filename": "tokenized-dataset.tar.gz",
    "size": len(b"tokenized-bytes"),
    "url": _FT_TOKENIZED_DATASET_URL,
}

_MODEL_LIMITS_BODY = {
    "model_name": "meta-llama/Llama-3-8b",
    "default_gradient_accumulation_steps": 1,
    "max_num_epochs": 10,
    "max_num_checkpoints": 5,
    "max_num_evals": 20,
    "max_learning_rate": 1,
    "min_learning_rate": 0,
    "min_max_seq_length": 1,
    "max_seq_length_sft": 4096,
    "max_seq_length_dpo": 4096,
    "merge_output_lora": True,
    "supports_full_training": True,
    "supports_reasoning": False,
    "supports_tools": True,
    "supports_vision": False,
    "full_training": {
        "max_batch_size": 64,
        "max_batch_size_dpo": 32,
        "min_batch_size": 1,
    },
    "lora_training": {
        "max_batch_size": 128,
        "max_batch_size_dpo": 64,
        "max_rank": 64,
        "min_batch_size": 1,
        "target_modules": ["q_proj", "v_proj"],
    },
}

_FT_CREATE_BODY = {
    "id": "ft-created",
    "status": "pending",
}


class TestFineTuningCreate:
    def test_create_help_describes_lora_options(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["fine-tuning", "create", "--help"])
        output = _normalize_cli_help(result.output)

        assert result.exit_code == 0
        assert "Rank of the LoRA adapter matrices" in output
        assert "Dropout probability applied to LoRA adapter inputs" in output
        assert "Scaling factor applied to the LoRA adapter weights" in output
        assert "MoE expert modules" in output
        assert "adapter-only output" in output

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
                "--non-interactive",
            ],
        )

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "not available for multimodal datasets" in output
        assert "Do you want to proceed?" not in result.output
        assert "ft-created" in result.output
        assert estimate.calls
        assert create.calls

    @pytest.mark.respx(base_url=base_url)
    def test_create_handles_missing_estimated_price(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY))
        respx_mock.post("/fine-tunes/estimate-price").mock(
            return_value=httpx.Response(
                200,
                json={
                    "estimation_available": True,
                    "estimated_total_price": None,
                    "allowed_to_proceed": True,
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
                "--non-interactive",
            ],
        )

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "Price estimation is not available for this job." in output
        assert "ft-created" in result.output
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

    @pytest.mark.skipif(not hasattr(time, "tzset"), reason="requires POSIX timezone support")
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_handles_boundary_datetime(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        body = {
            **_FT_RETRIEVE_BODY,
            "status": "queued",
            "started_at": "0001-01-01T00:00:00Z",
        }
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        previous_tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()

        try:
            result = cli_runner.invoke(["fine-tuning", "retrieve", "ft-1", "--no-plots"])
        finally:
            if previous_tz is None:
                os.environ.pop("TZ")
            else:
                os.environ["TZ"] = previous_tz
            time.tzset()

        assert result.exit_code == 0
        assert "ft-1" in result.output
        assert "Progress: unavailable" in result.output


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

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_not_cancellable_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        body = {**_FT_RETRIEVE_BODY, "status": "completed"}
        respx_mock.get("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json=body))
        result = cli_runner.invoke(["fine-tuning", "cancel", "ft-1", "--quiet", "--json"])
        assert result.exit_code == 1
        assert "Training is not currently cancellable" in result.output


class TestFineTuningDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete_json_skips_confirmation(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/fine-tunes/ft-1").mock(return_value=httpx.Response(200, json={"message": "deleted"}))
        result = cli_runner.invoke(["fine-tuning", "delete", "ft-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"message": "deleted"}

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
    def test_list_events_returns_all_events(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        events = [
            {
                **_FT_EVENT,
                "created_at": f"2024-01-01T00:00:{index:02d}Z",
                "message": f"event {index}",
            }
            for index in range(21)
        ]
        respx_mock.get("/fine-tunes/ft-1/events").mock(return_value=httpx.Response(200, json={"data": events}))

        result = cli_runner.invoke(["fine-tuning", "list-events", "ft-1", "--json"])

        assert result.exit_code == 0
        assert [event["message"] for event in json.loads(result.output)] == [f"event {index}" for index in range(21)]

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(
            return_value=httpx.Response(200, json={"data": [_FT_CHECKPOINT]})
        )
        result = cli_runner.invoke(["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "ft-1:5" in result.output
        assert "Registry artifacts" in result.output
        assert "project-slug/model-checkpoint" in result.output
        assert "intermediate" in result.output
        # The revision is deliberately not rendered; it stays available in --json output.
        assert "rv-checkpoint" not in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_checkpoints_table_falls_back_to_object_id(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        checkpoint = {**_FT_CHECKPOINT, "object_name": None}
        respx_mock.get("/fine-tunes/ft-1/checkpoints").mock(
            return_value=httpx.Response(200, json={"data": [checkpoint]})
        )
        result = cli_runner.invoke(["fine-tuning", "list-checkpoints", "ft-1"])
        assert result.exit_code == 0
        assert "ml-checkpoint" in result.output
        assert "rv-checkpoint" not in result.output

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


class TestFineTuningPreview:
    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        ("train_on_inputs_flag", "expected_train_on_inputs"),
        [
            ("--train-on-inputs", True),
            ("--no-train-on-inputs", False),
        ],
    )
    def test_preview_json_sends_params(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        train_on_inputs_flag: str,
        expected_train_on_inputs: bool,
    ) -> None:
        route = respx_mock.post("/fine-tunes/preview").mock(return_value=httpx.Response(200, json=_FT_PREVIEW_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "preview",
                "--training-file",
                "file-train",
                "--model",
                "meta-llama/Llama-3-8b",
                "--top-k",
                "5",
                train_on_inputs_flag,
                "--training-method",
                "sft",
                "--json",
            ]
        )

        assert result.exit_code == 0
        assert json.loads(result.output) == _FT_PREVIEW_BODY
        request_body = json.loads(cast(Call, route.calls[0]).request.content)
        assert request_body == {
            "model": "meta-llama/Llama-3-8b",
            "training_file": "file-train",
            "top_k": 5,
            "train_on_inputs": expected_train_on_inputs,
            "training_method": "sft",
        }

    @pytest.mark.respx(base_url=base_url)
    def test_preview_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.post("/fine-tunes/preview").mock(return_value=httpx.Response(200, json=_FT_PREVIEW_BODY))

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "preview",
                "--training-file",
                "file-train",
                "--model",
                "meta-llama/Llama-3-8b",
            ]
        )

        assert result.exit_code == 0
        assert "conversation" in result.output
        assert "Preview Rows" in result.output
        assert "1-3" in result.output
        assert "hello" in result.output


class TestFineTuningModelLimits:
    @pytest.mark.respx(base_url=base_url)
    def test_model_limits_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/fine-tunes/models/limits").mock(
            return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY)
        )

        result = cli_runner.invoke(["fine-tuning", "model-limits", "meta-llama/Llama-3-8b", "--json"])

        assert result.exit_code == 0
        params = cast(Call, route.calls[0]).request.url.params
        assert params["model_name"] == "meta-llama/Llama-3-8b"
        body = json.loads(result.output)
        assert body["model_name"] == "meta-llama/Llama-3-8b"
        assert body["lora_training"]["max_rank"] == 64

    @pytest.mark.respx(base_url=base_url)
    def test_model_limits_ft_alias_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/fine-tunes/models/limits").mock(return_value=httpx.Response(200, json=_MODEL_LIMITS_BODY))

        result = cli_runner.invoke(["ft", "model-limits", "meta-llama/Llama-3-8b"])

        assert result.exit_code == 0
        assert "meta-llama/Llama-3-8b" in result.output
        assert "Max Rank" in result.output


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

    @pytest.mark.respx(base_url=base_url)
    def test_download_defaults_to_merged_checkpoint_for_lora_job(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/fine-tunes/ft-abcd-12").mock(
            return_value=httpx.Response(
                200,
                json={
                    **_FT_RETRIEVE_BODY,
                    "training_type": {
                        "type": "Lora",
                        "lora_alpha": 16,
                        "lora_r": 8,
                    },
                },
            )
        )
        out_file = tmp_path / "weights.tar"
        out_file.write_bytes(b"x")

        class _DM:
            def __init__(self, _client: object) -> None:
                pass

            async def download(self, **kwargs: object) -> tuple[str, int]:
                assert "checkpoint=merged" in str(kwargs.get("url", ""))
                return str(out_file), 1

        with patch.object(_ft_download_mod, "AsyncDownloadManager", _DM):
            result = cli_runner.invoke(
                [
                    "fine-tuning",
                    "download",
                    "ft-abcd-12",
                    "--output-dir",
                    str(tmp_path),
                    "--json",
                ],
            )

        assert result.exit_code == 0


class TestFineTuningDownloadTokenizedDataset:
    @pytest.mark.respx(base_url=base_url)
    def test_download_tokenized_dataset_writes_file_json(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        metadata = respx_mock.get("/fine-tunes/ft-abcd-12/download-tokenized-dataset").mock(
            return_value=httpx.Response(200, json=_FT_TOKENIZED_DATASET_BODY)
        )
        download = respx_mock.get(_FT_TOKENIZED_DATASET_URL).mock(
            return_value=httpx.Response(200, content=b"tokenized-bytes")
        )

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "download-tokenized-dataset",
                "ft-abcd-12",
                "--output-dir",
                str(tmp_path),
                "--json",
            ]
        )

        assert result.exit_code == 0
        out_path = tmp_path / "tokenized-dataset.tar.gz"
        assert out_path.read_bytes() == b"tokenized-bytes"
        payload = json.loads(result.output)
        assert payload == {
            "object": "local",
            "id": "ft-abcd-12",
            "filename": str(out_path),
            "size": len(b"tokenized-bytes"),
        }
        assert _FT_TOKENIZED_DATASET_URL not in result.output
        assert metadata.calls
        assert download.calls

    @pytest.mark.respx(base_url=base_url)
    def test_download_tokenized_dataset_rejects_path_traversal_filename(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        body = {**_FT_TOKENIZED_DATASET_BODY, "filename": "../../outside.tar.gz"}
        respx_mock.get("/fine-tunes/ft-abcd-12/download-tokenized-dataset").mock(
            return_value=httpx.Response(200, json=body)
        )
        respx_mock.get(_FT_TOKENIZED_DATASET_URL).mock(return_value=httpx.Response(200, content=b"tokenized-bytes"))
        out_dir = tmp_path / "downloads"

        result = cli_runner.invoke(
            [
                "fine-tuning",
                "download-tokenized-dataset",
                "ft-abcd-12",
                "--output-dir",
                str(out_dir),
            ]
        )

        assert result.exit_code == 0
        saved = list(out_dir.iterdir())
        assert len(saved) == 1
        assert saved[0].is_file()
        assert saved[0].read_bytes() == b"tokenized-bytes"
        assert saved[0].resolve().is_relative_to(out_dir.resolve())
        assert not (tmp_path / "outside.tar.gz").exists()
