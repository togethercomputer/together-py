# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.clusters import (
    remediation_list_params,
    remediation_create_params,
    remediation_reject_params,
    remediation_approve_params,
)
from ....types.beta.clusters.remediation import Remediation
from ....types.beta.clusters.remediation_list_response import RemediationListResponse

__all__ = ["RemediationsResource", "AsyncRemediationsResource"]


class RemediationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RemediationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RemediationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RemediationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RemediationsResourceWithStreamingResponse(self)

    def create(
        self,
        instance_id: str,
        *,
        cluster_id: str,
        mode: Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ],
        remediation_id: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Creates a new remediation for an instance.

        Remediations created via the API goes directly to PENDING state.

        Our system may trigger automated remediations that require approval. These
        remediations are created with PENDING_APPROVAL state. The user must call
        /approve to start the actual remediation process. These operations can also be
        rejected by calling /reject.

        Args:
          mode: Remediation mode specifies how the remediation should be performed.

              - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
                available host.
              - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
                provisions a new one on a different host.

          remediation_id: Client-specified ID for idempotency.

          reason: User-provided reason for the remediation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        return self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations",
                cluster_id=cluster_id,
                instance_id=instance_id,
            ),
            body=maybe_transform(
                {
                    "mode": mode,
                    "reason": reason,
                },
                remediation_create_params.RemediationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"remediation_id": remediation_id}, remediation_create_params.RemediationCreateParams
                ),
            ),
            cast_to=Remediation,
        )

    def retrieve(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Retrieve the status of a specific remdiation on a specific instance in a
        specific cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return self._get(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    def list(
        self,
        instance_id: str,
        *,
        cluster_id: str,
        mode: List[
            Literal[
                "REMEDIATION_MODE_VM_ONLY",
                "REMEDIATION_MODE_HOST_AWARE",
                "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
                "REMEDIATION_MODE_REBOOT_VM",
            ]
        ]
        | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        state: List[
            Literal["PENDING_APPROVAL", "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "AUTO_RESOLVED"]
        ]
        | Omit = omit,
        trigger: List[Literal["REMEDIATION_TRIGGER_MANUAL", "REMEDIATION_TRIGGER_AUTOMATED"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RemediationListResponse:
        """
        Lists remediations for an instance or cluster.

        Args:
          instance_id: To list remediations on a specific node, pass the node's instance ID. To list
              remediations for all nodes in a cluster, pass `-` as a wildcard for the instance
              ID.

          mode: Filter by remediation mode(s). Returns remediations matching any of the
              specified modes.

          order_by: Order by expression.

          page_size: Maximum results to return.

          page_token: Pagination token from previous request.

          state: Filter by state(s). Returns remediations matching any of the specified states.

              - `PENDING_APPROVAL`: Awaiting approval before processing can begin.
              - `PENDING`: Approved and queued for processing.
              - `RUNNING`: Actively being processed.
              - `SUCCEEDED`: Successfully completed.
              - `FAILED`: Failed with an error.
              - `CANCELLED`: Cancelled by user or system.
              - `AUTO_RESOLVED`: The underlying issue was automatically resolved before
                processing.

          trigger: Filter by trigger type(s). Returns remediations matching any of the specified
              triggers.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        return self._get(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations",
                cluster_id=cluster_id,
                instance_id=instance_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "mode": mode,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "state": state,
                        "trigger": trigger,
                    },
                    remediation_list_params.RemediationListParams,
                ),
            ),
            cast_to=RemediationListResponse,
        )

    def approve(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        comment: str | Omit = omit,
        mode: Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Approves a pending remediation.

        Only remediations with state PENDING_APPROVAL can be approved.

        On APPROVE: state changes to PENDING and the remediation process begins. The
        reviewed_by, review_time, and review_comment fields are populated on the
        remediation after approval.

        Args:
          comment: Approval comment explaining the decision.

          mode: Remediation mode to use after approval. When omitted, the remediation keeps its
              existing mode.

              - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
                available host.
              - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
                provisions a new one on a different host.
              - `REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT`: Evicts the VM without
                provisioning a replacement.
              - `REMEDIATION_MODE_REBOOT_VM`: Reboots the VM in place.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/approve",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            body=maybe_transform(
                {
                    "comment": comment,
                    "mode": mode,
                },
                remediation_approve_params.RemediationApproveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    def cancel(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Cancels a pending remediation.

        Only remediations in PENDING_APPROVAL or PENDING state can be cancelled.

        Args:
          cluster_id: The cluster ID.

          instance_id: The instance ID.

          remediation_id: The remediation ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/cancel",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    def reject(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Rejects a pending remediation.

        Only remediations with state PENDING_APPROVAL can be rejected.

        On REJECT: state changes to CANCELLED. The reviewed_by, review_time, and
        review_comment fields are populated on the remediation after rejection.

        Args:
          comment: Comment explaining the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/reject",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            body=maybe_transform({"comment": comment}, remediation_reject_params.RemediationRejectParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )


class AsyncRemediationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRemediationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRemediationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRemediationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRemediationsResourceWithStreamingResponse(self)

    async def create(
        self,
        instance_id: str,
        *,
        cluster_id: str,
        mode: Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ],
        remediation_id: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Creates a new remediation for an instance.

        Remediations created via the API goes directly to PENDING state.

        Our system may trigger automated remediations that require approval. These
        remediations are created with PENDING_APPROVAL state. The user must call
        /approve to start the actual remediation process. These operations can also be
        rejected by calling /reject.

        Args:
          mode: Remediation mode specifies how the remediation should be performed.

              - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
                available host.
              - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
                provisions a new one on a different host.

          remediation_id: Client-specified ID for idempotency.

          reason: User-provided reason for the remediation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        return await self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations",
                cluster_id=cluster_id,
                instance_id=instance_id,
            ),
            body=await async_maybe_transform(
                {
                    "mode": mode,
                    "reason": reason,
                },
                remediation_create_params.RemediationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"remediation_id": remediation_id}, remediation_create_params.RemediationCreateParams
                ),
            ),
            cast_to=Remediation,
        )

    async def retrieve(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Retrieve the status of a specific remdiation on a specific instance in a
        specific cluster.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return await self._get(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    async def list(
        self,
        instance_id: str,
        *,
        cluster_id: str,
        mode: List[
            Literal[
                "REMEDIATION_MODE_VM_ONLY",
                "REMEDIATION_MODE_HOST_AWARE",
                "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
                "REMEDIATION_MODE_REBOOT_VM",
            ]
        ]
        | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        state: List[
            Literal["PENDING_APPROVAL", "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "AUTO_RESOLVED"]
        ]
        | Omit = omit,
        trigger: List[Literal["REMEDIATION_TRIGGER_MANUAL", "REMEDIATION_TRIGGER_AUTOMATED"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RemediationListResponse:
        """
        Lists remediations for an instance or cluster.

        Args:
          instance_id: To list remediations on a specific node, pass the node's instance ID. To list
              remediations for all nodes in a cluster, pass `-` as a wildcard for the instance
              ID.

          mode: Filter by remediation mode(s). Returns remediations matching any of the
              specified modes.

          order_by: Order by expression.

          page_size: Maximum results to return.

          page_token: Pagination token from previous request.

          state: Filter by state(s). Returns remediations matching any of the specified states.

              - `PENDING_APPROVAL`: Awaiting approval before processing can begin.
              - `PENDING`: Approved and queued for processing.
              - `RUNNING`: Actively being processed.
              - `SUCCEEDED`: Successfully completed.
              - `FAILED`: Failed with an error.
              - `CANCELLED`: Cancelled by user or system.
              - `AUTO_RESOLVED`: The underlying issue was automatically resolved before
                processing.

          trigger: Filter by trigger type(s). Returns remediations matching any of the specified
              triggers.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        return await self._get(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations",
                cluster_id=cluster_id,
                instance_id=instance_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "mode": mode,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "state": state,
                        "trigger": trigger,
                    },
                    remediation_list_params.RemediationListParams,
                ),
            ),
            cast_to=RemediationListResponse,
        )

    async def approve(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        comment: str | Omit = omit,
        mode: Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Approves a pending remediation.

        Only remediations with state PENDING_APPROVAL can be approved.

        On APPROVE: state changes to PENDING and the remediation process begins. The
        reviewed_by, review_time, and review_comment fields are populated on the
        remediation after approval.

        Args:
          comment: Approval comment explaining the decision.

          mode: Remediation mode to use after approval. When omitted, the remediation keeps its
              existing mode.

              - `REMEDIATION_MODE_VM_ONLY`: Deletes the VM and provisions a new one on any
                available host.
              - `REMEDIATION_MODE_HOST_AWARE`: Cordons the host, deletes the VM, and
                provisions a new one on a different host.
              - `REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT`: Evicts the VM without
                provisioning a replacement.
              - `REMEDIATION_MODE_REBOOT_VM`: Reboots the VM in place.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return await self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/approve",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            body=await async_maybe_transform(
                {
                    "comment": comment,
                    "mode": mode,
                },
                remediation_approve_params.RemediationApproveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    async def cancel(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Cancels a pending remediation.

        Only remediations in PENDING_APPROVAL or PENDING state can be cancelled.

        Args:
          cluster_id: The cluster ID.

          instance_id: The instance ID.

          remediation_id: The remediation ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return await self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/cancel",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )

    async def reject(
        self,
        remediation_id: str,
        *,
        cluster_id: str,
        instance_id: str,
        comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Remediation:
        """
        Rejects a pending remediation.

        Only remediations with state PENDING_APPROVAL can be rejected.

        On REJECT: state changes to CANCELLED. The reviewed_by, review_time, and
        review_comment fields are populated on the remediation after rejection.

        Args:
          comment: Comment explaining the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cluster_id:
            raise ValueError(f"Expected a non-empty value for `cluster_id` but received {cluster_id!r}")
        if not instance_id:
            raise ValueError(f"Expected a non-empty value for `instance_id` but received {instance_id!r}")
        if not remediation_id:
            raise ValueError(f"Expected a non-empty value for `remediation_id` but received {remediation_id!r}")
        return await self._post(
            path_template(
                "/compute/clusters/{cluster_id}/instances/{instance_id}/remediations/{remediation_id}/reject",
                cluster_id=cluster_id,
                instance_id=instance_id,
                remediation_id=remediation_id,
            ),
            body=await async_maybe_transform({"comment": comment}, remediation_reject_params.RemediationRejectParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Remediation,
        )


class RemediationsResourceWithRawResponse:
    def __init__(self, remediations: RemediationsResource) -> None:
        self._remediations = remediations

        self.create = to_raw_response_wrapper(
            remediations.create,
        )
        self.retrieve = to_raw_response_wrapper(
            remediations.retrieve,
        )
        self.list = to_raw_response_wrapper(
            remediations.list,
        )
        self.approve = to_raw_response_wrapper(
            remediations.approve,
        )
        self.cancel = to_raw_response_wrapper(
            remediations.cancel,
        )
        self.reject = to_raw_response_wrapper(
            remediations.reject,
        )


class AsyncRemediationsResourceWithRawResponse:
    def __init__(self, remediations: AsyncRemediationsResource) -> None:
        self._remediations = remediations

        self.create = async_to_raw_response_wrapper(
            remediations.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            remediations.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            remediations.list,
        )
        self.approve = async_to_raw_response_wrapper(
            remediations.approve,
        )
        self.cancel = async_to_raw_response_wrapper(
            remediations.cancel,
        )
        self.reject = async_to_raw_response_wrapper(
            remediations.reject,
        )


class RemediationsResourceWithStreamingResponse:
    def __init__(self, remediations: RemediationsResource) -> None:
        self._remediations = remediations

        self.create = to_streamed_response_wrapper(
            remediations.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            remediations.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            remediations.list,
        )
        self.approve = to_streamed_response_wrapper(
            remediations.approve,
        )
        self.cancel = to_streamed_response_wrapper(
            remediations.cancel,
        )
        self.reject = to_streamed_response_wrapper(
            remediations.reject,
        )


class AsyncRemediationsResourceWithStreamingResponse:
    def __init__(self, remediations: AsyncRemediationsResource) -> None:
        self._remediations = remediations

        self.create = async_to_streamed_response_wrapper(
            remediations.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            remediations.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            remediations.list,
        )
        self.approve = async_to_streamed_response_wrapper(
            remediations.approve,
        )
        self.cancel = async_to_streamed_response_wrapper(
            remediations.cancel,
        )
        self.reject = async_to_streamed_response_wrapper(
            remediations.reject,
        )
