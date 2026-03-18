# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import subprocess
import json
import os

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

def run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["together", "--base-url", base_url, "endpoints", *command.split(" "), "--json"], capture_output=True, text=True)

def assert_command_returns_json(command: str) -> None:
    result = run_command(command)
    assert result.returncode == 0
    assert result.stdout is not None
    assert json.loads(result.stdout) is not None

class TestEndpoints:
    def test_json_mode_is_supported(self) -> None:
        assert_command_returns_json("hardware")
        assert_command_returns_json("hardware --model deepseek-ai/DeepSeek-R1")
        assert_command_returns_json("availability-zones")
        assert_command_returns_json("list")
        assert_command_returns_json("list --type dedicated")
        assert_command_returns_json("list --usage-type on-demand")
        assert_command_returns_json("list --usage-type reserved")
        assert_command_returns_json("list --mine")
        assert_command_returns_json("create --model deepseek-ai/DeepSeek-R1 --hardware 1x_nvidia_a100_80gb_sxm")
        assert_command_returns_json("delete endpoint-123")
        assert_command_returns_json("start endpoint-123")
        assert_command_returns_json("stop endpoint-123")
        assert_command_returns_json("retrieve endpoint-123")
        assert_command_returns_json("update endpoint-123 --min-replicas 2 --max-replicas 4 --inactive-timeout 60")
    
    def test_create_requires_model(self) -> None:
        result = run_command("create")
        assert result.returncode == 2
        assert "Error: Missing option '--model'." in result.stderr

    def test_create_requires_hardware(self) -> None:
        result = run_command("create --model deepseek-ai/DeepSeek-R1 --hardware ''")
        assert result.returncode == 1
        assert "Invalid hardware selected." in result.stderr