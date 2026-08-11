from __future__ import annotations

import os
import json
from typing import Any, cast
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

import together.lib.cli.api.beta.jig.jig as _jig_mod
from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

_DEPLOY_NAME = "jig-cli-test"


@contextmanager
def _chdir(path: Path):
    prev = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


def _noop_config_post_init(_self: Any) -> None:
    """Stub replacing Config.__post_init__ when skipping validation in tests."""
    return None


@contextmanager
def _patched_jig_config(tmp_path: Path):
    """Avoid Config.find() + validate on py3.9 (DeployConfig uses PEP 604 hints)."""
    with patch.object(_jig_mod.Config, "__post_init__", _noop_config_post_init):
        cfg = _jig_mod.Config(
            model_name=_DEPLOY_NAME,
            image=_jig_mod.ImageConfig(),
            deploy=_jig_mod.DeployConfig(),
            _path=tmp_path / "pyproject.toml",
            _unique_name_hint="h",
        )

        def _find(*_args: Any):
            return cfg

        with patch.object(_jig_mod.Config, "find", classmethod(_find)):
            yield


_PYPROJECT = f"""[project]
name = "{_DEPLOY_NAME}"
version = "0.1.0"

[tool.jig.image]
python_version = "3.11"
cmd = "python app.py"

[tool.jig.deploy]
description = "test"
gpu_type = "h100-80gb"
gpu_count = 1
"""


def _write_jig_project(path: Path) -> None:
    path.joinpath("pyproject.toml").write_text(_PYPROJECT, encoding="utf-8")


def test_jig_failure_exit_preserves_diagnostic(capsys: pytest.CaptureFixture[str]) -> None:
    message = "Volume example not found"

    with pytest.raises(SystemExit) as exc_info:
        _jig_mod._jig_fail(message)

    assert exc_info.value.code == 1
    assert str(exc_info.value) == message
    assert f"Jig: Failed {message}" in capsys.readouterr().out


def _secret_api_body(name: str) -> dict[str, object]:
    return {
        "id": "sec-1",
        "name": name,
        "object": "secret",
        "description": "",
    }


def _volume_api_body(name: str, **extra: object) -> dict[str, object]:
    body: dict[str, object] = {
        "id": "vol-id-1",
        "name": name,
        "object": "volume",
        "type": "readOnly",
        "current_version": 0,
    }
    body.update(extra)
    return body


class TestBetaJigSecretsSet:
    @pytest.mark.respx(base_url=base_url)
    def test_set_creates_when_update_returns_not_found(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        scoped = f"{_DEPLOY_NAME}-apikey"
        respx_mock.get(f"/deployments/{_DEPLOY_NAME}").mock(return_value=httpx.Response(404, json={}))
        respx_mock.patch(f"/deployments/secrets/{scoped}").mock(return_value=httpx.Response(404, json={}))
        post = respx_mock.post("/deployments/secrets").mock(
            return_value=httpx.Response(200, json=_secret_api_body(scoped))
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(
                [
                    "beta",
                    "jig",
                    "secrets",
                    "set",
                    "--name",
                    "apikey",
                    "--value",
                    "secret-val",
                    "--description",
                    "d1",
                ],
            )
        assert "Created secret apikey" in result.output
        raw = cast(Call, post.calls[0]).request.content.decode()
        body = json.loads(raw)
        assert body["name"] == scoped
        assert body["value"] == "secret-val"
        assert body["description"] == "d1"
        state = json.loads((tmp_path / ".jig.json").read_text())
        assert state[_DEPLOY_NAME]["secrets"]["apikey"] == scoped
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_set_updates_when_secret_exists(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        scoped = f"{_DEPLOY_NAME}-apikey"
        respx_mock.get(f"/deployments/{_DEPLOY_NAME}").mock(return_value=httpx.Response(404, json={}))
        patch_route = respx_mock.patch(f"/deployments/secrets/{scoped}").mock(
            return_value=httpx.Response(200, json=_secret_api_body(scoped))
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(
                ["beta", "jig", "secrets", "set", "--name", "apikey", "--value", "v2"],
            )
        assert "Updated secret apikey" in result.output
        assert patch_route.called
        raw = cast(Call, patch_route.calls[0]).request.content.decode()
        assert json.loads(raw)["value"] == "v2"
        assert result.exit_code == 0


class TestBetaJigSecretsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_merges_local_and_remote(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        (tmp_path / ".jig.json").write_text(
            json.dumps({_DEPLOY_NAME: {"secrets": {"localonly": f"{_DEPLOY_NAME}-localonly"}}}),
            encoding="utf-8",
        )
        respx_mock.get("/deployments/secrets").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {"name": f"{_DEPLOY_NAME}-localonly", "object": "secret"},
                        {"name": f"{_DEPLOY_NAME}-remoteonly", "object": "secret"},
                        {"name": "other-project-x", "object": "secret"},
                    ],
                },
            )
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "secrets", "list"])
        assert "localonly" in result.output
        assert "remoteonly" in result.output
        assert "synced" in result.output or "local only" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_list_empty_message(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        respx_mock.get("/deployments/secrets").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": []})
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "secrets", "list"])
        assert "No secrets configured" in result.output
        assert result.exit_code == 0


