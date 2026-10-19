# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncCursorPagination, AsyncCursorPagination
from ...._base_client import AsyncPaginator, make_request_options
from ....types.organization.usage import cost_list_params
from ....types.organization.billing_usage_window import BillingUsageWindow

__all__ = ["CostsResource", "AsyncCostsResource"]


class CostsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CostsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return CostsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CostsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return CostsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        after: str | Omit = omit,
        granularity: Literal["day", "hour"] | Omit = omit,
        limit: int | Omit = omit,
        month: str | Omit = omit,
        organization_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[BillingUsageWindow]:
        """
        Returns an organization's billing usage for a month as cost-annotated line items
        grouped into time windows. Finalized windows are returned through the end of
        yesterday at daily granularity, or the last completed hour at hourly granularity
        (UTC).

        Args:
          after: Opaque cursor from a previous response's `next_cursor`. Only valid for the month
              and granularity it was issued for. Current-month data is a moving snapshot: each
              page reflects data as of its request, so newly completed windows may appear at
              the end of the sequence.

          granularity: Time window size for rows. 'hour' returns ~24x more rows than 'day'.

          limit: Maximum number of time windows per page (max 1000).

          month: Billing month in YYYY-MM format. Defaults to the current month, which returns
              data through yesterday (daily) or the last completed hour (hourly).

          organization_id: Organization to report on. Usage is always reported for the organization that
              owns the API key, so this is optional; supplying an ID that is not that
              organization returns 403.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/billing/usage",
            page=SyncCursorPagination[BillingUsageWindow],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "granularity": granularity,
                        "limit": limit,
                        "month": month,
                        "organization_id": organization_id,
                    },
                    cost_list_params.CostListParams,
                ),
            ),
            model=BillingUsageWindow,
        )


class AsyncCostsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCostsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncCostsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCostsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncCostsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        after: str | Omit = omit,
        granularity: Literal["day", "hour"] | Omit = omit,
        limit: int | Omit = omit,
        month: str | Omit = omit,
        organization_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[BillingUsageWindow, AsyncCursorPagination[BillingUsageWindow]]:
        """
        Returns an organization's billing usage for a month as cost-annotated line items
        grouped into time windows. Finalized windows are returned through the end of
        yesterday at daily granularity, or the last completed hour at hourly granularity
        (UTC).

        Args:
          after: Opaque cursor from a previous response's `next_cursor`. Only valid for the month
              and granularity it was issued for. Current-month data is a moving snapshot: each
              page reflects data as of its request, so newly completed windows may appear at
              the end of the sequence.

          granularity: Time window size for rows. 'hour' returns ~24x more rows than 'day'.

          limit: Maximum number of time windows per page (max 1000).

          month: Billing month in YYYY-MM format. Defaults to the current month, which returns
              data through yesterday (daily) or the last completed hour (hourly).

          organization_id: Organization to report on. Usage is always reported for the organization that
              owns the API key, so this is optional; supplying an ID that is not that
              organization returns 403.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/billing/usage",
            page=AsyncCursorPagination[BillingUsageWindow],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "granularity": granularity,
                        "limit": limit,
                        "month": month,
                        "organization_id": organization_id,
                    },
                    cost_list_params.CostListParams,
                ),
            ),
            model=BillingUsageWindow,
        )


class CostsResourceWithRawResponse:
    def __init__(self, costs: CostsResource) -> None:
        self._costs = costs

        self.list = to_raw_response_wrapper(
            costs.list,
        )


class AsyncCostsResourceWithRawResponse:
    def __init__(self, costs: AsyncCostsResource) -> None:
        self._costs = costs

        self.list = async_to_raw_response_wrapper(
            costs.list,
        )


class CostsResourceWithStreamingResponse:
    def __init__(self, costs: CostsResource) -> None:
        self._costs = costs

        self.list = to_streamed_response_wrapper(
            costs.list,
        )


class AsyncCostsResourceWithStreamingResponse:
    def __init__(self, costs: AsyncCostsResource) -> None:
        self._costs = costs

        self.list = async_to_streamed_response_wrapper(
            costs.list,
        )
