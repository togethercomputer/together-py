# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import (
    Checkpoint,
    CheckpointsListResponse,
    CheckpointDownloadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCheckpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        checkpoint = client.beta.rl.checkpoints.retrieve(
            "id",
        )
        assert_matches_type(Checkpoint, checkpoint, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.rl.checkpoints.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = response.parse()
        assert_matches_type(Checkpoint, checkpoint, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.rl.checkpoints.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = response.parse()
            assert_matches_type(Checkpoint, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.rl.checkpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        checkpoint = client.beta.rl.checkpoints.list()
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        checkpoint = client.beta.rl.checkpoints.list(
            after="after",
            base_model="base_model",
            limit=0,
            session_id="session_id",
        )
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.rl.checkpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = response.parse()
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.rl.checkpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = response.parse()
            assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_download(self, client: Together) -> None:
        checkpoint = client.beta.rl.checkpoints.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        )
        assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

    @parametrize
    def test_raw_response_download(self, client: Together) -> None:
        response = client.beta.rl.checkpoints.with_raw_response.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = response.parse()
        assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

    @parametrize
    def test_streaming_response_download(self, client: Together) -> None:
        with client.beta.rl.checkpoints.with_streaming_response.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = response.parse()
            assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_download(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.rl.checkpoints.with_raw_response.download(
                id="",
                variant="CHECKPOINT_VARIANT_UNSPECIFIED",
            )


class TestAsyncCheckpoints:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        checkpoint = await async_client.beta.rl.checkpoints.retrieve(
            "id",
        )
        assert_matches_type(Checkpoint, checkpoint, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.checkpoints.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = await response.parse()
        assert_matches_type(Checkpoint, checkpoint, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.checkpoints.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = await response.parse()
            assert_matches_type(Checkpoint, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.rl.checkpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        checkpoint = await async_client.beta.rl.checkpoints.list()
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        checkpoint = await async_client.beta.rl.checkpoints.list(
            after="after",
            base_model="base_model",
            limit=0,
            session_id="session_id",
        )
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.checkpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = await response.parse()
        assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.checkpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = await response.parse()
            assert_matches_type(CheckpointsListResponse, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_download(self, async_client: AsyncTogether) -> None:
        checkpoint = await async_client.beta.rl.checkpoints.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        )
        assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

    @parametrize
    async def test_raw_response_download(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.checkpoints.with_raw_response.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = await response.parse()
        assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.checkpoints.with_streaming_response.download(
            id="id",
            variant="CHECKPOINT_VARIANT_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = await response.parse()
            assert_matches_type(CheckpointDownloadResponse, checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_download(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.rl.checkpoints.with_raw_response.download(
                id="",
                variant="CHECKPOINT_VARIANT_UNSPECIFIED",
            )