class TestBetaJigSecretsUnset:
    def test_unset_removes_known_secret(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        (tmp_path / ".jig.json").write_text(
            json.dumps({_DEPLOY_NAME: {"secrets": {"tok": f"{_DEPLOY_NAME}-tok"}}}),
            encoding="utf-8",
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "secrets", "unset", "--name", "tok"])
        assert result.exit_code == 0
        assert "Removed secret tok" in result.output
        state = json.loads((tmp_path / ".jig.json").read_text())
        assert "tok" not in state[_DEPLOY_NAME].get("secrets", {})
        assert result.exit_code == 0

    def test_unset_missing_secret_message(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        (tmp_path / ".jig.json").write_text(
            json.dumps({_DEPLOY_NAME: {"secrets": {}}}),
            encoding="utf-8",
        )

        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "secrets", "unset", "--name", "nope"])
        assert "Secret nope is not set" in result.output
        assert result.exit_code == 0


class TestBetaJigBuild:
    def test_build_blocked_when_deploy_image_set(self, tmp_path: Path, cli_runner: CliRunner) -> None:
        with patch.object(_jig_mod.Config, "__post_init__", _noop_config_post_init):
            cfg = _jig_mod.Config(
                model_name=_DEPLOY_NAME,
                image=_jig_mod.ImageConfig(),
                deploy=_jig_mod.DeployConfig(image="ghcr.io/org/prebuilt:latest"),
                _path=tmp_path / "pyproject.toml",
                _unique_name_hint="h",
            )

            def _find(*_args: Any):
                return cfg

            with patch.object(_jig_mod.Config, "find", classmethod(_find)):
                with _chdir(tmp_path):
                    result = cli_runner.invoke(["beta", "jig", "build"])
        assert result.exit_code == 1
        assert "deploy.image is set" in result.output


