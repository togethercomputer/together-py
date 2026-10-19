from __future__ import annotations

import os
import importlib
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, patch
from collections.abc import Sequence

import httpx
import pytest
from respx import MockRouter

from tests.cli.utils import CliRunner
from tests.cli.test_files import FILE_ROW_NEWER, _file_response
from tests.cli.test_batches import _BATCH_JOB, _BATCH_CREATE
from tests.cli.test_clusters import _VOLUME_BODY, _REGIONS_BODY, _cluster_body
from tests.cli.test_fine_tuning import (
    _FT_EVENT,
    _FT_LIST_ITEM,
    _FT_CHECKPOINT,
    _FT_PREVIEW_BODY,
    _FT_RETRIEVE_BODY,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

_files_upload_cli = importlib.import_module("together.lib.cli.api.files.upload")

_FT_RUNNING = {**_FT_RETRIEVE_BODY, "id": "ft-123", "status": "running"}
_DATA_JSONL = Path(__file__).resolve().parent / "data.jsonl"


def _assert_stdout_json_pipes_to_jq(stdout: str) -> None:
    jq_result = subprocess.run(["jq"], input=stdout, capture_output=True, text=True)
    if jq_result.returncode != 0:
        raise AssertionError(f"jq failed: {jq_result.stderr!r}")


def _ok(body: object) -> httpx.Response:
    return httpx.Response(200, json=body)


def _mock_json_mode_http(respx_mock: MockRouter) -> None:
    """Deterministic HTTP for in-process CLI JSON-mode tests (no live API key)."""
    respx_mock.post("/v1/batches").mock(return_value=_ok(_BATCH_CREATE))
    respx_mock.get("/v1/batches").mock(return_value=_ok([_BATCH_JOB]))
    respx_mock.get("/v1/batches/batch_job_abc123def456").mock(return_value=_ok(_BATCH_JOB))
    respx_mock.post("/v1/batches/batch_job_abc123def456/cancel").mock(return_value=_ok(_BATCH_JOB))

    respx_mock.delete("/v1/files/file-123").mock(return_value=_ok({"id": "file-123", "deleted": True}))
    respx_mock.get("/v1/files").mock(return_value=_ok({"data": [FILE_ROW_NEWER]}))
    respx_mock.get("/v1/files/file-123").mock(return_value=_ok(FILE_ROW_NEWER))

    respx_mock.get("/v1/fine-tunes").mock(return_value=_ok({"data": [_FT_LIST_ITEM]}))
    respx_mock.get("/v1/fine-tunes/ft-123").mock(return_value=_ok(_FT_RUNNING))
    respx_mock.post("/v1/fine-tunes/ft-123/cancel").mock(return_value=_ok(_FT_RUNNING))
    respx_mock.delete("/v1/fine-tunes/ft-123").mock(return_value=_ok({"message": "deleted"}))
    respx_mock.get("/v1/fine-tunes/ft-123/events").mock(return_value=_ok({"data": [_FT_EVENT]}))
    respx_mock.get("/v1/fine-tunes/ft-123/checkpoints").mock(return_value=_ok({"data": [_FT_CHECKPOINT]}))
    respx_mock.post("/v1/fine-tunes/preview").mock(return_value=_ok(_FT_PREVIEW_BODY))

    cluster = _cluster_body("cluster-123", "together-py-testing-suite")
    respx_mock.post("/v1/compute/clusters").mock(return_value=_ok(cluster))
    respx_mock.get("/v1/compute/clusters").mock(return_value=_ok({"clusters": [cluster]}))
    respx_mock.get("/v1/compute/clusters/cluster-123").mock(return_value=_ok(cluster))
    respx_mock.put("/v1/compute/clusters/cluster-123").mock(return_value=_ok(cluster))
    respx_mock.delete("/v1/compute/clusters/cluster-123").mock(return_value=_ok({"cluster_id": "cluster-123"}))
    respx_mock.get("/v1/compute/regions").mock(return_value=_ok(_REGIONS_BODY))

    respx_mock.post("/v1/compute/clusters/storage/volumes").mock(return_value=_ok(_VOLUME_BODY))
    respx_mock.put("/v1/compute/clusters/storage/volumes").mock(return_value=_ok(_VOLUME_BODY))
    respx_mock.get("/v1/compute/clusters/storage/volumes").mock(return_value=_ok({"volumes": [_VOLUME_BODY]}))
    respx_mock.get("/v1/compute/clusters/storage/volumes/storage-123").mock(return_value=_ok(_VOLUME_BODY))
    respx_mock.delete("/v1/compute/clusters/storage/volumes/storage-123").mock(return_value=_ok({"success": True}))


class JSONValidator:
    def __init__(self, namespace: str | Sequence[str], cli_runner: CliRunner, *, skip: bool = False):
        # One argv segment per CLI word: "files" or ("clusters", "storage"), not "clusters storage".
        self.namespace_parts: tuple[str, ...] = (namespace,) if isinstance(namespace, str) else tuple(namespace)
        self.cli_runner = cli_runner
        self._skip = skip

    @property
    def skip(self) -> JSONValidator:
        return JSONValidator(self.namespace_parts, self.cli_runner, skip=True)

    def run_and_assert(self, command: str, *, allow_nonzero: bool = False) -> None:
        if self._skip:
            return

        result = self.cli_runner.invoke([*self.namespace_parts, *command.split(" "), "--json"])
        if result.exit_code != 0 and not allow_nonzero:
            ns = " ".join(self.namespace_parts)
            raise AssertionError(f"{ns} {command} exited {result.exit_code}: stderr={result.err_out!r}")
        try:
            _assert_stdout_json_pipes_to_jq(result.out_out)
        except AssertionError as e:
            ns = " ".join(self.namespace_parts)
            raise AssertionError(f"{ns} {command}: {e}") from e


@pytest.mark.respx(base_url=base_url, assert_all_called=False)
class TestJSONMode:
    @pytest.fixture(autouse=True)
    def _http(self, respx_mock: MockRouter) -> None:
        _mock_json_mode_http(respx_mock)

    def test_evals_json_mode(self, cli_runner: CliRunner) -> None:
        evals = JSONValidator("evals", cli_runner)
        evals.skip.run_and_assert(
            "create --type classify --judge-model deepseek-ai/DeepSeek-R1 --judge-model-source dedicated --judge-system-template 'You are a helpful assistant' --input-data-file-path data.json --model-field 'generated_text' --model-to-evaluate deepseek-ai/DeepSeek-R1 --model-to-evaluate-source dedicated --model-to-evaluate-system-template 'You are a helpful assistant' --model-to-evaluate-input-template 'You are a helpful assistant' --labels 'yes,no' --pass-labels 'yes' --min-score 0.5 --max-score 1.0 --pass-threshold 0.75"
        )
        evals.skip.run_and_assert("list")
        evals.skip.run_and_assert("list --status completed")
        evals.skip.run_and_assert("list --limit 1")
        evals.skip.run_and_assert("retrieve eval-123")
        evals.skip.run_and_assert("status eval-123")

    def test_batches_json_mode(self, cli_runner: CliRunner) -> None:
        batches = JSONValidator("batches", cli_runner)
        batches.run_and_assert("submit file-abc123def456ghi789 chat.completions")
        batches.run_and_assert("list")
        batches.run_and_assert("retrieve batch_job_abc123def456")
        batches.run_and_assert("cancel batch_job_abc123def456")
        # --json download refuses to dump file bytes; error payload must still be jq-parseable.
        batches.run_and_assert("download batch_job_abc123def456", allow_nonzero=True)

    def test_files_json_mode(self, cli_runner: CliRunner) -> None:
        files = JSONValidator("files", cli_runner)
        files.run_and_assert(f"check {_DATA_JSONL}")
        files.run_and_assert("delete file-123")
        files.run_and_assert("list")
        files.run_and_assert("retrieve file-123")

    def test_files_upload_json_mode_pipeable_to_jq(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        sample = tmp_path / "data.jsonl"
        sample.write_text('{"text": "x"}\n', encoding="utf-8")
        uploaded = _file_response(id="file-json-upload")
        with patch.object(_files_upload_cli, "check_file") as check_mock, patch(
            "together.resources.files.AsyncFilesResource.upload", new_callable=AsyncMock
        ) as upload_mock:
            check_mock.return_value = {"is_check_passed": True, "message": "ok"}
            upload_mock.return_value = uploaded
            result = cli_runner.invoke(
                ["files", "upload", str(sample), "--purpose", "fine-tune", "--json"],
            )
        assert result.exit_code == 0
        _assert_stdout_json_pipes_to_jq(result.out_out)

    def test_fine_tuning_json_mode(self, cli_runner: CliRunner) -> None:
        fine_tuning = JSONValidator("fine-tuning", cli_runner)
        fine_tuning.skip.run_and_assert("create")
        fine_tuning.run_and_assert("list")
        fine_tuning.run_and_assert("retrieve ft-123")
        fine_tuning.run_and_assert("cancel ft-123 --quiet")
        fine_tuning.skip.run_and_assert("download ft-123")
        fine_tuning.run_and_assert("delete ft-123 --force")
        fine_tuning.run_and_assert("list-events ft-123")
        fine_tuning.run_and_assert("list-checkpoints ft-123")
        fine_tuning.run_and_assert("preview --training-file file-123 --model deepseek-ai/DeepSeek-R1")
        fine_tuning.skip.run_and_assert("retrieve-checkpoint ft-123/checkpoint-123")

    def test_clusters_json_mode(self, cli_runner: CliRunner) -> None:
        clusters = JSONValidator(("clusters",), cli_runner)
        clusters.run_and_assert(
            "create --non-interactive --cluster-type KUBERNETES --gpu-type H100_SXM "
            "--nvidia-driver-version 565 --cuda-version 12.6 --region us-central-8 --num-gpus 8 "
            "--billing-type ON_DEMAND --name together-py-testing-suite --volume 123"
        )
        clusters.run_and_assert("delete cluster-123")
        clusters.run_and_assert("get-credentials cluster-123")
        clusters.run_and_assert("list")
        clusters.run_and_assert("list-regions")
        clusters.run_and_assert("retrieve cluster-123")
        clusters.run_and_assert("update cluster-123 --num-gpus 16 --cluster-type KUBERNETES")

    def test_clusters_storage_json_mode(self, cli_runner: CliRunner) -> None:
        clusters_storage = JSONValidator(("clusters", "storage"), cli_runner)
        clusters_storage.run_and_assert("create --region us-east-1 --size-tib 1 --volume-name test-volume")
        clusters_storage.run_and_assert("update storage-123 --size-tib 4")
        clusters_storage.run_and_assert("delete storage-123")
        clusters_storage.run_and_assert("list")
        clusters_storage.run_and_assert("retrieve storage-123")

    def test_jig_json_mode(self, cli_runner: CliRunner) -> None:
        jig = JSONValidator(("beta", "jig"), cli_runner)
        jig.skip.run_and_assert("init")
        jig.skip.run_and_assert("dockerfile")
        jig.skip.run_and_assert("build")
        jig.skip.run_and_assert("push")
        jig.skip.run_and_assert("deploy")
        jig.skip.run_and_assert("endpoint")
        jig.skip.run_and_assert("logs")
        jig.skip.run_and_assert("destroy")
        jig.skip.run_and_assert("submit")
        jig.skip.run_and_assert("job-status")
        jig.skip.run_and_assert("queue-status")
        jig.skip.run_and_assert("list")
        jig.skip.run_and_assert("status")

    def test_jig_secrets_json_mode(self, cli_runner: CliRunner) -> None:
        jig = JSONValidator(("beta", "jig", "secrets"), cli_runner)
        jig.skip.run_and_assert("set")
        jig.skip.run_and_assert("unset")
        jig.skip.run_and_assert("list")

    def test_jig_volumes_json_mode(self, cli_runner: CliRunner) -> None:
        jig = JSONValidator(("beta", "jig", "volumes"), cli_runner)
        jig.skip.run_and_assert("create")
        jig.skip.run_and_assert("update")
        jig.skip.run_and_assert("delete")
        jig.skip.run_and_assert("describe")
        jig.skip.run_and_assert("list")
