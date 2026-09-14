from __future__ import annotations

import os
import json
import hashlib
from typing import Any, cast
from pathlib import Path

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _whoami_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "api_key_id": "key-1",
        "organization_id": "org-1",
        "organization_name": "Acme",
        "project_id": "proj",
        "project_name": "My Project",
        "project_slug": "my-project",
        "user_id": "user-1",
    }
    body.update(overrides)
    return body


def _model_body(model_id: str = "ml_1", name: str = "my-project/my-model", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": model_id,
        "projectId": "proj",
        "organizationId": "org-1",
        "name": name,
        "baseModelId": "ml_base",
        "visibility": "VISIBILITY_PRIVATE",
        "weights": {"architecture": "llama", "type": "WEIGHTS_TYPE_DEFAULT"},
        "description": "a model",
    }
    body.update(overrides)
    return body


def _files_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "object": "list",
        "revisionId": "rev-1",
        "revisionCreatedAt": "2026-01-01T00:00:00Z",
        "totalSizeBytes": "11",
        "data": [
            {
                "path": "weights.bin",
                "sizeBytes": "11",
                "hash": hashlib.md5(b"hello world").hexdigest(),
            }
        ],
        "next_cursor": None,
    }
    body.update(overrides)
    return body


def _config_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "cr_1",
        "projectId": "proj",
        "referenceModel": "projects/proj/models/ml_1",
        "referenceModelId": "ml_1",
        "selectors": [{"key": "gpu", "value": "H100"}],
        "certifications": [],
    }
    body.update(overrides)
    return body


def _remote_upload_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ru_1",
        "projectId": "proj",
        "modelId": "ml_1",
        "remoteUrl": "https://huggingface.co/acme/model",
        "status": "REMOTE_UPLOAD_STATUS_PENDING",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _supported_model_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ml_base",
        "name": "meta-llama/Llama-3-8B",
        "displayName": "Llama 3 8B",
        "displayType": "chat",
        "baseModel": "projects/together/models/ml_base",
        "baseModelId": "ml_base",
        "capabilities": ["CAPABILITY_CHAT"],
        "createdAt": "2026-01-01T00:00:00Z",
        "inputModalities": ["MODALITY_TEXT"],
        "outputModalities": ["MODALITY_TEXT"],
        "products": ["PRODUCT_DEDICATED"],
        "publisher": "meta",
        "status": "SUPPORTED_MODEL_STATUS_SUPPORTED",
        "deploymentProfiles": [
            {
                "profileId": "cr_1",
                "certifiedConfigRevisionId": "cr_1",
                "certifiedModelRevisionId": "rev-1",
                "config": "projects/together/configs/cr_1",
                "model": "projects/together/models/ml_base",
                "modelName": "meta-llama/Llama-3-8B-FP16",
                "gpuCount": 1,
                "gpuType": "H100",
                "parallelism": "TP1",
                "quantization": "fp16",
                "performanceBenchmarks": {},
            }
        ],
    }
    body.update(overrides)
    return body


class TestBetaModelsCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_posts_name_base_model_and_type(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/projects/proj/models").mock(return_value=httpx.Response(200, json=_model_body()))

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "create",
                "my-model",
                "--project",
                "proj",
                "--base-model",
                "ml_base",
                "--type",
                "model",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {
            "name": "my-model",
            "baseModelId": "ml_base",
            "type": "model",
        }
        assert json.loads(result.output)["id"] == "ml_1"
        # Model ids are passed through — no supported-models lookup.
        assert not any(call.request.url.path == "/supported-models" for call in cast(list[Call], respx_mock.calls))

    @pytest.mark.respx(base_url=base_url)
    def test_create_resolves_base_model_name_via_supported_models(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        supported_route = respx_mock.get("/supported-models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_supported_model_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/models").mock(
            return_value=httpx.Response(200, json=_model_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "create",
                "my-model",
                "--project",
                "proj",
                "--base-model",
                "meta-llama/Llama-3-8B-FP16",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert "search=meta-llama%2FLlama-3-8B-FP16" in str(cast(Call, supported_route.calls[0]).request.url)
        assert json.loads(cast(Call, create_route.calls[0]).request.content.decode()) == {
            "name": "my-model",
            "baseModelId": "ml_base",
            "type": "model",
        }

    @pytest.mark.respx(base_url=base_url)
    def test_create_rejects_unmatched_base_model_name_with_candidates(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/supported-models").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _supported_model_body(
                            deploymentProfiles=[
                                {
                                    "profileId": "cr_1",
                                    "certifiedConfigRevisionId": "cr_1",
                                    "certifiedModelRevisionId": "rev-1",
                                    "config": "projects/together/configs/cr_1",
                                    "model": "projects/together/models/ml_base",
                                    "modelName": "meta-llama/Llama-3-8B-FP16",
                                    "gpuCount": 1,
                                    "gpuType": "H100",
                                    "parallelism": "TP1",
                                    "quantization": "fp16",
                                    "performanceBenchmarks": {},
                                },
                                {
                                    "profileId": "cr_2",
                                    "certifiedConfigRevisionId": "cr_2",
                                    "certifiedModelRevisionId": "rev-2",
                                    "config": "projects/together/configs/cr_2",
                                    "model": "projects/together/models/ml_base_fp8",
                                    "modelName": "meta-llama/Llama-3-8B-FP8",
                                    "gpuCount": 1,
                                    "gpuType": "H100",
                                    "parallelism": "TP1",
                                    "quantization": "fp8",
                                    "performanceBenchmarks": {},
                                },
                            ]
                        )
                    ],
                    "next_cursor": None,
                },
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "create",
                "my-model",
                "--project",
                "proj",
                "--base-model",
                "meta-llama/Llama-3-8B",
                "--json",
            ]
        )

        assert result.exit_code != 0
        assert "No exact match for base model" in result.output
        assert "meta-llama/Llama-3-8B-FP16" in result.output
        assert "ml_base" in result.output
        assert "meta-llama/Llama-3-8B-FP8" in result.output
        assert "ml_base_fp8" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_create_requires_explicit_project_in_json_mode(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        # Meta still resolves the client project via whoami when --project / env are omitted.
        cli_runner.env.pop("TOGETHER_PROJECT_ID", None)
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))

        result = cli_runner.invoke(["beta", "models", "create", "my-model", "--base-model", "ml_base", "--json"])
        assert result.exit_code != 0
        assert "Project argument is required" in result.output


class TestBetaModelsUpdate:
    @pytest.mark.respx(base_url=base_url)
    def test_update_sends_mask_and_payload(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.patch("/projects/proj/models/ml_1").mock(
            return_value=httpx.Response(200, json=_model_body(name="my-project/renamed"))
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "update",
                "ml_1",
                "--project",
                "proj",
                "--name",
                "renamed",
                "--description",
                "updated",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        req = cast(Call, route.calls[0]).request
        assert "updateMask=name%2Cdescription" in str(req.url)
        assert json.loads(req.content.decode()) == {"name": "renamed", "description": "updated"}

    def test_update_requires_option(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["beta", "models", "update", "ml_1", "--project", "proj"])
        assert result.exit_code != 0
        assert "At least one update option must be specified" in result.output


class TestBetaModelsList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_sends_cursor_pagination(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_model_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            ["beta", "models", "list", "--project", "proj", "--limit", "10", "--after", "tok", "--json"]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=10" in url
        assert "after=tok" in url
        assert json.loads(result.output)["next_cursor"] == "next"


class TestBetaModelsPublic:
    @pytest.mark.respx(base_url=base_url)
    def test_public_maps_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/supported-models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_supported_model_body()], "next_cursor": "c1"},
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "public",
                "--project",
                "proj",
                "--search",
                "llama",
                "--limit",
                "5",
                "--after",
                "tok",
                "--modality",
                "text",
                "--product",
                "dedicated",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "search=llama" in url
        assert "limit=5" in url
        assert "after=tok" in url
        assert "modality=MODALITY_TEXT" in url
        assert "product=PRODUCT_DEDICATED" in url
        assert json.loads(result.output)["next_cursor"] == "c1"

    @pytest.mark.respx(base_url=base_url)
    def test_public_table_shows_profile_model_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/supported-models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_supported_model_body()], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(["beta", "models", "public", "--project", "proj"])

        assert result.exit_code == 0, result.output
        assert "meta-llama/Llama-3-8B-FP16" in result.output
        assert "1x H100" in result.output
        assert "TP1" in result.output
        assert "cr_1" not in result.output


