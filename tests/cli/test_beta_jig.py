from __future__ import annotations

import os
import sys
import json
from typing import Any, cast
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter
from respx.models import Call
from click.testing import CliRunner

from together.lib.cli import main

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"
_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}

# Imported into jig CLI module namespace
_jig_mod = sys.modules["together.lib.cli.api.beta.jig.jig"]

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
    def test_set_creates_when_update_returns_not_found(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        scoped = f"{_DEPLOY_NAME}-apikey"
        respx_mock.get(f"/deployments/{_DEPLOY_NAME}").mock(return_value=httpx.Response(404, json={}))
        respx_mock.patch(f"/deployments/secrets/{scoped}").mock(return_value=httpx.Response(404, json={}))
        post = respx_mock.post("/deployments/secrets").mock(
            return_value=httpx.Response(200, json=_secret_api_body(scoped))
        )

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(
                main,
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
        assert result.exit_code == 0
        assert "Created secret apikey" in result.output
        raw = cast(Call, post.calls[0]).request.content.decode()
        body = json.loads(raw)
        assert body["name"] == scoped
        assert body["value"] == "secret-val"
        assert body["description"] == "d1"
        state = json.loads((tmp_path / ".jig.json").read_text())
        assert state[_DEPLOY_NAME]["secrets"]["apikey"] == scoped

    @pytest.mark.respx(base_url=base_url)
    def test_set_updates_when_secret_exists(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        scoped = f"{_DEPLOY_NAME}-apikey"
        respx_mock.get(f"/deployments/{_DEPLOY_NAME}").mock(return_value=httpx.Response(404, json={}))
        patch_route = respx_mock.patch(f"/deployments/secrets/{scoped}").mock(
            return_value=httpx.Response(200, json=_secret_api_body(scoped))
        )

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(
                main,
                ["beta", "jig", "secrets", "set", "--name", "apikey", "--value", "v2"],
            )
        assert result.exit_code == 0
        assert "Updated secret apikey" in result.output
        assert patch_route.called
        raw = cast(Call, patch_route.calls[0]).request.content.decode()
        assert json.loads(raw)["value"] == "v2"


class TestBetaJigSecretsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_merges_local_and_remote(self, respx_mock: MockRouter, tmp_path: Path) -> None:
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

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "secrets", "list"])
        assert result.exit_code == 0
        assert "localonly" in result.output
        assert "remoteonly" in result.output
        assert "synced" in result.output or "local only" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_empty_message(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        respx_mock.get("/deployments/secrets").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": []})
        )

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "secrets", "list"])
        assert result.exit_code == 0
        assert "No secrets configured" in result.output


class TestBetaJigSecretsUnset:
    def test_unset_removes_known_secret(self, tmp_path: Path) -> None:
        (tmp_path / ".jig.json").write_text(
            json.dumps({_DEPLOY_NAME: {"secrets": {"tok": f"{_DEPLOY_NAME}-tok"}}}),
            encoding="utf-8",
        )

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "secrets", "unset", "--name", "tok"])
        assert result.exit_code == 0
        assert "Deleted secret tok" in result.output
        state = json.loads((tmp_path / ".jig.json").read_text())
        assert "tok" not in state[_DEPLOY_NAME].get("secrets", {})

    def test_unset_missing_secret_message(self, tmp_path: Path) -> None:
        (tmp_path / ".jig.json").write_text(
            json.dumps({_DEPLOY_NAME: {"secrets": {}}}),
            encoding="utf-8",
        )

        runner = CliRunner(env=_ENV)
        with _patched_jig_config(tmp_path), _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "secrets", "unset", "--name", "nope"])
        assert result.exit_code == 0
        assert "Secret nope is not set" in result.output


class TestBetaJigVolumes:
    @pytest.mark.respx(base_url=base_url)
    def test_delete(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        _write_jig_project(tmp_path)
        respx_mock.delete("/deployments/storage/volumes/data-vol").mock(return_value=httpx.Response(200, json={}))

        runner = CliRunner(env=_ENV)
        with _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "volumes", "delete", "--name", "data-vol"])
        assert result.exit_code == 0
        assert "Deleted volume data-vol" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_delete_not_found(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        _write_jig_project(tmp_path)
        respx_mock.delete("/deployments/storage/volumes/missing").mock(
            return_value=httpx.Response(404, json={"error": {"message": "not found"}})
        )

        runner = CliRunner(env=_ENV)
        with _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "volumes", "delete", "--name", "missing"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    @pytest.mark.respx(base_url=base_url)
    def test_describe_json(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        _write_jig_project(tmp_path)
        payload = _volume_api_body("v1", current_version=2)
        respx_mock.get("/deployments/storage/volumes/v1").mock(return_value=httpx.Response(200, json=payload))

        runner = CliRunner(env=_ENV)
        with _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "volumes", "describe", "--name", "v1"])
        assert result.exit_code == 0
        assert json.loads(result.output) == payload

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, tmp_path: Path) -> None:
        _write_jig_project(tmp_path)
        payload = {"object": "list", "data": [_volume_api_body("a"), _volume_api_body("b")]}
        respx_mock.get("/deployments/storage/volumes").mock(return_value=httpx.Response(200, json=payload))

        runner = CliRunner(env=_ENV)
        with _chdir(tmp_path):
            result = runner.invoke(main, ["beta", "jig", "volumes", "list"])
        assert result.exit_code == 0
        assert json.loads(result.output) == payload

    @pytest.mark.respx(base_url=base_url)
    def test_create_invokes_upload(self, respx_mock: MockRouter, tmp_path: Path) -> None:
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
            runner = CliRunner(env=_ENV)
            with _chdir(tmp_path):
                result = runner.invoke(
                    main,
                    ["beta", "jig", "volumes", "create", "--name", "myvol", "--source", str(src)],
                )

        assert result.exit_code == 0
        assert uploaded == [(src, "myvol/0")]
        assert "Volume created" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_create_rolls_back_on_upload_failure(self, respx_mock: MockRouter, tmp_path: Path) -> None:
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
            runner = CliRunner(env=_ENV)
            with _chdir(tmp_path):
                result = runner.invoke(
                    main,
                    ["beta", "jig", "volumes", "create", "--name", "badvol", "--source", str(src)],
                )

        assert result.exit_code == 1
        assert del_vol.called

    @pytest.mark.respx(base_url=base_url)
    def test_update_bumps_version_and_uploads(self, respx_mock: MockRouter, tmp_path: Path) -> None:
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
            runner = CliRunner(env=_ENV)
            with _chdir(tmp_path):
                result = runner.invoke(
                    main,
                    ["beta", "jig", "volumes", "update", "--name", "shared", "--source", str(src)],
                )

        assert result.exit_code == 0
        assert uploaded == [(src, "shared/4")]
        assert patch_r.called
        patch_body = json.loads(cast(Call, patch_r.calls[0]).request.content.decode())
        assert patch_body["content"] == {"type": "files", "source_prefix": "shared/4"}
