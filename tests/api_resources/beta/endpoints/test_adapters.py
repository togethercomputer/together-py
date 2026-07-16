# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta.endpoints import (
    AdapterListResponse,
    AdapterCreateResponse,
    AdapterDeleteResponse,
    AdapterUpdateResponse,
    AdapterRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdapters:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        )
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
            adapter_revision_id="adapterRevisionId",
            force=True,
        )
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.endpoints.adapters.with_raw_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.endpoints.adapters.with_streaming_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.create(
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_model_id="adapterModelId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.create(
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                adapter_model_id="adapterModelId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.create(
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                adapter_model_id="adapterModelId",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        )
        assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.adapters.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.adapters.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        )
        assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.endpoints.adapters.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.endpoints.adapters.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
            after="after",
            limit=0,
        )
        assert_matches_type(SyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.adapters.with_raw_response.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(SyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.adapters.with_streaming_response.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(SyncCursorPagination[AdapterListResponse], adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="",
                deployment_id="deploymentId",
                project_id="projectId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="endpointId",
                deployment_id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        adapter = client.beta.endpoints.adapters.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        )
        assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.endpoints.adapters.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.endpoints.adapters.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.adapters.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                etag="etag",
            )


class TestAsyncAdapters:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        )
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
            adapter_revision_id="adapterRevisionId",
            force=True,
        )
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.adapters.with_raw_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.adapters.with_streaming_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_model_id="adapterModelId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterCreateResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.create(
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_model_id="adapterModelId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.create(
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                adapter_model_id="adapterModelId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.create(
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                adapter_model_id="adapterModelId",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        )
        assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.adapters.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.adapters.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterRetrieveResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        )
        assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.adapters.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.adapters.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            adapter_revision_id="adapterRevisionId",
            etag="etag",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterUpdateResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                adapter_revision_id="adapterRevisionId",
                etag="etag",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
            after="after",
            limit=0,
        )
        assert_matches_type(AsyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.adapters.with_raw_response.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AsyncCursorPagination[AdapterListResponse], adapter, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.adapters.with_streaming_response.list(
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AsyncCursorPagination[AdapterListResponse], adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="",
                deployment_id="deploymentId",
                project_id="projectId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.list(
                endpoint_id="endpointId",
                deployment_id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.beta.endpoints.adapters.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        )
        assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.adapters.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.adapters.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            deployment_id="deploymentId",
            etag="etag",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterDeleteResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
                deployment_id="deploymentId",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="",
                etag="etag",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.adapters.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                deployment_id="deploymentId",
                etag="etag",
            )