class TestBetaJigLogs:
    @pytest.mark.respx(base_url=base_url)
    def test_logs_forwards_sdk_filters(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        route = respx_mock.get(f"/deployments/{_DEPLOY_NAME}/logs").mock(
            return_value=httpx.Response(200, json={"lines": ["line 1", "line 2"]})
        )

        with _chdir(tmp_path):
            result = cli_runner.invoke(
                [
                    "beta",
                    "jig",
                    "logs",
                    "--replica-id",
                    "replica-1",
                    "--revision",
                    "revision-1",
                    "--image-version",
                    "v2",
                ]
            )

        assert "line 1" in result.output
        assert "line 2" in result.output
        request = cast(Call, route.calls[0]).request
        assert request.url.params["replica_id"] == "replica-1"
        assert request.url.params["revision"] == "revision-1"
        assert request.url.params["version"] == "v2"
        assert result.exit_code == 0


class TestBetaJigVolumes:
    @pytest.mark.respx(base_url=base_url)
    def test_delete(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        respx_mock.delete("/deployments/storage/volumes/data-vol").mock(return_value=httpx.Response(200, json={}))

        with _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "volumes", "delete", "--name", "data-vol"])
        assert "Deleted volume data-vol" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_delete_not_found(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        respx_mock.delete("/deployments/storage/volumes/missing").mock(
            return_value=httpx.Response(404, json={"error": {"message": "not found"}})
        )

        with _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "volumes", "delete", "--name", "missing"])
        assert "not found" in result.output.lower()
        assert result.exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_describe_json(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        payload = _volume_api_body("v1", current_version=2)
        respx_mock.get("/deployments/storage/volumes/v1").mock(return_value=httpx.Response(200, json=payload))

        with _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "volumes", "describe", "--name", "v1", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_describe_forwards_version(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        route = respx_mock.get("/deployments/storage/volumes/v1").mock(
            return_value=httpx.Response(200, json=_volume_api_body("v1", current_version=1))
        )

        with _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "volumes", "describe", "--name", "v1", "--volume-version", "1"])

        assert "version" in result.output
        request = cast(Call, route.calls[0]).request
        assert request.url.params["version"] == "1"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        payload = {"object": "list", "data": [_volume_api_body("a"), _volume_api_body("b")]}
        respx_mock.get("/deployments/storage/volumes").mock(return_value=httpx.Response(200, json=payload))

        with _chdir(tmp_path):
            result = cli_runner.invoke(["beta", "jig", "volumes", "list", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_create_invokes_upload(self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner) -> None:
        _write_jig_project(tmp_path)
        src = tmp_path / "srcdir"
        src.mkdir()
        (src / "f.txt").write_text("x", encoding="utf-8")

        respx_mock.post("/deployments/storage/volumes").mock(
            return_value=httpx.Response(200, json=_volume_api_body("myvol"))
        )

        uploaded: list[tuple[Path, str]] = []

        class _FakeUploader:
            def __init__(self, _client: object) -> None:
                pass

            async def upload_files(self, source: Path, prefix: str) -> None:
                uploaded.append((source, prefix))

        with patch.object(_jig_mod, "Uploader", _FakeUploader):
            with _chdir(tmp_path):
                result = cli_runner.invoke(
                    ["beta", "jig", "volumes", "create", "--name", "myvol", "--source", str(src)]
                )

        assert uploaded == [(src, "myvol/0")]
        assert "Volume created" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_create_rolls_back_on_upload_failure(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        _write_jig_project(tmp_path)
        src = tmp_path / "srcdir"
        src.mkdir()

        respx_mock.post("/deployments/storage/volumes").mock(
            return_value=httpx.Response(200, json=_volume_api_body("badvol"))
        )
        del_vol = respx_mock.delete("/deployments/storage/volumes/badvol").mock(
            return_value=httpx.Response(200, json={})
        )

        class _FakeUploader:
            def __init__(self, _client: object) -> None:
                pass

            async def upload_files(self, _source: Path, _prefix: str) -> None:
                raise RuntimeError("upload boom")

        with patch.object(_jig_mod, "Uploader", _FakeUploader):
            with _chdir(tmp_path):
                result = cli_runner.invoke(
                    ["beta", "jig", "volumes", "create", "--name", "badvol", "--source", str(src)],
                )

        assert del_vol.called
        assert result.exit_code == 1

    @pytest.mark.respx(base_url=base_url)
    def test_update_bumps_version_and_uploads(
        self, respx_mock: MockRouter, tmp_path: Path, cli_runner: CliRunner
    ) -> None:
        _write_jig_project(tmp_path)
        src = tmp_path / "newsrc"
        src.mkdir()
        (src / "a.bin").write_bytes(b"\0")

        respx_mock.get("/deployments/storage/volumes/shared").mock(
            return_value=httpx.Response(200, json=_volume_api_body("shared", current_version=3))
        )
        patch_r = respx_mock.patch("/deployments/storage/volumes/shared").mock(
            return_value=httpx.Response(200, json=_volume_api_body("shared", current_version=4))
        )

        uploaded: list[tuple[Path, str]] = []

        class _FakeUploader:
            def __init__(self, _client: object) -> None:
                pass

            async def upload_files(self, source: Path, prefix: str) -> None:
                uploaded.append((source, prefix))

        with patch.object(_jig_mod, "Uploader", _FakeUploader):
            with _chdir(tmp_path):
                result = cli_runner.invoke(
                    ["beta", "jig", "volumes", "update", "--name", "shared", "--source", str(src)],
                )

        assert uploaded == [(src, "shared/4")]
        assert patch_r.called
        patch_body = json.loads(cast(Call, patch_r.calls[0]).request.content.decode())
        assert patch_body["content"] == {"type": "files", "source_prefix": "shared/4"}
        assert result.exit_code == 0
