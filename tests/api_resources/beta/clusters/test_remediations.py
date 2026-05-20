# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.clusters import (
    Remediation,
    RemediationListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRemediations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
            remediation_id="remediation_id",
            reason="reason",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.create(
                instance_id="instance_id",
                cluster_id="",
                mode="REMEDIATION_MODE_VM_ONLY",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.create(
                instance_id="",
                cluster_id="cluster_id",
                mode="REMEDIATION_MODE_VM_ONLY",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        )
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode=["REMEDIATION_MODE_VM_ONLY"],
            order_by="order_by",
            page_size=0,
            page_token="page_token",
            state=["PENDING_APPROVAL"],
            trigger=["REMEDIATION_TRIGGER_MANUAL"],
        )
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(RemediationListResponse, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.list(
                instance_id="instance_id",
                cluster_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.list(
                instance_id="",
                cluster_id="cluster_id",
            )

    @parametrize
    def test_method_approve(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_method_approve_with_all_params(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
            comment="comment",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_raw_response_approve(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_streaming_response_approve(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_approve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    def test_method_reject(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_method_reject_with_all_params(self, client: Together) -> None:
        remediation = client.beta.clusters.remediations.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
            comment="comment",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_raw_response_reject(self, client: Together) -> None:
        response = client.beta.clusters.remediations.with_raw_response.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    def test_streaming_response_reject(self, client: Together) -> None:
        with client.beta.clusters.remediations.with_streaming_response.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_reject(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )


class TestAsyncRemediations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
            remediation_id="remediation_id",
            reason="reason",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.create(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode="REMEDIATION_MODE_VM_ONLY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.create(
                instance_id="instance_id",
                cluster_id="",
                mode="REMEDIATION_MODE_VM_ONLY",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.create(
                instance_id="",
                cluster_id="cluster_id",
                mode="REMEDIATION_MODE_VM_ONLY",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.retrieve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.retrieve(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        )
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
            mode=["REMEDIATION_MODE_VM_ONLY"],
            order_by="order_by",
            page_size=0,
            page_token="page_token",
            state=["PENDING_APPROVAL"],
            trigger=["REMEDIATION_TRIGGER_MANUAL"],
        )
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(RemediationListResponse, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.list(
            instance_id="instance_id",
            cluster_id="cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(RemediationListResponse, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.list(
                instance_id="instance_id",
                cluster_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.list(
                instance_id="",
                cluster_id="cluster_id",
            )

    @parametrize
    async def test_method_approve(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_method_approve_with_all_params(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
            comment="comment",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_raw_response_approve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_approve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.approve(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_approve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.approve(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.cancel(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.cancel(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )

    @parametrize
    async def test_method_reject(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_method_reject_with_all_params(self, async_client: AsyncTogether) -> None:
        remediation = await async_client.beta.clusters.remediations.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
            comment="comment",
        )
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_raw_response_reject(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.remediations.with_raw_response.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        remediation = await response.parse()
        assert_matches_type(Remediation, remediation, path=["response"])

    @parametrize
    async def test_streaming_response_reject(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.remediations.with_streaming_response.reject(
            remediation_id="remediation_id",
            cluster_id="cluster_id",
            instance_id="instance_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            remediation = await response.parse()
            assert_matches_type(Remediation, remediation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_reject(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="remediation_id",
                cluster_id="",
                instance_id="instance_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `instance_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="remediation_id",
                cluster_id="cluster_id",
                instance_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `remediation_id` but received ''"):
            await async_client.beta.clusters.remediations.with_raw_response.reject(
                remediation_id="",
                cluster_id="cluster_id",
                instance_id="instance_id",
            )