class TestBetaModelsOrg:
    @pytest.mark.respx(base_url=base_url)
    def test_org_lists_org_scoped_models(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        route = respx_mock.get("/organizations/org-1/models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_model_body()], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(
            ["beta", "models", "org", "--project", "proj", "--limit", "3", "--after", "tok", "--json"]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=3" in url
        assert "after=tok" in url
        assert json.loads(result.output)["data"][0]["id"] == "ml_1"


class TestBetaModelsRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_includes_files(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json=_model_body()))
        respx_mock.get("/projects/proj/models/ml_1/files").mock(return_value=httpx.Response(200, json=_files_body()))

        result = cli_runner.invoke(["beta", "models", "get", "ml_1", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["id"] == "ml_1"
        assert payload["revisionId"] == "rev-1"
        assert payload["files"][0]["path"] == "weights.bin"


class TestBetaModelsRm:
    @pytest.mark.respx(base_url=base_url)
    def test_rm_deletes_model(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.delete("/projects/proj/models/ml_1").mock(return_value=httpx.Response(200, json={}))

        result = cli_runner.invoke(["beta", "models", "rm", "ml_1", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        assert route.call_count == 1
        assert json.loads(result.output)["message"] == "Successfully deleted beta model"


class TestBetaModelsListFiles:
    @pytest.mark.respx(base_url=base_url)
    def test_ls_files_passes_revision(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/models/ml_1/files").mock(
            return_value=httpx.Response(200, json=_files_body())
        )

        result = cli_runner.invoke(
            ["beta", "models", "ls-files", "ml_1", "--project", "proj", "--revision", "rev-1", "--json"]
        )

        assert result.exit_code == 0, result.output
        assert "revisionId=rev-1" in str(cast(Call, route.calls[0]).request.url)
        assert json.loads(result.output)["revisionId"] == "rev-1"


class TestBetaModelsListRevisions:
    @pytest.mark.respx(base_url=base_url)
    def test_ls_revisions(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/models/ml_1/revisions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {
                            "revisionId": "rev-1",
                            "createdAt": "2026-01-01T00:00:00Z",
                            "validationStatus": "REVISION_VALIDATION_STATUS_SUCCESS",
                            "lastValidatedAt": "2026-01-01T00:05:00Z",
                        }
                    ],
                },
            )
        )

        result = cli_runner.invoke(["beta", "models", "ls-revisions", "ml_1", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        row = json.loads(result.output)["data"][0]
        assert row["revisionId"] == "rev-1"
        assert row["validationStatus"] == "REVISION_VALIDATION_STATUS_SUCCESS"

    @pytest.mark.respx(base_url=base_url)
    def test_ls_revisions_table_shows_validation(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/models/ml_1/revisions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {
                            "revisionId": "rev-1",
                            "createdAt": "2026-01-01T00:00:00Z",
                            "validationStatus": "REVISION_VALIDATION_STATUS_FAILED",
                            "lastValidatedAt": "2026-01-01T00:05:00Z",
                        }
                    ],
                },
            )
        )

        result = cli_runner.invoke(["beta", "models", "ls-revisions", "ml_1", "--project", "proj"])

        assert result.exit_code == 0, result.output
        assert "rev-1" in result.output
        assert "Failed" in result.output
        assert "Validation" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_ls_revisions_table_renders_legacy_numeric_fields(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/projects/proj/models/19/revisions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {
                            "revisionId": 123,
                            "createdAt": "2026-01-01T00:00:00Z",
                            "validationStatus": "REVISION_VALIDATION_STATUS_SUCCESS",
                        },
                        {
                            "revisionId": "rev-2",
                            "createdAt": "2026-01-01T00:00:00Z",
                            "validationStatus": 314159,
                        },
                    ],
                },
            )
        )

        result = cli_runner.invoke(["beta", "models", "ls-revisions", "19", "--project", "proj"])

        assert result.exit_code == 0, result.output
        assert "123" in result.output
        assert "rev-2" in result.output
        assert "314159" in result.output


