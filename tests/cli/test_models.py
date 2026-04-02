from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from click.testing import CliRunner

from together.lib.cli import main

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"
_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}

_UPLOAD_BODY = {
    "data": {
        "job_id": "job-a15dad11-8d8e-4007-97c5-a211304de284",
        "model_name": "necolinehubner/Qwen2.5-72B-Instruct",
        "model_id": "model-c0e32dfc-637e-47b2-bf4e-e9b2e58c9da7",
        "model_source": "huggingface",
    },
    "message": "Processing model weights. Job created.",
}

list_data = [
    {
        "id": "model/chat",
        "created": 1742764800,
        "object": "model",
        "type": "chat",
        "context_length": 1000,
        "display_name": "Chat Model",
        "license": None,
        "link": None,
        "organization": "org/1",
        "pricing": {"base": None, "finetune": None, "hourly": None, "input": 0.05, "output": 0.10},
    },
    {
        "id": "model/lang",
        "created": 1742764800,
        "object": "model",
        "type": "language",
        "context_length": 1000,
        "display_name": "Language Model",
        "license": None,
        "link": None,
        "organization": "org/1",
        "pricing": {"base": None, "finetune": None, "hourly": None, "input": 0.5, "output": 1.0},
    },
    {
        "id": "model/video",
        "created": 1742764800,
        "object": "model",
        "type": "video",
        "context_length": None,
        "display_name": "Video Model",
        "license": None,
        "link": None,
        "organization": "org/1",
        "pricing": None,
    },
]


class TestModelsList:
    # Test for endpoint create requiring the model
    @pytest.mark.respx(base_url=base_url)
    def test_list(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/models").mock(return_value=httpx.Response(200, json=list_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["models", "list"])
        assert (
            result.output.strip()
            == """
Model        Type        Context length  Price per 1M Tokens (input/output)
-----------  --------  ----------------  ------------------------------------
model/chat   chat                  1000  $0.05/$0.10
model/lang   language              1000  $0.50/$1.00
model/video  video
""".strip()
        )

    # Test for endpoint create requiring the model
    @pytest.mark.respx(base_url=base_url)
    def test_list_dedicated(self, respx_mock: MockRouter) -> None:
        route = respx_mock.get("/models").mock(return_value=httpx.Response(200, json=list_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["models", "list", "--type", "dedicated"])
        assert (
            result.output.strip()
            == """
Model        Type        Context length  Price per 1M Tokens (input/output)
-----------  --------  ----------------  ------------------------------------
model/chat   chat                  1000  $0.05/$0.10
model/lang   language              1000  $0.50/$1.00
model/video  video
""".strip()
        )
        url = str(route.calls[0].request.url)  # type: ignore[arg-type]
        assert "dedicated=true" in url

    # Test for endpoint create requiring the model
    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/models").mock(return_value=httpx.Response(200, json=list_data))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["models", "list", "--json"])
        assert result.output.strip() == json.dumps(list_data, indent=2).strip()


class TestModelsUpload:
    @pytest.mark.respx(base_url=base_url)
    def test_upload(self, respx_mock: MockRouter) -> None:
        route = respx_mock.post("/models").mock(return_value=httpx.Response(200, json=_UPLOAD_BODY))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main, ["models", "upload", "--model-name", "model-123", "--model-source", "s3://model-123"]
        )
        assert (
            result.output.strip()
            == """Model upload job created successfully!
Job ID: job-a15dad11-8d8e-4007-97c5-a211304de284
Model Name: necolinehubner/Qwen2.5-72B-Instruct
Model ID: model-c0e32dfc-637e-47b2-bf4e-e9b2e58c9da7
Model Source: huggingface
Message: Processing model weights. Job created.
""".strip()
        )
        raw = cast(str, route.calls[0].request.content.decode())  # type: ignore[arg-type]
        body = json.loads(raw)
        assert body["model_type"] == "model"

    @pytest.mark.respx(base_url=base_url)
    def test_upload_adapter_sends_model_type(self, respx_mock: MockRouter) -> None:
        post = respx_mock.post("/models").mock(return_value=httpx.Response(200, json=_UPLOAD_BODY))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            [
                "models",
                "upload",
                "--model-name",
                "m",
                "--model-source",
                "s3://x",
                "--model-type",
                "adapter",
                "--base-model",
                "base-m",
            ],
        )
        assert result.exit_code == 0
        raw = cast(str, post.calls[0].request.content.decode())  # type: ignore[arg-type]
        body = json.loads(raw)
        assert body["model_type"] == "adapter"
        assert body["base_model"] == "base-m"

    @pytest.mark.respx(base_url=base_url)
    def test_upload_json(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/models").mock(return_value=httpx.Response(200, json=_UPLOAD_BODY))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            ["models", "upload", "--model-name", "model-123", "--model-source", "s3://model-123", "--json"],
        )
        assert result.exit_code == 0
        out = json.loads(result.output)
        assert out["message"] == _UPLOAD_BODY["message"]


class TestModelsListInvalid:
    def test_list_invalid_type_choice(self) -> None:
        runner = CliRunner(env=_ENV)
        r = runner.invoke(main, ["models", "list", "--type", "serverless"])
        assert r.exit_code == 2
