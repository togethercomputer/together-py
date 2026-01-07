# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.endpoints import (
    StorageListSharedVolumesResponse,
    StorageCreateSharedVolumeResponse,
    StorageDeleteSharedVolumeResponse,
)
from together.types.beta.clusters import ClusterStorage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_shared_volume(self, client: Together) -> None:
        storage = client.endpoints.storages.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )
        assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

    @parametrize
    def test_raw_response_create_shared_volume(self, client: Together) -> None:
        response = client.endpoints.storages.with_raw_response.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

    @parametrize
    def test_streaming_response_create_shared_volume(self, client: Together) -> None:
        with client.endpoints.storages.with_streaming_response.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete_shared_volume(self, client: Together) -> None:
        storage = client.endpoints.storages.delete_shared_volume(
            "volume_id",
        )
        assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

    @parametrize
    def test_raw_response_delete_shared_volume(self, client: Together) -> None:
        response = client.endpoints.storages.with_raw_response.delete_shared_volume(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

    @parametrize
    def test_streaming_response_delete_shared_volume(self, client: Together) -> None:
        with client.endpoints.storages.with_streaming_response.delete_shared_volume(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete_shared_volume(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            client.endpoints.storages.with_raw_response.delete_shared_volume(
                "",
            )

    @parametrize
    def test_method_list_shared_volumes(self, client: Together) -> None:
        storage = client.endpoints.storages.list_shared_volumes()
        assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

    @parametrize
    def test_raw_response_list_shared_volumes(self, client: Together) -> None:
        response = client.endpoints.storages.with_raw_response.list_shared_volumes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

    @parametrize
    def test_streaming_response_list_shared_volumes(self, client: Together) -> None:
        with client.endpoints.storages.with_streaming_response.list_shared_volumes() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve_shared_volume(self, client: Together) -> None:
        storage = client.endpoints.storages.retrieve_shared_volume(
            "volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_raw_response_retrieve_shared_volume(self, client: Together) -> None:
        response = client.endpoints.storages.with_raw_response.retrieve_shared_volume(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_shared_volume(self, client: Together) -> None:
        with client.endpoints.storages.with_streaming_response.retrieve_shared_volume(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_shared_volume(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            client.endpoints.storages.with_raw_response.retrieve_shared_volume(
                "",
            )

    @parametrize
    def test_method_update_shared_volume(self, client: Together) -> None:
        storage = client.endpoints.storages.update_shared_volume()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_method_update_shared_volume_with_all_params(self, client: Together) -> None:
        storage = client.endpoints.storages.update_shared_volume(
            size_tib=0,
            volume_id="volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_raw_response_update_shared_volume(self, client: Together) -> None:
        response = client.endpoints.storages.with_raw_response.update_shared_volume()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    def test_streaming_response_update_shared_volume(self, client: Together) -> None:
        with client.endpoints.storages.with_streaming_response.update_shared_volume() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_shared_volume(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )
        assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

    @parametrize
    async def test_raw_response_create_shared_volume(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.storages.with_raw_response.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

    @parametrize
    async def test_streaming_response_create_shared_volume(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.storages.with_streaming_response.create_shared_volume(
            region="region",
            size_tib=0,
            volume_name="volume_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageCreateSharedVolumeResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete_shared_volume(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.delete_shared_volume(
            "volume_id",
        )
        assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

    @parametrize
    async def test_raw_response_delete_shared_volume(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.storages.with_raw_response.delete_shared_volume(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

    @parametrize
    async def test_streaming_response_delete_shared_volume(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.storages.with_streaming_response.delete_shared_volume(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageDeleteSharedVolumeResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete_shared_volume(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            await async_client.endpoints.storages.with_raw_response.delete_shared_volume(
                "",
            )

    @parametrize
    async def test_method_list_shared_volumes(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.list_shared_volumes()
        assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

    @parametrize
    async def test_raw_response_list_shared_volumes(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.storages.with_raw_response.list_shared_volumes()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

    @parametrize
    async def test_streaming_response_list_shared_volumes(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.storages.with_streaming_response.list_shared_volumes() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(StorageListSharedVolumesResponse, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve_shared_volume(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.retrieve_shared_volume(
            "volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_shared_volume(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.storages.with_raw_response.retrieve_shared_volume(
            "volume_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_shared_volume(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.storages.with_streaming_response.retrieve_shared_volume(
            "volume_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_shared_volume(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `volume_id` but received ''"):
            await async_client.endpoints.storages.with_raw_response.retrieve_shared_volume(
                "",
            )

    @parametrize
    async def test_method_update_shared_volume(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.update_shared_volume()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_method_update_shared_volume_with_all_params(self, async_client: AsyncTogether) -> None:
        storage = await async_client.endpoints.storages.update_shared_volume(
            size_tib=0,
            volume_id="volume_id",
        )
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_raw_response_update_shared_volume(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.storages.with_raw_response.update_shared_volume()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage = await response.parse()
        assert_matches_type(ClusterStorage, storage, path=["response"])

    @parametrize
    async def test_streaming_response_update_shared_volume(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.storages.with_streaming_response.update_shared_volume() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage = await response.parse()
            assert_matches_type(ClusterStorage, storage, path=["response"])

        assert cast(Any, response.is_closed) is True