class TestBetaModelsConfigs:
    @pytest.mark.respx(base_url=base_url)
    def test_configs_filters_by_model(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_config_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "configs",
                "ml_1",
                "--project",
                "proj",
                "--limit",
                "5",
                "--after",
                "tok",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "referenceModelId=ml_1" in url
        assert "limit=5" in url
        assert "after=tok" in url
        assert json.loads(result.output)["next_cursor"] == "next"

    @pytest.mark.respx(base_url=base_url)
    def test_configs_accepts_model_resource_path(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [_config_body()], "next_cursor": None})
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "configs",
                "projects/together/models/ml_base",
                "--project",
                "proj",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        params = cast(Call, route.calls[0]).request.url.params
        assert params["referenceModel"] == "projects/together/models/ml_base"
        assert "referenceModelId" not in params

    @pytest.mark.respx(base_url=base_url)
    def test_configs_resolves_private_model_name_to_base_model(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/projects/proj/models").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_model_body(baseModel="projects/together/models/ml_base")],
                    "next_cursor": None,
                },
            )
        )
        route = respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [_config_body()], "next_cursor": None})
        )

        result = cli_runner.invoke(["beta", "models", "configs", "my-project/my-model", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        params = cast(Call, route.calls[0]).request.url.params
        assert params["referenceModel"] == "projects/together/models/ml_base"
        assert "referenceModelId" not in params

    @pytest.mark.respx(base_url=base_url)
    def test_configs_resolves_public_model_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get("/supported-models").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_supported_model_body()], "next_cursor": None},
            )
        )
        route = respx_mock.get("/projects/proj/configs").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [_config_body()], "next_cursor": None})
        )

        result = cli_runner.invoke(
            ["beta", "models", "configs", "meta-llama/Llama-3-8B", "--project", "proj", "--json"]
        )

        assert result.exit_code == 0, result.output
        params = cast(Call, route.calls[0]).request.url.params
        assert params["referenceModel"] == "projects/together/models/ml_base"
        assert "referenceModelId" not in params


