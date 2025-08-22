# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import ExecuteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCodeInterpreter:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    def test_method_execute(self, client: Together) -> None:
        code_interpreter = client.code_interpreter.execute(
            code="print('Hello, world!')",
            language="python",
        )
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    def test_method_execute_with_all_params(self, client: Together) -> None:
        code_interpreter = client.code_interpreter.execute(
            code="print('Hello, world!')",
            language="python",
            files=[
                {
                    "content": "content",
                    "encoding": "string",
                    "name": "name",
                }
            ],
            session_id="ses_abcDEF123",
        )
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    def test_raw_response_execute(self, client: Together) -> None:
        response = client.code_interpreter.with_raw_response.execute(
            code="print('Hello, world!')",
            language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_interpreter = response.parse()
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    def test_streaming_response_execute(self, client: Together) -> None:
        with client.code_interpreter.with_streaming_response.execute(
            code="print('Hello, world!')",
            language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_interpreter = response.parse()
            assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCodeInterpreter:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    async def test_method_execute(self, async_client: AsyncTogether) -> None:
        code_interpreter = await async_client.code_interpreter.execute(
            code="print('Hello, world!')",
            language="python",
        )
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    async def test_method_execute_with_all_params(self, async_client: AsyncTogether) -> None:
        code_interpreter = await async_client.code_interpreter.execute(
            code="print('Hello, world!')",
            language="python",
            files=[
                {
                    "content": "content",
                    "encoding": "string",
                    "name": "name",
                }
            ],
            session_id="ses_abcDEF123",
        )
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    async def test_raw_response_execute(self, async_client: AsyncTogether) -> None:
        response = await async_client.code_interpreter.with_raw_response.execute(
            code="print('Hello, world!')",
            language="python",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        code_interpreter = await response.parse()
        assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

    @pytest.mark.skip(reason="Prism doesn't support callbacks yet")
    @parametrize
    async def test_streaming_response_execute(self, async_client: AsyncTogether) -> None:
        async with async_client.code_interpreter.with_streaming_response.execute(
            code="print('Hello, world!')",
            language="python",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            code_interpreter = await response.parse()
            assert_matches_type(ExecuteResponse, code_interpreter, path=["response"])

        assert cast(Any, response.is_closed) is True
