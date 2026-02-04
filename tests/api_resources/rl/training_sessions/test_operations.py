# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve_forward_backward(self, client: Together) -> None:
        operation = client.rl.training_sessions.operations.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert operation is None

    @parametrize
    def test_raw_response_retrieve_forward_backward(self, client: Together) -> None:
        response = client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert operation is None

    @parametrize
    def test_streaming_response_retrieve_forward_backward(self, client: Together) -> None:
        with client.rl.training_sessions.operations.with_streaming_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert operation is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_optim_step(self, client: Together) -> None:
        operation = client.rl.training_sessions.operations.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert operation is None

    @parametrize
    def test_raw_response_retrieve_optim_step(self, client: Together) -> None:
        response = client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert operation is None

    @parametrize
    def test_streaming_response_retrieve_optim_step(self, client: Together) -> None:
        with client.rl.training_sessions.operations.with_streaming_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert operation is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_optim_step(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
                operation_id="",
                session_id="session_id",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.rl.training_sessions.operations.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert operation is None

    @parametrize
    async def test_raw_response_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert operation is None

    @parametrize
    async def test_streaming_response_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.operations.with_streaming_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert operation is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.rl.training_sessions.operations.with_raw_response.retrieve_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        operation = await async_client.rl.training_sessions.operations.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert operation is None

    @parametrize
    async def test_raw_response_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert operation is None

    @parametrize
    async def test_streaming_response_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.operations.with_streaming_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert operation is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.rl.training_sessions.operations.with_raw_response.retrieve_optim_step(
                operation_id="",
                session_id="session_id",
            )
