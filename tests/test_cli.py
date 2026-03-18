from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from together.lib.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_client():
    return MagicMock()


def invoke(runner: CliRunner, mock_client: MagicMock, args: list, input: str | None = None):
    """Invoke the CLI with a mocked Together client."""
    with patch("together.Together", return_value=mock_client):
        return runner.invoke(main, ["--api-key", "test-key"] + args, input=input)


# ---------------------------------------------------------------------------
# Main CLI group
# ---------------------------------------------------------------------------


class TestMainCLI:
    def test_version_flag(self, runner, mock_client):
        with patch("together.Together", return_value=mock_client):
            result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "Version" in result.output

    def test_help_flag(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_subcommand_groups_in_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        for group in ["files", "fine-tuning", "models", "endpoints", "evals", "beta"]:
            assert group in result.output

    def test_missing_api_key_creates_dummy_client(self, runner):
        """Without an API key the CLI creates a dummy client and prints a warning on first request."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("together.Together") as mock_cls:
                # First call raises (no key), second call with dummy key succeeds
                mock_cls.side_effect = [Exception("api_key missing"), MagicMock()]
                result = runner.invoke(main, ["files", "list"])
        # Should not crash at help-level (graceful degradation)
        assert result.exit_code in (0, 1)

    def test_missing_api_key_hook_blocks_request(self):
        """When no API key is set the request hook fires on the first API call,
        prints a helpful error message, and exits with code 1.

        This test uses subprocess.run instead of CliRunner so that:
          - The child process starts with a clean import state (no import-time
            evaluation of os.getenv("TOGETHER_API_KEY") carrying over from the
            parent).
          - Stripping TOGETHER_API_KEY from the child's environment is
            sufficient — no mock gymnastics required.
          - The httpx request hook fires before any bytes are sent over the
            network, so sys.exit(1) is called before a real request is made.

        Flow:
          1. Together() raises because api_key is missing.
          2. CLI catches the error and creates a dummy client with a fake key.
          3. A request hook is registered on the dummy client's httpx session.
          4. files.list() tries to make an HTTP request; httpx calls the hook
             first, which prints the error and calls sys.exit(1).
        """
        import subprocess
        import sys
        from pathlib import Path

        together_bin = str(Path(sys.executable).parent / "together")
        env = {k: v for k, v in os.environ.items() if k != "TOGETHER_API_KEY"}

        result = subprocess.run(
            [together_bin, "files", "list"],
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 1
        assert (
            "Error: api key missing.\n\nThe api key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable"
            in result.stdout
        )
        assert "https://api.together.xyz/settings/api-keys" in result.stdout

    def test_debug_flag_sets_env(self, runner, mock_client):
        with patch("together.Together", return_value=mock_client):
            with patch("together.lib.cli.__init__.setup_logging") as mock_setup:
                mock_client.files.list.return_value = MagicMock(data=[])
                result = runner.invoke(main, ["--api-key", "test-key", "--debug", "files", "list"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# files commands
# ---------------------------------------------------------------------------


class TestFilesCLI:
    def test_files_help(self, runner, mock_client):
        result = invoke(runner, mock_client, ["files", "--help"])
        assert result.exit_code == 0
        for cmd in ["upload", "list", "retrieve", "retrieve-content", "delete", "check"]:
            assert cmd in result.output

    def test_files_list_empty(self, runner, mock_client):
        mock_client.files.list.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["files", "list"])
        assert result.exit_code == 0
        mock_client.files.list.assert_called_once()

    def test_files_list_json_empty(self, runner, mock_client):
        mock_client.files.list.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["files", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == []

    def test_files_list_with_data(self, runner, mock_client):
        mock_file = MagicMock()
        mock_file.id = "file-abc123"
        mock_file.filename = "train.jsonl"
        mock_file.bytes = 2048
        # created_at must be a Unix timestamp (int) because convert_unix_timestamp expects an integer
        mock_file.created_at = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
        mock_client.files.list.return_value = MagicMock(data=[mock_file])
        result = invoke(runner, mock_client, ["files", "list"])
        assert result.exit_code == 0

    def test_files_retrieve(self, runner, mock_client):
        mock_client.files.retrieve.return_value = MagicMock(
            model_dump=lambda **kw: {"id": "file-abc123", "filename": "train.jsonl"}
        )
        result = invoke(runner, mock_client, ["files", "retrieve", "file-abc123"])
        assert result.exit_code == 0
        mock_client.files.retrieve.assert_called_once_with(id="file-abc123")

    def test_files_retrieve_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["files", "retrieve"])
        assert result.exit_code != 0

    def test_files_delete(self, runner, mock_client):
        mock_client.files.delete.return_value = MagicMock(
            model_dump=lambda **kw: {"id": "file-abc123", "deleted": True}
        )
        result = invoke(runner, mock_client, ["files", "delete", "file-abc123"])
        assert result.exit_code == 0
        mock_client.files.delete.assert_called_once_with(id="file-abc123")

    def test_files_delete_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["files", "delete"])
        assert result.exit_code != 0

    def test_files_upload_requires_file_argument(self, runner, mock_client):
        result = invoke(runner, mock_client, ["files", "upload"])
        assert result.exit_code != 0

    def test_files_upload_with_valid_file(self, runner, mock_client, tmp_path):
        test_file = tmp_path / "train.jsonl"
        test_file.write_text('{"text": "example"}\n')
        mock_response = MagicMock()
        mock_response.id = "file-abc123"
        mock_response.purpose = "fine-tune"
        mock_response.model_dump.return_value = {"id": "file-abc123", "purpose": "fine-tune"}
        mock_client.files.upload.return_value = mock_response
        result = invoke(runner, mock_client, ["files", "upload", str(test_file)])
        assert result.exit_code == 0
        mock_client.files.upload.assert_called_once()

    def test_files_upload_json_flag(self, runner, mock_client, tmp_path):
        test_file = tmp_path / "train.jsonl"
        test_file.write_text('{"text": "example"}\n')
        mock_response = MagicMock()
        mock_response.id = "file-abc123"
        mock_response.purpose = "fine-tune"
        mock_response.model_dump.return_value = {"id": "file-abc123", "purpose": "fine-tune"}
        mock_client.files.upload.return_value = mock_response
        result = invoke(runner, mock_client, ["files", "upload", "--json", str(test_file)])
        assert result.exit_code == 0

    def test_files_upload_purpose_option(self, runner, mock_client, tmp_path):
        test_file = tmp_path / "train.jsonl"
        test_file.write_text('{"text": "example"}\n')
        mock_response = MagicMock()
        mock_response.id = "file-abc123"
        mock_response.purpose = "batch-api"
        mock_response.model_dump.return_value = {"id": "file-abc123"}
        mock_client.files.upload.return_value = mock_response
        result = invoke(runner, mock_client, ["files", "upload", "--purpose", "batch-api", str(test_file)])
        assert result.exit_code == 0
        call_kwargs = mock_client.files.upload.call_args
        assert call_kwargs.kwargs.get("purpose") == "batch-api"

    def test_files_upload_no_check(self, runner, mock_client, tmp_path):
        test_file = tmp_path / "train.jsonl"
        test_file.write_text('{"text": "example"}\n')
        mock_response = MagicMock()
        mock_response.id = "file-abc123"
        mock_response.purpose = "fine-tune"
        mock_response.model_dump.return_value = {"id": "file-abc123"}
        mock_client.files.upload.return_value = mock_response
        result = invoke(runner, mock_client, ["files", "upload", "--no-check", str(test_file)])
        assert result.exit_code == 0
        call_kwargs = mock_client.files.upload.call_args
        assert call_kwargs.kwargs.get("check") is False

    def test_files_upload_invalid_purpose(self, runner, mock_client, tmp_path):
        test_file = tmp_path / "train.jsonl"
        test_file.write_text('{"text": "example"}\n')
        result = invoke(
            runner, mock_client, ["files", "upload", "--purpose", "invalid-purpose", str(test_file)]
        )
        assert result.exit_code != 0

    def test_files_retrieve_content_requires_stdout_or_output(self, runner, mock_client):
        result = invoke(runner, mock_client, ["files", "retrieve-content", "file-abc123"])
        assert result.exit_code != 0

    def test_files_retrieve_content_stdout(self, runner, mock_client):
        mock_content = MagicMock()
        mock_content.read.return_value = b"line1\nline2\n"
        mock_client.files.content.return_value = mock_content
        result = invoke(runner, mock_client, ["files", "retrieve-content", "file-abc123", "--stdout"])
        assert result.exit_code == 0
        assert "line1" in result.output
        mock_client.files.content.assert_called_once_with(id="file-abc123")

    def test_files_retrieve_content_to_output_file(self, runner, mock_client, tmp_path):
        mock_content = MagicMock()
        mock_content.read.return_value = b"data"
        mock_client.files.content.return_value = mock_content
        output_file = str(tmp_path / "output.jsonl")
        result = invoke(
            runner, mock_client, ["files", "retrieve-content", "file-abc123", "--output", output_file]
        )
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# fine-tuning commands
# ---------------------------------------------------------------------------


class TestFineTuningCLI:
    def test_fine_tuning_help(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "--help"])
        assert result.exit_code == 0
        for cmd in ["create", "list", "retrieve", "cancel", "list-events", "list-checkpoints", "download", "delete"]:
            assert cmd in result.output

    def test_fine_tuning_list_empty(self, runner, mock_client):
        mock_client.fine_tuning.list.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["fine-tuning", "list"])
        assert result.exit_code == 0
        mock_client.fine_tuning.list.assert_called_once()

    def test_fine_tuning_list_json(self, runner, mock_client):
        mock_client.fine_tuning.list.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["fine-tuning", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == []

    def test_fine_tuning_list_with_data(self, runner, mock_client):
        mock_job = MagicMock()
        mock_job.id = "ft-abc123"
        mock_job.model = "llama-3"
        mock_job.suffix = "my-model"
        mock_job.status = "completed"
        mock_job.total_price = 100
        mock_job.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_client.fine_tuning.list.return_value = MagicMock(data=[mock_job])
        result = invoke(runner, mock_client, ["fine-tuning", "list"])
        assert result.exit_code == 0

    def test_fine_tuning_retrieve(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.status = "completed"
        mock_response.events = None
        mock_response.model_dump.return_value = {"id": "ft-abc123", "status": "completed"}
        mock_client.fine_tuning.retrieve.return_value = mock_response
        result = invoke(runner, mock_client, ["fine-tuning", "retrieve", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.retrieve.assert_called_once_with("ft-abc123")

    def test_fine_tuning_retrieve_json(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.status = "completed"
        mock_response.events = None
        mock_response.model_dump.return_value = {"id": "ft-abc123", "status": "completed"}
        mock_client.fine_tuning.retrieve.return_value = mock_response
        result = invoke(runner, mock_client, ["fine-tuning", "retrieve", "--json", "ft-abc123"])
        assert result.exit_code == 0

    def test_fine_tuning_retrieve_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "retrieve"])
        assert result.exit_code != 0

    def test_fine_tuning_cancel_already_completed(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="completed")
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "ft-abc123"])
        assert result.exit_code == 0
        assert "not currently cancellable" in result.output
        mock_client.fine_tuning.cancel.assert_not_called()

    def test_fine_tuning_cancel_already_cancelled(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="cancelled")
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "ft-abc123"])
        assert result.exit_code == 0
        assert "not currently cancellable" in result.output

    def test_fine_tuning_cancel_error_state(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="error")
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "ft-abc123"])
        assert result.exit_code == 0
        assert "not currently cancellable" in result.output

    def test_fine_tuning_cancel_quiet_running(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="running")
        mock_cancel_response = MagicMock()
        mock_cancel_response.model_dump.return_value = {"id": "ft-abc123", "status": "cancel_requested"}
        mock_client.fine_tuning.cancel.return_value = mock_cancel_response
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "--quiet", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.cancel.assert_called_once_with("ft-abc123")

    def test_fine_tuning_cancel_interactive_yes(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="running")
        mock_cancel_response = MagicMock()
        mock_cancel_response.model_dump.return_value = {"id": "ft-abc123", "status": "cancel_requested"}
        mock_client.fine_tuning.cancel.return_value = mock_cancel_response
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "ft-abc123"], input="y\n")
        assert result.exit_code == 0
        mock_client.fine_tuning.cancel.assert_called_once_with("ft-abc123")

    def test_fine_tuning_cancel_interactive_no(self, runner, mock_client):
        mock_client.fine_tuning.retrieve.return_value = MagicMock(status="running")
        result = invoke(runner, mock_client, ["fine-tuning", "cancel", "ft-abc123"], input="n\n")
        assert result.exit_code == 0
        mock_client.fine_tuning.cancel.assert_not_called()

    def test_fine_tuning_cancel_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "cancel"])
        assert result.exit_code != 0

    def test_fine_tuning_list_events(self, runner, mock_client):
        mock_client.fine_tuning.list_events.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["fine-tuning", "list-events", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.list_events.assert_called_once_with("ft-abc123")

    def test_fine_tuning_list_events_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "list-events"])
        assert result.exit_code != 0

    def test_fine_tuning_list_checkpoints(self, runner, mock_client):
        mock_client.fine_tuning.list_checkpoints.return_value = MagicMock(data=[])
        result = invoke(runner, mock_client, ["fine-tuning", "list-checkpoints", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.list_checkpoints.assert_called_once_with("ft-abc123")

    def test_fine_tuning_delete_quiet(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "ft-abc123"}
        mock_client.fine_tuning.delete.return_value = mock_response
        result = invoke(runner, mock_client, ["fine-tuning", "delete", "--quiet", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.delete.assert_called_once_with("ft-abc123", force=False)

    def test_fine_tuning_delete_interactive_yes(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "ft-abc123"}
        mock_client.fine_tuning.delete.return_value = mock_response
        result = invoke(runner, mock_client, ["fine-tuning", "delete", "ft-abc123"], input="y\n")
        assert result.exit_code == 0
        mock_client.fine_tuning.delete.assert_called_once()

    def test_fine_tuning_delete_interactive_no(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "delete", "ft-abc123"], input="n\n")
        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()
        mock_client.fine_tuning.delete.assert_not_called()

    def test_fine_tuning_delete_force_flag(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "ft-abc123"}
        mock_client.fine_tuning.delete.return_value = mock_response
        result = invoke(runner, mock_client, ["fine-tuning", "delete", "--quiet", "--force", "ft-abc123"])
        assert result.exit_code == 0
        mock_client.fine_tuning.delete.assert_called_once_with("ft-abc123", force=True)

    def test_fine_tuning_delete_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "delete"])
        assert result.exit_code != 0

    def test_fine_tuning_create_requires_training_file(self, runner, mock_client):
        result = invoke(runner, mock_client, ["fine-tuning", "create", "--model", "llama-3"])
        assert result.exit_code != 0

    def test_fine_tuning_create_requires_model_or_checkpoint(self, runner, mock_client):
        with patch("together.lib.cli.api.fine_tuning.create.get_model_limits"):
            result = invoke(runner, mock_client, ["fine-tuning", "create", "--training-file", "file-abc123"])
        assert result.exit_code != 0

    def test_fine_tuning_create_with_model_and_confirm(self, runner, mock_client):
        mock_limits = MagicMock()
        mock_limits.lora_training = None
        mock_limits.full_training = MagicMock()
        mock_limits.supports_vision = False
        mock_client.fine_tuning.estimate_price.return_value = MagicMock(
            estimated_total_price=10.0, allowed_to_proceed=True
        )
        mock_client.fine_tuning.create.return_value = MagicMock(id="ft-new123")
        with patch("together.lib.cli.api.fine_tuning.create.get_model_limits", return_value=mock_limits):
            result = invoke(
                runner,
                mock_client,
                ["fine-tuning", "create", "--training-file", "file-abc123", "--model", "llama-3", "--confirm"],
            )
        assert result.exit_code == 0
        mock_client.fine_tuning.create.assert_called_once()

    def test_fine_tuning_create_lora_flag(self, runner, mock_client):
        mock_limits = MagicMock()
        mock_limits.lora_training = MagicMock(max_rank=16)
        mock_limits.full_training = MagicMock()
        mock_limits.supports_vision = False
        mock_client.fine_tuning.estimate_price.return_value = MagicMock(
            estimated_total_price=5.0, allowed_to_proceed=True
        )
        mock_client.fine_tuning.create.return_value = MagicMock(id="ft-new456")
        with patch("together.lib.cli.api.fine_tuning.create.get_model_limits", return_value=mock_limits):
            result = invoke(
                runner,
                mock_client,
                [
                    "fine-tuning",
                    "create",
                    "--training-file",
                    "file-abc123",
                    "--model",
                    "llama-3",
                    "--lora",
                    "--confirm",
                ],
            )
        assert result.exit_code == 0

    def test_fine_tuning_create_n_epochs_option(self, runner, mock_client):
        mock_limits = MagicMock()
        mock_limits.lora_training = None
        mock_limits.full_training = MagicMock()
        mock_limits.supports_vision = False
        mock_client.fine_tuning.estimate_price.return_value = MagicMock(
            estimated_total_price=20.0, allowed_to_proceed=True
        )
        mock_client.fine_tuning.create.return_value = MagicMock(id="ft-new789")
        with patch("together.lib.cli.api.fine_tuning.create.get_model_limits", return_value=mock_limits):
            result = invoke(
                runner,
                mock_client,
                [
                    "fine-tuning",
                    "create",
                    "--training-file",
                    "file-abc123",
                    "--model",
                    "llama-3",
                    "--n-epochs",
                    "3",
                    "--confirm",
                ],
            )
        assert result.exit_code == 0
        call_kwargs = mock_client.fine_tuning.create.call_args
        assert call_kwargs.kwargs.get("n_epochs") == 3

    def test_fine_tuning_create_dpo_method(self, runner, mock_client):
        mock_limits = MagicMock()
        mock_limits.lora_training = None
        mock_limits.full_training = MagicMock()
        mock_limits.supports_vision = False
        mock_client.fine_tuning.estimate_price.return_value = MagicMock(
            estimated_total_price=10.0, allowed_to_proceed=True
        )
        mock_client.fine_tuning.create.return_value = MagicMock(id="ft-dpo123")
        with patch("together.lib.cli.api.fine_tuning.create.get_model_limits", return_value=mock_limits):
            result = invoke(
                runner,
                mock_client,
                [
                    "fine-tuning",
                    "create",
                    "--training-file",
                    "file-abc123",
                    "--model",
                    "llama-3",
                    "--training-method",
                    "dpo",
                    "--confirm",
                ],
            )
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# models commands
# ---------------------------------------------------------------------------


class TestModelsCLI:
    def test_models_help(self, runner, mock_client):
        result = invoke(runner, mock_client, ["models", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output

    def test_models_list_empty(self, runner, mock_client):
        mock_client.models.list.return_value = []
        result = invoke(runner, mock_client, ["models", "list"])
        assert result.exit_code == 0
        mock_client.models.list.assert_called_once()

    def test_models_list_json_empty(self, runner, mock_client):
        mock_client.models.list.return_value = []
        result = invoke(runner, mock_client, ["models", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == []

    def test_models_list_with_data(self, runner, mock_client):
        mock_model = MagicMock()
        mock_model.id = "llama-3-8b"
        mock_model.type = "chat"
        mock_model.context_length = 8192
        mock_model.pricing = MagicMock()
        mock_model.pricing.input = 0.2
        mock_model.pricing.output = 0.4
        mock_client.models.list.return_value = [mock_model]
        result = invoke(runner, mock_client, ["models", "list"])
        assert result.exit_code == 0

    def test_models_list_dedicated_type(self, runner, mock_client):
        mock_client.models.list.return_value = []
        result = invoke(runner, mock_client, ["models", "list", "--type", "dedicated"])
        assert result.exit_code == 0
        call_kwargs = mock_client.models.list.call_args
        assert call_kwargs.kwargs.get("dedicated") is True

    def test_models_list_no_type_filter(self, runner, mock_client):
        mock_client.models.list.return_value = []
        result = invoke(runner, mock_client, ["models", "list"])
        assert result.exit_code == 0
        # Without --type, dedicated should not be True
        call_kwargs = mock_client.models.list.call_args
        assert call_kwargs.kwargs.get("dedicated") is not True

    def test_models_list_invalid_type(self, runner, mock_client):
        result = invoke(runner, mock_client, ["models", "list", "--type", "invalid"])
        assert result.exit_code != 0

    def test_models_list_json_with_data(self, runner, mock_client):
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {"id": "llama-3", "type": "chat"}
        mock_client.models.list.return_value = [mock_model]
        result = invoke(runner, mock_client, ["models", "list", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "llama-3"

    def test_models_list_no_pricing(self, runner, mock_client):
        """Models without pricing should not crash."""
        mock_model = MagicMock()
        mock_model.id = "some-model"
        mock_model.type = "language"
        mock_model.context_length = None
        mock_model.pricing = MagicMock()
        mock_model.pricing.input = 0
        mock_model.pricing.output = 0
        mock_client.models.list.return_value = [mock_model]
        result = invoke(runner, mock_client, ["models", "list"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# endpoints commands
# ---------------------------------------------------------------------------


class TestEndpointsCLI:
    def test_endpoints_help(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "--help"])
        assert result.exit_code == 0
        for cmd in ["list", "retrieve", "create", "start", "stop", "delete", "hardware", "availability-zones"]:
            assert cmd in result.output

    def test_endpoints_list_empty(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list"])
        assert result.exit_code == 0
        mock_client.endpoints.list.assert_called_once()

    def test_endpoints_list_json_empty(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == []

    def test_endpoints_list_type_dedicated(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--type", "dedicated"])
        assert result.exit_code == 0

    def test_endpoints_list_type_serverless(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--type", "serverless"])
        assert result.exit_code == 0

    def test_endpoints_list_invalid_type(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "list", "--type", "invalid"])
        assert result.exit_code != 0

    def test_endpoints_list_mine_flag(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--mine"])
        assert result.exit_code == 0

    def test_endpoints_list_usage_type_on_demand(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--usage-type", "on-demand"])
        assert result.exit_code == 0

    def test_endpoints_list_usage_type_reserved(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.__bool__ = lambda self: False
        mock_client.endpoints.list.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "list", "--usage-type", "reserved"])
        assert result.exit_code == 0

    def test_endpoints_list_invalid_usage_type(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "list", "--usage-type", "invalid"])
        assert result.exit_code != 0

    def test_endpoints_retrieve(self, runner, mock_client):
        mock_endpoint = MagicMock()
        mock_client.endpoints.retrieve.return_value = mock_endpoint
        mock_client.print_endpoint = MagicMock()
        result = invoke(runner, mock_client, ["endpoints", "retrieve", "ep-abc123"])
        assert result.exit_code == 0
        mock_client.endpoints.retrieve.assert_called_once_with("ep-abc123")

    def test_endpoints_retrieve_json(self, runner, mock_client):
        mock_endpoint = MagicMock()
        mock_endpoint.model_dump.return_value = {"id": "ep-abc123", "state": "STARTED"}
        mock_client.endpoints.retrieve.return_value = mock_endpoint
        mock_client.print_endpoint = MagicMock()
        result = invoke(runner, mock_client, ["endpoints", "retrieve", "--json", "ep-abc123"])
        assert result.exit_code == 0

    def test_endpoints_retrieve_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "retrieve"])
        assert result.exit_code != 0

    def test_endpoints_start(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "ep-abc123", "state": "STARTED"}
        mock_client.endpoints.update.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "start", "ep-abc123"])
        assert result.exit_code == 0
        mock_client.endpoints.update.assert_called_once_with("ep-abc123", state="STARTED")

    def test_endpoints_start_json(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "ep-abc123", "state": "STARTED"}
        mock_client.endpoints.update.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "start", "--json", "ep-abc123"])
        assert result.exit_code == 0

    def test_endpoints_start_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "start"])
        assert result.exit_code != 0

    def test_endpoints_stop(self, runner, mock_client):
        mock_response = MagicMock()
        mock_client.endpoints.update.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "stop", "ep-abc123"])
        assert result.exit_code == 0
        mock_client.endpoints.update.assert_called_once_with("ep-abc123", state="STOPPED")

    def test_endpoints_stop_json(self, runner, mock_client):
        mock_response = MagicMock()
        mock_client.endpoints.update.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "stop", "--json", "ep-abc123"])
        assert result.exit_code == 0

    def test_endpoints_stop_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "stop"])
        assert result.exit_code != 0

    def test_endpoints_delete(self, runner, mock_client):
        mock_client.endpoints.delete.return_value = MagicMock()
        result = invoke(runner, mock_client, ["endpoints", "delete", "ep-abc123"])
        assert result.exit_code == 0
        mock_client.endpoints.delete.assert_called_once_with("ep-abc123")

    def test_endpoints_delete_json(self, runner, mock_client):
        mock_client.endpoints.delete.return_value = MagicMock()
        result = invoke(runner, mock_client, ["endpoints", "delete", "--json", "ep-abc123"])
        assert result.exit_code == 0

    def test_endpoints_delete_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["endpoints", "delete"])
        assert result.exit_code != 0

    def test_endpoints_hardware_list(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.endpoints.list_hardware.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "hardware"])
        assert result.exit_code == 0
        mock_client.endpoints.list_hardware.assert_called_once()

    def test_endpoints_hardware_json(self, runner, mock_client):
        mock_response = MagicMock()
        mock_hw = MagicMock()
        mock_hw.model_dump.return_value = {"id": "h100-80gb"}
        mock_response.data = [mock_hw]
        mock_client.endpoints.list_hardware.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "hardware", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert len(parsed) == 1

    def test_endpoints_hardware_model_filter(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.endpoints.list_hardware.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "hardware", "--model", "llama-3"])
        assert result.exit_code == 0
        call_kwargs = mock_client.endpoints.list_hardware.call_args
        assert call_kwargs.kwargs.get("model") == "llama-3"

    def test_endpoints_availability_zones(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.avzones = ["us-east-1", "us-west-2"]
        mock_response.__bool__ = lambda self: True
        mock_client.endpoints.list_avzones.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "availability-zones"])
        assert result.exit_code == 0
        mock_client.endpoints.list_avzones.assert_called_once()

    def test_endpoints_availability_zones_json(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"avzones": ["us-east-1"]}
        mock_client.endpoints.list_avzones.return_value = mock_response
        result = invoke(runner, mock_client, ["endpoints", "availability-zones", "--json"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# evals commands
# ---------------------------------------------------------------------------


class TestEvalsCLI:
    def test_evals_help(self, runner, mock_client):
        result = invoke(runner, mock_client, ["evals", "--help"])
        assert result.exit_code == 0
        for cmd in ["create", "list", "retrieve", "status"]:
            assert cmd in result.output

    def test_evals_list_empty(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list"])
        assert result.exit_code == 0
        mock_client.evals.list.assert_called_once()

    def test_evals_list_with_data(self, runner, mock_client):
        mock_job = MagicMock()
        mock_job.workflow_id = "eval-abc123"
        mock_job.type = "score"
        mock_job.status = "completed"
        mock_job.created_at = 1704067200
        mock_job.parameters = {"model_to_evaluate": "llama-3", "model_a": "", "model_b": ""}
        mock_client.evals.list.return_value = [mock_job]
        result = invoke(runner, mock_client, ["evals", "list"])
        assert result.exit_code == 0

    def test_evals_list_status_pending(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list", "--status", "pending"])
        assert result.exit_code == 0

    def test_evals_list_status_running(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list", "--status", "running"])
        assert result.exit_code == 0

    def test_evals_list_status_completed(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list", "--status", "completed"])
        assert result.exit_code == 0

    def test_evals_list_status_error(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list", "--status", "error"])
        assert result.exit_code == 0

    def test_evals_list_invalid_status(self, runner, mock_client):
        result = invoke(runner, mock_client, ["evals", "list", "--status", "not-a-status"])
        assert result.exit_code != 0

    def test_evals_list_with_limit(self, runner, mock_client):
        mock_client.evals.list.return_value = []
        result = invoke(runner, mock_client, ["evals", "list", "--limit", "10"])
        assert result.exit_code == 0

    def test_evals_list_invalid_limit(self, runner, mock_client):
        result = invoke(runner, mock_client, ["evals", "list", "--limit", "not-a-number"])
        assert result.exit_code != 0

    def test_evals_retrieve(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"workflow_id": "eval-abc123", "status": "completed"}
        mock_client.evals.retrieve.return_value = mock_response
        result = invoke(runner, mock_client, ["evals", "retrieve", "eval-abc123"])
        assert result.exit_code == 0
        mock_client.evals.retrieve.assert_called_once_with("eval-abc123")

    def test_evals_retrieve_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["evals", "retrieve"])
        assert result.exit_code != 0

    def test_evals_status(self, runner, mock_client):
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"workflow_id": "eval-abc123", "status": "running"}
        mock_client.evals.status.return_value = mock_response
        result = invoke(runner, mock_client, ["evals", "status", "eval-abc123"])
        assert result.exit_code == 0
        mock_client.evals.status.assert_called_once_with("eval-abc123")

    def test_evals_status_requires_id(self, runner, mock_client):
        result = invoke(runner, mock_client, ["evals", "status"])
        assert result.exit_code != 0
