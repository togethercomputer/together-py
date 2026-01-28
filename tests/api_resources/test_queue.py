# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    QueueCancelResponse,
    QueueSubmitResponse,
    QueueGetStatusResponse,
    QueueGetMetricsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQueue:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        queue = client.queue.cancel(
            model="model",
            request_id="request_id",
        )
        assert_matches_type(QueueCancelResponse, queue, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.queue.with_raw_response.cancel(
            model="model",
            request_id="request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = response.parse()
        assert_matches_type(QueueCancelResponse, queue, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.queue.with_streaming_response.cancel(
            model="model",
            request_id="request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = response.parse()
            assert_matches_type(QueueCancelResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_metrics(self, client: Together) -> None:
        queue = client.queue.get_metrics(
            model="model",
        )
        assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

    @parametrize
    def test_raw_response_get_metrics(self, client: Together) -> None:
        response = client.queue.with_raw_response.get_metrics(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = response.parse()
        assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

    @parametrize
    def test_streaming_response_get_metrics(self, client: Together) -> None:
        with client.queue.with_streaming_response.get_metrics(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = response.parse()
            assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Together) -> None:
        queue = client.queue.get_status(
            model="model",
            request_id="request_id",
        )
        assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Together) -> None:
        response = client.queue.with_raw_response.get_status(
            model="model",
            request_id="request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = response.parse()
        assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Together) -> None:
        with client.queue.with_streaming_response.get_status(
            model="model",
            request_id="request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = response.parse()
            assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_submit(self, client: Together) -> None:
        queue = client.queue.submit(
            model="model",
            payload={"foo": "bar"},
        )
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    def test_method_submit_with_all_params(self, client: Together) -> None:
        queue = client.queue.submit(
            model="model",
            payload={"foo": "bar"},
            info={"foo": "bar"},
            priority=0,
        )
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    def test_raw_response_submit(self, client: Together) -> None:
        response = client.queue.with_raw_response.submit(
            model="model",
            payload={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = response.parse()
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    def test_streaming_response_submit(self, client: Together) -> None:
        with client.queue.with_streaming_response.submit(
            model="model",
            payload={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = response.parse()
            assert_matches_type(QueueSubmitResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncQueue:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        queue = await async_client.queue.cancel(
            model="model",
            request_id="request_id",
        )
        assert_matches_type(QueueCancelResponse, queue, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.queue.with_raw_response.cancel(
            model="model",
            request_id="request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = await response.parse()
        assert_matches_type(QueueCancelResponse, queue, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.queue.with_streaming_response.cancel(
            model="model",
            request_id="request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = await response.parse()
            assert_matches_type(QueueCancelResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_metrics(self, async_client: AsyncTogether) -> None:
        queue = await async_client.queue.get_metrics(
            model="model",
        )
        assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

    @parametrize
    async def test_raw_response_get_metrics(self, async_client: AsyncTogether) -> None:
        response = await async_client.queue.with_raw_response.get_metrics(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = await response.parse()
        assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

    @parametrize
    async def test_streaming_response_get_metrics(self, async_client: AsyncTogether) -> None:
        async with async_client.queue.with_streaming_response.get_metrics(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = await response.parse()
            assert_matches_type(QueueGetMetricsResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncTogether) -> None:
        queue = await async_client.queue.get_status(
            model="model",
            request_id="request_id",
        )
        assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.queue.with_raw_response.get_status(
            model="model",
            request_id="request_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = await response.parse()
        assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncTogether) -> None:
        async with async_client.queue.with_streaming_response.get_status(
            model="model",
            request_id="request_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = await response.parse()
            assert_matches_type(QueueGetStatusResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_submit(self, async_client: AsyncTogether) -> None:
        queue = await async_client.queue.submit(
            model="model",
            payload={"foo": "bar"},
        )
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncTogether) -> None:
        queue = await async_client.queue.submit(
            model="model",
            payload={"foo": "bar"},
            info={"foo": "bar"},
            priority=0,
        )
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncTogether) -> None:
        response = await async_client.queue.with_raw_response.submit(
            model="model",
            payload={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        queue = await response.parse()
        assert_matches_type(QueueSubmitResponse, queue, path=["response"])

    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncTogether) -> None:
        async with async_client.queue.with_streaming_response.submit(
            model="model",
            payload={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            queue = await response.parse()
            assert_matches_type(QueueSubmitResponse, queue, path=["response"])

        assert cast(Any, response.is_closed) is True