class TestBetaModelsUpload:
    @pytest.mark.respx(base_url=base_url)
    def test_upload_model_files(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        model_dir = tmp_path / "model"
        model_dir.mkdir()
        weights = model_dir / "weights.bin"
        weights.write_bytes(b"hello world")
        (model_dir / ".hidden").write_bytes(b"ignored")
        (model_dir / "empty.bin").write_bytes(b"")

        # upload forces the client onto the v2 production host
        create_route = respx_mock.post("https://api.together.ai/v2/projects/proj/models/upload/create").mock(
            return_value=httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "path": "weights.bin",
                            "uploadId": "upload-1",
                            "parts": [
                                {
                                    "partNumber": 1,
                                    "url": "https://storage.example/upload-1/part-1",
                                    "headers": {"x-test": "yes"},
                                }
                            ],
                        }
                    ]
                },
            )
        )
        put_route = respx_mock.put("https://storage.example/upload-1/part-1").mock(
            return_value=httpx.Response(200, headers={"ETag": '"etag-1"'})
        )
        complete_route = respx_mock.post("https://api.together.ai/v2/projects/proj/models/upload/complete").mock(
            return_value=httpx.Response(200, json={"revisionId": "rev-1"})
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "upload",
                "ml_1",
                str(model_dir),
                "--project",
                "proj",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == {"revisionId": "rev-1"}
        create_body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert create_body == {
            "objectId": "ml_1",
            "files": [
                {
                    "path": "weights.bin",
                    "hash": hashlib.md5(b"hello world").hexdigest(),
                    "numParts": 1,
                }
            ],
        }
        put_request = cast(Call, put_route.calls[0]).request
        assert put_request.headers["x-test"] == "yes"
        assert put_request.content == b"hello world"
        assert json.loads(cast(Call, complete_route.calls[0]).request.content.decode()) == {
            "objectId": "ml_1",
            "files": [
                {
                    "path": "weights.bin",
                    "hash": hashlib.md5(b"hello world").hexdigest(),
                    "uploadDetails": {
                        "uploadId": "upload-1",
                        "parts": [{"partNumber": 1, "hash": "etag-1"}],
                    },
                }
            ],
        }

    @pytest.mark.respx(base_url=base_url)
    def test_upload_skips_existing_files(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        weights = tmp_path / "weights.bin"
        weights.write_bytes(b"cached")
        create_route = respx_mock.post("https://api.together.ai/v2/projects/proj/models/upload/create").mock(
            return_value=httpx.Response(
                200,
                json={"files": [{"path": "weights.bin", "skipUpload": True}]},
            )
        )
        complete_route = respx_mock.post("https://api.together.ai/v2/projects/proj/models/upload/complete").mock(
            return_value=httpx.Response(200, json={"revisionId": "rev-2"})
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "upload",
                "ml_1",
                str(weights),
                "--project",
                "proj",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == {"revisionId": "rev-2"}
        assert json.loads(cast(Call, create_route.calls[0]).request.content.decode())["objectId"] == "ml_1"
        assert json.loads(cast(Call, complete_route.calls[0]).request.content.decode()) == {
            "objectId": "ml_1",
            "files": [
                {
                    "path": "weights.bin",
                    "hash": hashlib.md5(b"cached").hexdigest(),
                    "skipUpload": True,
                }
            ],
        }


class TestBetaModelsDownload:
    @pytest.mark.respx(base_url=base_url)
    def test_download_writes_files(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        dest = tmp_path / "out"
        dest.mkdir()
        content = b"hello world"

        # download forces the client onto the v2 production host
        respx_mock.post("https://api.together.ai/v2/projects/proj/models/download").mock(
            return_value=httpx.Response(
                200,
                json={
                    "revisionId": "rev-1",
                    "files": [
                        {
                            "path": "weights.bin",
                            "hash": hashlib.md5(content).hexdigest(),
                            "sizeBytes": len(content),
                            "parts": [
                                {
                                    "partNumber": 1,
                                    "sizeBytes": len(content),
                                    "url": "https://storage.example/download/part-1",
                                    "headers": {},
                                }
                            ],
                        }
                    ],
                },
            )
        )
        respx_mock.get("https://storage.example/download/part-1").mock(
            return_value=httpx.Response(200, content=content)
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "download",
                "ml_1",
                str(dest),
                "--project",
                "proj",
                "--revision",
                "rev-1",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["revisionId"] == "rev-1"
        assert payload["files"] == 1
        assert (dest / "weights.bin").read_bytes() == content

    def test_download_rejects_conflicting_revision(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "download",
                "ml_1@rev-a",
                str(tmp_path),
                "--project",
                "proj",
                "--revision",
                "rev-b",
                "--json",
            ]
        )
        assert result.exit_code != 0
        assert "conflicting revisions" in result.output


class TestBetaModelsRemoteUploads:
    @pytest.mark.respx(base_url=base_url)
    def test_create_remote_upload(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/projects/proj/models/uploads").mock(
            return_value=httpx.Response(200, json=_remote_upload_body())
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "remote-uploads",
                "create",
                "ml_1",
                "--project",
                "proj",
                "--from",
                "https://huggingface.co/acme/model",
                "--token",
                "hf_token",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {
            "modelId": "ml_1",
            "remoteUrl": "https://huggingface.co/acme/model",
            "token": "hf_token",
        }
        assert json.loads(result.output)["id"] == "ru_1"

    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_remote_upload(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/projects/proj/models/uploads/ru_1").mock(
            return_value=httpx.Response(200, json=_remote_upload_body())
        )

        result = cli_runner.invoke(["beta", "models", "remote-uploads", "get", "ru_1", "--project", "proj", "--json"])

        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["id"] == "ru_1"

    @pytest.mark.respx(base_url=base_url)
    def test_list_remote_uploads(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.get("/projects/proj/models/uploads").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_remote_upload_body()], "next_cursor": "next"},
            )
        )

        result = cli_runner.invoke(
            [
                "beta",
                "models",
                "remote-uploads",
                "ls",
                "--project",
                "proj",
                "--limit",
                "2",
                "--after",
                "tok",
                "--json",
            ]
        )

        assert result.exit_code == 0, result.output
        url = str(cast(Call, route.calls[0]).request.url)
        assert "limit=2" in url
        assert "after=tok" in url
        assert json.loads(result.output)["next_cursor"] == "next"
