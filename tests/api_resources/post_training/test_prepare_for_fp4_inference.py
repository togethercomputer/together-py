# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.post_training import (
    QuantizationJob,
    QuantizationEstimate,
    PrepareForFp4InferenceListResponse,
    PrepareForFp4InferenceListEventsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPrepareForFp4Inference:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.create(
            inputs={
                "adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R",
                "adapter_revision_id": "rv_CeG3faPBj2ABwbAaHPTmx",
                "calibration_file_id": "file-5f1b0c7a-2d19-4a3e-9c60-8ab41c2f7d35",
            },
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.retrieve(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.retrieve(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.retrieve(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.post_training.prepare_for_fp4_inference.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.list()
        assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.cancel(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.cancel(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.cancel(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.post_training.prepare_for_fp4_inference.with_raw_response.cancel(
                "",
            )

    @parametrize
    def test_method_estimate_cost(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_method_estimate_cost_with_all_params(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.estimate_cost(
            inputs={
                "adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R",
                "adapter_revision_id": "rv_CeG3faPBj2ABwbAaHPTmx",
                "calibration_file_id": "file-5f1b0c7a-2d19-4a3e-9c60-8ab41c2f7d35",
            },
        )
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_estimate_cost(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_estimate_cost(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_events(self, client: Together) -> None:
        prepare_for_fp4_inference = client.post_training.prepare_for_fp4_inference.list_events(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_raw_response_list_events(self, client: Together) -> None:
        response = client.post_training.prepare_for_fp4_inference.with_raw_response.list_events(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = response.parse()
        assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    def test_streaming_response_list_events(self, client: Together) -> None:
        with client.post_training.prepare_for_fp4_inference.with_streaming_response.list_events(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = response.parse()
            assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_events(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.post_training.prepare_for_fp4_inference.with_raw_response.list_events(
                "",
            )


class TestAsyncPrepareForFp4Inference:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.create(
            inputs={
                "adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R",
                "adapter_revision_id": "rv_CeG3faPBj2ABwbAaHPTmx",
                "calibration_file_id": "file-5f1b0c7a-2d19-4a3e-9c60-8ab41c2f7d35",
            },
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.create(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.retrieve(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.retrieve(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.retrieve(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.post_training.prepare_for_fp4_inference.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.list()
        assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(PrepareForFp4InferenceListResponse, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.cancel(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.cancel(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.cancel(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(QuantizationJob, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.post_training.prepare_for_fp4_inference.with_raw_response.cancel(
                "",
            )

    @parametrize
    async def test_method_estimate_cost(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_method_estimate_cost_with_all_params(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.estimate_cost(
            inputs={
                "adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R",
                "adapter_revision_id": "rv_CeG3faPBj2ABwbAaHPTmx",
                "calibration_file_id": "file-5f1b0c7a-2d19-4a3e-9c60-8ab41c2f7d35",
            },
        )
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_estimate_cost(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_estimate_cost(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.estimate_cost(
            inputs={"adapter_object_id": "ml_CeG3fF6pyEViU8dE8pk7R"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(QuantizationEstimate, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_events(self, async_client: AsyncTogether) -> None:
        prepare_for_fp4_inference = await async_client.post_training.prepare_for_fp4_inference.list_events(
            "shp-quant-ea9-0-b1--5f",
        )
        assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.prepare_for_fp4_inference.with_raw_response.list_events(
            "shp-quant-ea9-0-b1--5f",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prepare_for_fp4_inference = await response.parse()
        assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.prepare_for_fp4_inference.with_streaming_response.list_events(
            "shp-quant-ea9-0-b1--5f",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prepare_for_fp4_inference = await response.parse()
            assert_matches_type(PrepareForFp4InferenceListEventsResponse, prepare_for_fp4_inference, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.post_training.prepare_for_fp4_inference.with_raw_response.list_events(
                "",
            )
