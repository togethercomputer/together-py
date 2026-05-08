from __future__ import annotations

import os
import importlib
import subprocess
from typing import Any
from pathlib import Path
from unittest.mock import AsyncMock, patch
from collections.abc import Sequence

from tests.cli.utils import CliRunner
from tests.cli.test_files import _file_response

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

_files_upload_cli = importlib.import_module("together.lib.cli.api.files.upload")


def _assert_stdout_json_pipes_to_jq(stdout: str) -> None:
    jq_result = subprocess.run(["jq"], input=stdout, capture_output=True, text=True)
    if jq_result.returncode != 0:
        raise AssertionError(f"jq failed: {jq_result.stderr!r}")


class JSONValidator:
    _skip: bool = False

    def __init__(self, namespace: str | Sequence[str]):
        # One argv segment per CLI word: "files" or ("beta", "clusters"), not "beta clusters".
        self.namespace_parts: tuple[str, ...] = (namespace,) if isinstance(namespace, str) else tuple(namespace)

    @property
    def skip(self) -> JSONValidator:
        self._skip = True
        return self

    # Invokes the command on the command line
    # It then pipes the results to jq to assert that the JSON is valid
    def run_and_assert(self, command: str, **kwargs: Any) -> None:
        if self._skip:
            print(f"Skipping {command} because it is not supported in JSON mode")
            return

        def run_command(command: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["together", *self.namespace_parts, *command.split(" "), "--json", "--base-url", base_url],
                capture_output=True,
                text=True,
                **kwargs,
            )

        command_result = run_command(command)
        if command_result.returncode != 0:
            ns = " ".join(self.namespace_parts)
            raise AssertionError(f"{ns} {command} exited {command_result.returncode}: stderr={command_result.stderr!r}")
        try:
            _assert_stdout_json_pipes_to_jq(command_result.stdout)
        except AssertionError as e:
            ns = " ".join(self.namespace_parts)
            raise AssertionError(f"{ns} {command}: {e}") from e


