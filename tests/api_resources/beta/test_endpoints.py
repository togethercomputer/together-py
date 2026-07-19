# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together._utils import parse_datetime
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta import (
    Endpoint,
    EndpointDeleteResponse,
    EndpointAnalyticsResponse,
    EndpointListEventsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEndpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        endpoint = client.beta.endpoints.create(
            project_id="projectId",
            name="name",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.create(
            project_id="projectId",
            name="name",
            visibility="VISIBILITY_PRIVATE",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.create(
            project_id="projectId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.create(
            project_id="projectId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.create(
                project_id="",
                name="name",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        endpoint = client.beta.endpoints.retrieve(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.retrieve(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.with_raw_response.retrieve(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        endpoint = client.beta.endpoints.update(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.update(
            id="id",
            project_id="projectId",
            update_mask="updateMask",
            etag="etag",
            name="name",
            traffic_split=[
                {
                    "deployment_id": "deploymentId",
                    "weight": 0,
                }
            ],
            visibility="VISIBILITY_PRIVATE",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.update(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.update(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.update(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.with_raw_response.update(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list(
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list(
            project_id="projectId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.list(
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.list(
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.list(
                project_id="",
            )

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        endpoint = client.beta.endpoints.delete(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.delete(
            id="id",
            project_id="projectId",
            etag="etag",
        )
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.delete(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.delete(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.delete(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.with_raw_response.delete(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_analytics(self, client: Together) -> None:
        endpoint = client.beta.endpoints.analytics(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    def test_method_analytics_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.analytics(
            id="id",
            project_id="projectId",
            deployment_id="deploymentId",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            granularity="granularity",
            include_time_series=True,
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    def test_raw_response_analytics(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.analytics(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_analytics(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.analytics(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_analytics(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.analytics(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.with_raw_response.analytics(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_list_events(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list_events(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    def test_method_list_events_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list_events(
            id="id",
            project_id="projectId",
            after="after",
            deployment_ids=["string"],
            limit=0,
            min_level="LEVEL_DEBUG",
            since=parse_datetime("2019-12-27T18:11:19.117Z"),
            source_kinds=["SOURCE_KIND_ENDPOINT"],
            subject_id="subjectId",
            types=["string"],
            until=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(SyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    def test_raw_response_list_events(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.list_events(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(SyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list_events(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.list_events(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(SyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_events(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.with_raw_response.list_events(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.with_raw_response.list_events(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_list_org_scoped(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list_org_scoped(
            organization_id="organizationId",
        )
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_method_list_org_scoped_with_all_params(self, client: Together) -> None:
        endpoint = client.beta.endpoints.list_org_scoped(
            organization_id="organizationId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_raw_response_list_org_scoped(self, client: Together) -> None:
        response = client.beta.endpoints.with_raw_response.list_org_scoped(
            organization_id="organizationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list_org_scoped(self, client: Together) -> None:
        with client.beta.endpoints.with_streaming_response.list_org_scoped(
            organization_id="organizationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(SyncCursorPagination[Endpoint], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_org_scoped(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.beta.endpoints.with_raw_response.list_org_scoped(
                organization_id="",
            )


class TestAsyncEndpoints:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.create(
            project_id="projectId",
            name="name",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.create(
            project_id="projectId",
            name="name",
            visibility="VISIBILITY_PRIVATE",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.create(
            project_id="projectId",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.create(
            project_id="projectId",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.create(
                project_id="",
                name="name",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.retrieve(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.retrieve(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.retrieve(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.update(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.update(
            id="id",
            project_id="projectId",
            update_mask="updateMask",
            etag="etag",
            name="name",
            traffic_split=[
                {
                    "deployment_id": "deploymentId",
                    "weight": 0,
                }
            ],
            visibility="VISIBILITY_PRIVATE",
        )
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.update(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(Endpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.update(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(Endpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.update(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.update(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list(
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list(
            project_id="projectId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.list(
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.list(
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.list(
                project_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.delete(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.delete(
            id="id",
            project_id="projectId",
            etag="etag",
        )
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.delete(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.delete(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(EndpointDeleteResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.delete(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.delete(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_analytics(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.analytics(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    async def test_method_analytics_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.analytics(
            id="id",
            project_id="projectId",
            deployment_id="deploymentId",
            end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            granularity="granularity",
            include_time_series=True,
            start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_analytics(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.analytics(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_analytics(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.analytics(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(EndpointAnalyticsResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_analytics(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.analytics(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.analytics(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_list_events(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list_events(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list_events(
            id="id",
            project_id="projectId",
            after="after",
            deployment_ids=["string"],
            limit=0,
            min_level="LEVEL_DEBUG",
            since=parse_datetime("2019-12-27T18:11:19.117Z"),
            source_kinds=["SOURCE_KIND_ENDPOINT"],
            subject_id="subjectId",
            types=["string"],
            until=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AsyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.list_events(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(AsyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.list_events(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(AsyncCursorPagination[EndpointListEventsResponse], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.list_events(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.list_events(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_list_org_scoped(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list_org_scoped(
            organization_id="organizationId",
        )
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_method_list_org_scoped_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.beta.endpoints.list_org_scoped(
            organization_id="organizationId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list_org_scoped(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.with_raw_response.list_org_scoped(
            organization_id="organizationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list_org_scoped(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.with_streaming_response.list_org_scoped(
            organization_id="organizationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(AsyncCursorPagination[Endpoint], endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_org_scoped(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.beta.endpoints.with_raw_response.list_org_scoped(
                organization_id="",
            )
