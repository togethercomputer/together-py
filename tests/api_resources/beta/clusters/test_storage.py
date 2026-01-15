# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.clusters import (
    ClusterStorage,
    StorageListResponse,
    StorageDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorage:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        storage = client.beta.clusters.storage.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.clusters.storage.with_raw_response.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.clusters.storage.with_streaming_response.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        storage = client.beta.clusters.storage.retrieve(
            "volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.clusters.storage.with_raw_response.retrieve(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.clusters.storage.with_streaming_response.retrieve(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            client.beta.clusters.storage.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        storage = client.beta.clusters.storage.update()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        storage = client.beta.clusters.storage.update(
            size_tib=0,
            volume_id="volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.clusters.storage.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.clusters.storage.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Together) -> None:
        storage = client.beta.clusters.storage.list()
        assert_matches_type(StorageListResponse, storage, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.clusters.storage.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageListResponse, storage, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.clusters.storage.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageListResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        storage = client.beta.clusters.storage.delete(
            "volume_id",
        )
        assert_matches_type(StorageDeleteResponse, storage, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.clusters.storage.with_raw_response.delete(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageDeleteResponse, storage, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.clusters.storage.with_streaming_response.delete(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageDeleteResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            client.beta.clusters.storage.with_raw_response.delete(
                "",
            )


class TestAsyncStorage:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.storage.with_raw_response.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.storage.with_streaming_response.create(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.retrieve(
            "volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.storage.with_raw_response.retrieve(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.storage.with_streaming_response.retrieve(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            await async_client.beta.clusters.storage.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.update()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.update(
            size_tib=0,
            volume_id="volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.storage.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.storage.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.list()
        assert_matches_type(StorageListResponse, storage, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.storage.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageListResponse, storage, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.storage.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageListResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        storage = await async_client.beta.clusters.storage.delete(
            "volume_id",
        )
        assert_matches_type(StorageDeleteResponse, storage, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.storage.with_raw_response.delete(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageDeleteResponse, storage, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.storage.with_streaming_response.delete(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageDeleteResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            await async_client.beta.clusters.storage.with_raw_response.delete(
                "",
            )