class TestJSONMode:
    # All Endpoint commands
    def test_endpoints_json_mode(self) -> None:
        endpoints = JSONValidator("endpoints")
        endpoints.run_and_assert("availability-zones")
        endpoints.run_and_assert("create --model deepseek-ai/DeepSeek-R1 --hardware 1x_nvidia_a100_80gb_sxm")
        endpoints.run_and_assert("delete endpoint-123")
        endpoints.run_and_assert("hardware")
        endpoints.run_and_assert("hardware --model deepseek-ai/DeepSeek-R1")
        endpoints.run_and_assert("list")
        endpoints.run_and_assert("list --type dedicated")
        endpoints.run_and_assert("list --usage-type on-demand")
        endpoints.run_and_assert("list --usage-type reserved")
        endpoints.run_and_assert("list --mine")
        endpoints.run_and_assert("retrieve endpoint-123")
        endpoints.run_and_assert("start endpoint-123")
        endpoints.run_and_assert("stop endpoint-123")
        endpoints.run_and_assert("update endpoint-123 --min-replicas 2 --max-replicas 4 --inactive-timeout 60")

    # All Evals commands
    def test_evals_json_mode(self) -> None:
        evals = JSONValidator("evals")
        evals.skip.run_and_assert(
            "create --type classify --judge-model deepseek-ai/DeepSeek-R1 --judge-model-source dedicated --judge-system-template 'You are a helpful assistant' --input-data-file-path data.json --model-field 'generated_text' --model-to-evaluate deepseek-ai/DeepSeek-R1 --model-to-evaluate-source dedicated --model-to-evaluate-system-template 'You are a helpful assistant' --model-to-evaluate-input-template 'You are a helpful assistant' --labels 'yes,no' --pass-labels 'yes' --min-score 0.5 --max-score 1.0 --pass-threshold 0.75"
        )
        evals.skip.run_and_assert("list")
        evals.skip.run_and_assert("list --status completed")
        evals.skip.run_and_assert("list --limit 1")
        evals.skip.run_and_assert("retrieve eval-123")
        evals.skip.run_and_assert("status eval-123")

    # All files commands (subprocess against mock server; no respx — child process never sees patches).
    def test_files_json_mode(self) -> None:
        files = JSONValidator("files")
        files.run_and_assert("check data.jsonl", cwd=os.path.dirname(__file__))
        files.run_and_assert("delete file-123")
        files.run_and_assert("list")
        files.run_and_assert("retrieve file-123")

    def test_files_upload_json_mode_pipeable_to_jq(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        """Upload JSON path: mock ``AsyncFilesResource.upload`` (subprocess cannot hit respx mocks)."""
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

    # All fine-tuning commands
    def test_fine_tuning_json_mode(self) -> None:
        fine_tuning = JSONValidator("fine-tuning")
        fine_tuning.skip.run_and_assert("create")  # TODO:
        fine_tuning.run_and_assert("list")
        fine_tuning.run_and_assert("retrieve ft-123")
        fine_tuning.run_and_assert("cancel ft-123 --quiet")
        fine_tuning.run_and_assert("download ft-123")
        fine_tuning.run_and_assert("delete ft-123 --force")
        fine_tuning.run_and_assert("list-events ft-123")
        fine_tuning.run_and_assert("list-checkpoints ft-123")
        fine_tuning.run_and_assert("retrieve-checkpoint ft-123/checkpoint-123")
        fine_tuning.run_and_assert("retrieve-checkpoint ft-123/checkpoint-123")

    def test_models_json_mode(self) -> None:
        models = JSONValidator("models")
        models.run_and_assert("list")
        models.run_and_assert("list --type dedicated")
        models.run_and_assert("upload --model-name model-123/version-123 --model-source s3://model-123/version-123")

    def test_beta_clusters_json_mode(self) -> None:
        beta_clusters = JSONValidator(("beta", "clusters"))
        beta_clusters.run_and_assert(
            "create --non-interactive --cluster-type KUBERNETES --gpu-type H100_SXM "
            "--nvidia-driver-version 565 --cuda-version 12.6 --region us-central-8 --num-gpus 8 "
            "--billing-type ON_DEMAND --name together-py-testing-suite --volume 123"
        )
        beta_clusters.run_and_assert("delete cluster-123")
        # get-credentials --json does not write files (see get_credentials.py).
        beta_clusters.run_and_assert("get-credentials cluster-123")
        beta_clusters.run_and_assert("list")
        beta_clusters.run_and_assert("list-regions")
        beta_clusters.run_and_assert("retrieve cluster-123")
        beta_clusters.run_and_assert("update cluster-123 --num-gpus 16 --cluster-type KUBERNETES")

    def test_beta_clusters_storage_json_mode(self) -> None:
        beta_clusters_storage = JSONValidator(("beta", "clusters", "storage"))
        beta_clusters_storage.run_and_assert("create --region us-east-1 --size-tib 1 --volume-name test-volume")
        beta_clusters_storage.run_and_assert("update storage-123 --size-tib 4")
        beta_clusters_storage.run_and_assert("delete storage-123")
        beta_clusters_storage.run_and_assert("list")
        beta_clusters_storage.run_and_assert("retrieve storage-123")

    def test_jig_json_mode(self) -> None:
        jig = JSONValidator(("beta", "jig"))
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

        jig.run_and_assert("list")
        jig.run_and_assert("status")

    def test_jig_secrets_json_mode(self) -> None:
        jig = JSONValidator(("beta", "jig", "secrets"))
        jig.skip.run_and_assert("set")
        jig.skip.run_and_assert("unset")
        jig.skip.run_and_assert("list")

    def test_jig_volumes_json_mode(self) -> None:
        jig = JSONValidator(("beta", "jig", "volumes"))
        jig.skip.run_and_assert("create")
        jig.skip.run_and_assert("update")
        jig.skip.run_and_assert("delete")
        jig.skip.run_and_assert("describe")
        jig.skip.run_and_assert("list")
