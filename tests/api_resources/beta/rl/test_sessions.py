# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import (
    Session,
    SessionsListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        session = client.beta.rl.sessions.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        session = client.beta.rl.sessions.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
            display_name="gsm8k-experiment-2",
            load_optimizer=True,
            lora_config={
                "alpha": 64,
                "dropout": 0,
                "rank": 32,
                "seed": "59",
                "train_unembed": True,
            },
            metadata={
                "wandb": {
                    "entity": "example-org",
                    "group": "gsm8k-35b-sweep",
                    "project": "grpo-gsm8k",
                    "run_id": "abc123",
                    "run_name": "exp2-thinking-4k-ctx",
                    "url": "https://wandb.ai/example-org/example-project/runs/run-id",
                }
            },
            resume_from_checkpoint_id="123e4567-e89b-12d3-a456-426614174000",
            resume_from_hf_checkpoint="your-org/llama-3-8b-finetuned",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.rl.sessions.with_raw_response.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.rl.sessions.with_streaming_response.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        session = client.beta.rl.sessions.retrieve(
            "session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.rl.sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.rl.sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        session = client.beta.rl.sessions.update(
            session_id="session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        session = client.beta.rl.sessions.update(
            session_id="session_id",
            display_name="display_name",
            metadata={
                "wandb": {
                    "entity": "example-org",
                    "group": "gsm8k-35b-sweep",
                    "project": "grpo-gsm8k",
                    "run_id": "abc123",
                    "run_name": "exp2-thinking-4k-ctx",
                    "url": "https://wandb.ai/example-org/example-project/runs/run-id",
                }
            },
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.rl.sessions.with_raw_response.update(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.rl.sessions.with_streaming_response.update(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.sessions.with_raw_response.update(
                session_id="",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        session = client.beta.rl.sessions.list()
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        session = client.beta.rl.sessions.list(
            after="after",
            created_by="created_by",
            limit=0,
            model_resources_id="model_resources_id",
            status=["TRAINING_SESSION_STATUS_CREATING"],
        )
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.rl.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.rl.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionsListResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_stop(self, client: Together) -> None:
        session = client.beta.rl.sessions.stop(
            "session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_raw_response_stop(self, client: Together) -> None:
        response = client.beta.rl.sessions.with_raw_response.stop(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    def test_streaming_response_stop(self, client: Together) -> None:
        with client.beta.rl.sessions.with_streaming_response.stop(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_stop(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.sessions.with_raw_response.stop(
                "",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
            display_name="gsm8k-experiment-2",
            load_optimizer=True,
            lora_config={
                "alpha": 64,
                "dropout": 0,
                "rank": 32,
                "seed": "59",
                "train_unembed": True,
            },
            metadata={
                "wandb": {
                    "entity": "example-org",
                    "group": "gsm8k-35b-sweep",
                    "project": "grpo-gsm8k",
                    "run_id": "abc123",
                    "run_name": "exp2-thinking-4k-ctx",
                    "url": "https://wandb.ai/example-org/example-project/runs/run-id",
                }
            },
            resume_from_checkpoint_id="123e4567-e89b-12d3-a456-426614174000",
            resume_from_hf_checkpoint="your-org/llama-3-8b-finetuned",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.sessions.with_raw_response.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.sessions.with_streaming_response.create(
            model_resources_id="123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.retrieve(
            "session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.update(
            session_id="session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.update(
            session_id="session_id",
            display_name="display_name",
            metadata={
                "wandb": {
                    "entity": "example-org",
                    "group": "gsm8k-35b-sweep",
                    "project": "grpo-gsm8k",
                    "run_id": "abc123",
                    "run_name": "exp2-thinking-4k-ctx",
                    "url": "https://wandb.ai/example-org/example-project/runs/run-id",
                }
            },
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.sessions.with_raw_response.update(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.sessions.with_streaming_response.update(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.sessions.with_raw_response.update(
                session_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.list()
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.list(
            after="after",
            created_by="created_by",
            limit=0,
            model_resources_id="model_resources_id",
            status=["TRAINING_SESSION_STATUS_CREATING"],
        )
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionsListResponse, session, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionsListResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_stop(self, async_client: AsyncTogether) -> None:
        session = await async_client.beta.rl.sessions.stop(
            "session_id",
        )
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_raw_response_stop(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.sessions.with_raw_response.stop(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @parametrize
    async def test_streaming_response_stop(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.sessions.with_streaming_response.stop(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_stop(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.sessions.with_raw_response.stop(
                "",
            )
