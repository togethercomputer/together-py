# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrainingSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        training_session = client.rl.training_sessions.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        )
        assert training_session is None

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        training_session = client.rl.training_sessions.create(
            body={
                "base_model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "checkpoint_id": "checkpoint-123",
                "lora_config": {
                    "alpha": 0,
                    "dropout": 0,
                    "rank": 0,
                },
                "lr_scheduler_config": {
                    "linear": {
                        "params": {
                            "lr_min": 0,
                            "warmup_steps": 0,
                        }
                    }
                },
                "optimizer_config": {
                    "adamw": {
                        "params": {
                            "beta1": 0,
                            "beta2": 0,
                            "eps": 0,
                            "lr": 0,
                            "weight_decay": 0,
                        }
                    },
                    "max_grad_norm": 0,
                },
            },
        )
        assert training_session is None

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        training_session = client.rl.training_sessions.retrieve(
            "session_id",
        )
        assert training_session is None

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        training_session = client.rl.training_sessions.list()
        assert training_session is None

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        training_session = client.rl.training_sessions.list(
            limit="limit",
            offset="offset",
            status="status",
        )
        assert training_session is None

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_forward_backward(self, client: Together) -> None:
        training_session = client.rl.training_sessions.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        )
        assert training_session is None

    @parametrize
    def test_raw_response_forward_backward(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_forward_backward(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.with_raw_response.forward_backward(
                session_id="",
                body={
                    "loss_fn": "LOSS_FN_GRPO",
                    "samples": [
                        {
                            "loss_fn_inputs": {
                                "target_tokens": {"data": [123, 456, 789]},
                                "weights": {"data": [0.1, 0.2, 0.3]},
                            },
                            "model_input": {"chunks": [{}]},
                        }
                    ],
                },
            )

    @parametrize
    def test_method_optim_step(self, client: Together) -> None:
        training_session = client.rl.training_sessions.optim_step(
            session_id="session_id",
            body={},
        )
        assert training_session is None

    @parametrize
    def test_raw_response_optim_step(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.optim_step(
            session_id="session_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_optim_step(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.optim_step(
            session_id="session_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_optim_step(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.with_raw_response.optim_step(
                session_id="",
                body={},
            )

    @parametrize
    def test_method_stop(self, client: Together) -> None:
        training_session = client.rl.training_sessions.stop(
            "session_id",
        )
        assert training_session is None

    @parametrize
    def test_raw_response_stop(self, client: Together) -> None:
        response = client.rl.training_sessions.with_raw_response.stop(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = response.parse()
        assert training_session is None

    @parametrize
    def test_streaming_response_stop(self, client: Together) -> None:
        with client.rl.training_sessions.with_streaming_response.stop(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_stop(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.rl.training_sessions.with_raw_response.stop(
                "",
            )


class TestAsyncTrainingSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        )
        assert training_session is None

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.create(
            body={
                "base_model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "checkpoint_id": "checkpoint-123",
                "lora_config": {
                    "alpha": 0,
                    "dropout": 0,
                    "rank": 0,
                },
                "lr_scheduler_config": {
                    "linear": {
                        "params": {
                            "lr_min": 0,
                            "warmup_steps": 0,
                        }
                    }
                },
                "optimizer_config": {
                    "adamw": {
                        "params": {
                            "beta1": 0,
                            "beta2": 0,
                            "eps": 0,
                            "lr": 0,
                            "weight_decay": 0,
                        }
                    },
                    "max_grad_norm": 0,
                },
            },
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.create(
            body={"base_model": "meta-llama/Meta-Llama-3-8B-Instruct"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.retrieve(
            "session_id",
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.list()
        assert training_session is None

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.list(
            limit="limit",
            offset="offset",
            status="status",
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_forward_backward(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.forward_backward(
            session_id="session_id",
            body={
                "loss_fn": "LOSS_FN_GRPO",
                "samples": [
                    {
                        "loss_fn_inputs": {
                            "target_tokens": {"data": [123, 456, 789]},
                            "weights": {"data": [0.1, 0.2, 0.3]},
                        },
                        "model_input": {"chunks": [{}]},
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.with_raw_response.forward_backward(
                session_id="",
                body={
                    "loss_fn": "LOSS_FN_GRPO",
                    "samples": [
                        {
                            "loss_fn_inputs": {
                                "target_tokens": {"data": [123, 456, 789]},
                                "weights": {"data": [0.1, 0.2, 0.3]},
                            },
                            "model_input": {"chunks": [{}]},
                        }
                    ],
                },
            )

    @parametrize
    async def test_method_optim_step(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.optim_step(
            session_id="session_id",
            body={},
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_optim_step(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.optim_step(
            session_id="session_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_optim_step(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.optim_step(
            session_id="session_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_optim_step(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.with_raw_response.optim_step(
                session_id="",
                body={},
            )

    @parametrize
    async def test_method_stop(self, async_client: AsyncTogether) -> None:
        training_session = await async_client.rl.training_sessions.stop(
            "session_id",
        )
        assert training_session is None

    @parametrize
    async def test_raw_response_stop(self, async_client: AsyncTogether) -> None:
        response = await async_client.rl.training_sessions.with_raw_response.stop(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        training_session = await response.parse()
        assert training_session is None

    @parametrize
    async def test_streaming_response_stop(self, async_client: AsyncTogether) -> None:
        async with async_client.rl.training_sessions.with_streaming_response.stop(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            training_session = await response.parse()
            assert training_session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_stop(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.rl.training_sessions.with_raw_response.stop(
                "",
            )
