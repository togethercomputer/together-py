# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.organization import BillingUsageWindow

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCosts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Together) -> None:
        cost = client.organization.usage.costs.list()
        assert_matches_type(SyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        cost = client.organization.usage.costs.list(
            after="after",
            granularity="day",
            limit=1,
            month="7321-06",
            organization_id="x",
        )
        assert_matches_type(SyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.organization.usage.costs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cost = response.parse()
        assert_matches_type(SyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.organization.usage.costs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cost = response.parse()
            assert_matches_type(SyncCursorPagination[BillingUsageWindow], cost, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCosts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        cost = await async_client.organization.usage.costs.list()
        assert_matches_type(AsyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        cost = await async_client.organization.usage.costs.list(
            after="after",
            granularity="day",
            limit=1,
            month="7321-06",
            organization_id="x",
        )
        assert_matches_type(AsyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.organization.usage.costs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cost = await response.parse()
        assert_matches_type(AsyncCursorPagination[BillingUsageWindow], cost, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.organization.usage.costs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cost = await response.parse()
            assert_matches_type(AsyncCursorPagination[BillingUsageWindow], cost, path=["response"])

        assert cast(Any, response.is_closed) is True
