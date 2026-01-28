# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.models import UploadStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUploads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_status(self, client: Together) -> None:
        upload = client.models.uploads.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        )
        assert_matches_type(UploadStatusResponse, upload, path=["response"])

    @parametrize
    def test_raw_response_status(self, client: Together) -> None:
        response = client.models.uploads.with_raw_response.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(UploadStatusResponse, upload, path=["response"])

    @parametrize
    def test_streaming_response_status(self, client: Together) -> None:
        with client.models.uploads.with_streaming_response.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(UploadStatusResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_status(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.models.uploads.with_raw_response.status(
                "",
            )


class TestAsyncUploads:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_status(self, async_client: AsyncTogether) -> None:
        upload = await async_client.models.uploads.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        )
        assert_matches_type(UploadStatusResponse, upload, path=["response"])

    @parametrize
    async def test_raw_response_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.models.uploads.with_raw_response.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(UploadStatusResponse, upload, path=["response"])

    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncTogether) -> None:
        async with async_client.models.uploads.with_streaming_response.status(
            "job-a15dad11-8d8e-4007-97c5-a211304de284",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(UploadStatusResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_status(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.models.uploads.with_raw_response.status(
                "",
            )
