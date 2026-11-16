from __future__ import annotations

import pytest

from tests.cli.utils import CliRunner


@pytest.mark.parametrize(
    "args",
    [
        ["evals"],
        ["evals", "list"],
        ["evals", "ls"],
        ["evals", "list", "--status", "completed", "--limit", "5"],
        ["evals", "retrieve", "eval-wf-1"],
        ["evals", "get", "eval-wf-1"],
        ["evals", "eval-wf-1"],
        ["evals", "status", "eval-wf-1"],
        [
            "evals",
            "create",
            "--type",
            "compare",
            "--judge-model",
            "Qwen/Qwen3.5-9B",
            "--judge-model-source",
            "serverless",
            "--judge-system-template",
            "Choose the better response.",
            "--input-data-file-path",
            "file-123",
            "--model-a-field",
            "response_a",
            "--model-b-field",
            "response_b",
            "--disable-position-bias-correction",
        ],
        ["evals", "create", "--not-a-real-flag", "whatever"],
        ["evals", "-c", "--garbage"],
    ],
)
def test_evals_commands_return_service_discontinued(args: list[str], cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(args)
    assert result.exit_code != 0
    assert "Error: Service discontinued" in result.output


def test_evals_hidden_from_root_help(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "Run and manage model evaluations" not in result.output
    # Command name may still appear in unrelated help copy (e.g. files upload purpose).
    lines = [line for line in result.output.splitlines() if line.strip().startswith("evals")]
    assert lines == []
