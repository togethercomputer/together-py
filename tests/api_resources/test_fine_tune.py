# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    FineTune,
    FineTuneEvent,
    FineTuneListResponse,
    FineTuneDownloadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFineTune:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        fine_tune = client.fine_tune.create(
            model="model",
            training_file="training_file",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        fine_tune = client.fine_tune.create(
            model="model",
            training_file="training_file",
            batch_size=0,
            learning_rate=0,
            lora=True,
            lora_alpha=0,
            lora_dropout=0,
            lora_r=0,
            lora_trainable_modules="lora_trainable_modules",
            n_checkpoints=0,
            n_epochs=0,
            n_evals=0,
            suffix="suffix",
            validation_file="validation_file",
            wandb_api_key="wandb_api_key",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.create(
            model="model",
            training_file="training_file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.create(
            model="model",
            training_file="training_file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        fine_tune = client.fine_tune.retrieve(
            "id",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tune.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        fine_tune = client.fine_tune.list()
        assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        fine_tune = client.fine_tune.cancel(
            "id",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.cancel(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.cancel(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tune.with_raw_response.cancel(
                "",
            )

    @parametrize
    def test_method_download(self, client: Together) -> None:
        fine_tune = client.fine_tune.download(
            ft_id="ft_id",
        )
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    def test_method_download_with_all_params(self, client: Together) -> None:
        fine_tune = client.fine_tune.download(
            ft_id="ft_id",
            checkpoint_step=0,
            output="output",
        )
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_download(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.download(
            ft_id="ft_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_download(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.download(
            ft_id="ft_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_events(self, client: Together) -> None:
        fine_tune = client.fine_tune.list_events(
            "id",
        )
        assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_list_events(self, client: Together) -> None:
        response = client.fine_tune.with_raw_response.list_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

    @parametrize
    def test_streaming_response_list_events(self, client: Together) -> None:
        with client.fine_tune.with_streaming_response.list_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = response.parse()
            assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_events(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tune.with_raw_response.list_events(
                "",
            )


class TestAsyncFineTune:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.create(
            model="model",
            training_file="training_file",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.create(
            model="model",
            training_file="training_file",
            batch_size=0,
            learning_rate=0,
            lora=True,
            lora_alpha=0,
            lora_dropout=0,
            lora_r=0,
            lora_trainable_modules="lora_trainable_modules",
            n_checkpoints=0,
            n_epochs=0,
            n_evals=0,
            suffix="suffix",
            validation_file="validation_file",
            wandb_api_key="wandb_api_key",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.create(
            model="model",
            training_file="training_file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.create(
            model="model",
            training_file="training_file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.retrieve(
            "id",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tune.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.list()
        assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTuneListResponse, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.cancel(
            "id",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.cancel(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.cancel(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTune, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tune.with_raw_response.cancel(
                "",
            )

    @parametrize
    async def test_method_download(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.download(
            ft_id="ft_id",
        )
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    async def test_method_download_with_all_params(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.download(
            ft_id="ft_id",
            checkpoint_step=0,
            output="output",
        )
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_download(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.download(
            ft_id="ft_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.download(
            ft_id="ft_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTuneDownloadResponse, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_events(self, async_client: AsyncTogether) -> None:
        fine_tune = await async_client.fine_tune.list_events(
            "id",
        )
        assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tune.with_raw_response.list_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = await response.parse()
        assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tune.with_streaming_response.list_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune = await response.parse()
            assert_matches_type(FineTuneEvent, fine_tune, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tune.with_raw_response.list_events(
                "",
            )
