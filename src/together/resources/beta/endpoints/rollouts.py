# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
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
from ....pagination import SyncCursorPagination, AsyncCursorPagination
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.endpoints import (
    rollout_list_params,
    rollout_pause_params,
    rollout_cancel_params,
    rollout_create_params,
    rollout_delete_params,
    rollout_resume_params,
    rollout_promote_params,
    rollout_preview_defaults_params,
)
from ....types.beta.endpoints.rollout import Rollout
from ....types.beta.endpoints.metric_rule_param import MetricRuleParam
from ....types.beta.endpoints.canary_config_param import CanaryConfigParam
from ....types.beta.endpoints.rolling_config_param import RollingConfigParam
from ....types.beta.endpoints.blue_green_config_param import BlueGreenConfigParam
from ....types.beta.endpoints.rollout_delete_response import RolloutDeleteResponse
from ....types.beta.endpoints.rollout_defaults_preview import RolloutDefaultsPreview

__all__ = ["RolloutsResource", "AsyncRolloutsResource"]


class RolloutsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RolloutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return RolloutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RolloutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return RolloutsResourceWithStreamingResponse(self)

    def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        source_deployment_id: str,
        target_deployment_id: str,
        blue_green: BlueGreenConfigParam | Omit = omit,
        canary: CanaryConfigParam | Omit = omit,
        final_source_replicas: int | Omit = omit,
        final_target_replicas: int | Omit = omit,
        metrics: Iterable[MetricRuleParam] | Omit = omit,
        rolling: RollingConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """Creates a rollout in the pending state without shifting traffic.

        Start the
        rollout in a separate request after reviewing its strategy and metric gates.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          source_deployment_id: Deployment that traffic shifts away from.

          target_deployment_id: Deployment that traffic shifts toward.

          blue_green: Blue-green strategy configuration for a single cutover to the target deployment.

          canary: Canary strategy configuration for gradual traffic progression. An empty config
              uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair
              left by cancel, the default ladder is derived at start from the pair's current
              served share so it begins above it.

          final_source_replicas: Optional final replica count for the source deployment. Defaults to 0, which
              drains and stops the source.

          final_target_replicas: Optional target replica floor at completion. Must be at least 1 when set;
              defaults to the source deployment's replica count at create time, or to the
              source and target deployments' combined replica count when both already stand in
              the endpoint traffic split after a cancel. The completed target's autoscaling
              max lands at the landing ceiling, max(this value, the source max, the target's
              own max); the rollout may lift the target max at first wake, at the first step
              that needs it, or at completion unless an operator changes max mid-run. The
              lifted ceiling remains after completion, and PreviewRolloutDefaults reports a
              coming lift as ROLLOUT_WILL_RAISE_TARGET_MAX. A pre-existing target whose own
              autoscaling min is higher keeps that floor, reported as
              FINAL_BELOW_INHERITED_MIN. A target that starts stopped lands exactly at this
              value; if the source min was higher, PreviewRolloutDefaults reports
              FINAL_BELOW_SOURCE_MIN.

          metrics: Optional metric gates evaluated after each step's soak. Canary only; rejected on
              rolling and blue-green rollouts.

          rolling: Rolling strategy configuration for capacity-preserving batches that ramp target
              replicas up while draining source replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=maybe_transform(
                {
                    "source_deployment_id": source_deployment_id,
                    "target_deployment_id": target_deployment_id,
                    "blue_green": blue_green,
                    "canary": canary,
                    "final_source_replicas": final_source_replicas,
                    "final_target_replicas": final_target_replicas,
                    "metrics": metrics,
                    "rolling": rolling,
                },
                rollout_create_params.RolloutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Retrieves a rollout's strategy, lifecycle state, current traffic percentage,
        step history, and metric-gate results.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        filter: Literal["ROLLOUT_FILTER_ACTIVE", "ROLLOUT_FILTER_TERMINAL"] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPagination[Rollout]:
        """Lists rollout histories for an endpoint.

        Use `filter=ROLLOUT_FILTER_ACTIVE` to
        return only the active rollout, if one exists.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous rollout list response.

          filter: Narrow results to active or terminal rollouts. Omit to list all rollouts.

          limit: Maximum number of rollouts to return. Max 500, defaults to 50.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=SyncCursorPagination[Rollout],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "filter": filter,
                        "limit": limit,
                    },
                    rollout_list_params.RolloutListParams,
                ),
            ),
            model=Rollout,
        )

    def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RolloutDeleteResponse:
        """Deletes a rollout record.

        An active rollout must be aborted or completed before
        it can be deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"etag": etag}, rollout_delete_params.RolloutDeleteParams),
            ),
            cast_to=RolloutDeleteResponse,
        )

    def cancel(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        reason: str,
        disposition: Literal["CANCEL_DISPOSITION_FREEZE", "CANCEL_DISPOSITION_REVERT"] | Omit = omit,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Cancels a running, pausing, paused, system-paused, or stabilizing rollout by
        freezing the current traffic split into standing weights. Revert is removed and
        rejected; after canceling, start another canary rollout in either direction or
        rebalance the traffic split. The response is the accepted rollout snapshot; poll
        GetRollout until it reaches CANCELED.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          reason: Required human-readable reason recorded in the rollout audit trail.

          disposition: Optional cancel behavior. Absent defaults to freeze, which preserves the current
              traffic split. Revert is removed and rejected with FAILED_PRECONDITION; cancel
              with freeze, then run a reverse rollout back to the source.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/cancel",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "reason": reason,
                    "disposition": disposition,
                    "etag": etag,
                },
                rollout_cancel_params.RolloutCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def pause(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Requests a running or stabilizing rollout to pause and records an optional
        reason. The response returns the PAUSING snapshot; poll GetRollout until state
        is PAUSED to confirm the executor has parked.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          reason: Optional human-readable reason recorded on the rollout pause metadata.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/pause",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform(
                {
                    "etag": etag,
                    "reason": reason,
                },
                rollout_pause_params.RolloutPauseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def preview_defaults(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        source_deployment_id: str,
        target_deployment_id: str,
        blue_green: BlueGreenConfigParam | Omit = omit,
        canary: CanaryConfigParam | Omit = omit,
        final_source_replicas: int | Omit = omit,
        final_target_replicas: int | Omit = omit,
        metrics: Iterable[MetricRuleParam] | Omit = omit,
        rolling: RollingConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RolloutDefaultsPreview:
        """
        Returns the values a create request would pick for any field left unset, plus
        the capacity context needed to display them, without creating a rollout.
        Responses are display state only and re-validated authoritatively at create and
        start; do not copy response values back into a create request.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          source_deployment_id: Deployment that traffic shifts away from.

          target_deployment_id: Deployment that traffic shifts toward.

          blue_green: Blue-green strategy configuration for a single cutover to the target deployment.

          canary: Canary strategy configuration for gradual traffic progression. An empty config
              uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair
              left by cancel, the default ladder is derived at start from the pair's current
              served share so it begins above it.

          final_source_replicas: Optional final replica count for the source deployment. Defaults to 0, which
              drains and stops the source.

          final_target_replicas: Optional target replica floor at completion. Must be at least 1 when set;
              defaults to the source deployment's replica count at create time, or to the
              source and target deployments' combined replica count when both already stand in
              the endpoint traffic split after a cancel. The completed target's autoscaling
              max lands at the landing ceiling, max(this value, the source max, the target's
              own max); the rollout may lift the target max at first wake, at the first step
              that needs it, or at completion unless an operator changes max mid-run. The
              lifted ceiling remains after completion, and PreviewRolloutDefaults reports a
              coming lift as ROLLOUT_WILL_RAISE_TARGET_MAX. A pre-existing target whose own
              autoscaling min is higher keeps that floor, reported as
              FINAL_BELOW_INHERITED_MIN. A target that starts stopped lands exactly at this
              value; if the source min was higher, PreviewRolloutDefaults reports
              FINAL_BELOW_SOURCE_MIN.

          metrics: Optional metric gates evaluated after each step's soak. Canary only; rejected on
              rolling and blue-green rollouts.

          rolling: Rolling strategy configuration for capacity-preserving batches that ramp target
              replicas up while draining source replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/preview-defaults",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=maybe_transform(
                {
                    "source_deployment_id": source_deployment_id,
                    "target_deployment_id": target_deployment_id,
                    "blue_green": blue_green,
                    "canary": canary,
                    "final_source_replicas": final_source_replicas,
                    "final_target_replicas": final_target_replicas,
                    "metrics": metrics,
                    "rolling": rolling,
                },
                rollout_preview_defaults_params.RolloutPreviewDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RolloutDefaultsPreview,
        )

    def promote(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Completes a running or paused rollout immediately by sending all live traffic to
        the target deployment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/promote",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform({"etag": etag}, rollout_promote_params.RolloutPromoteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def resume(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Resumes a pausing, paused, or system-paused rollout from its current step and
        traffic split.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/resume",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=maybe_transform({"etag": etag}, rollout_resume_params.RolloutResumeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def start(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Starts a pending rollout and begins its configured traffic-shifting workflow.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/start",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )


class AsyncRolloutsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRolloutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncRolloutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRolloutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncRolloutsResourceWithStreamingResponse(self)

    async def create(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        source_deployment_id: str,
        target_deployment_id: str,
        blue_green: BlueGreenConfigParam | Omit = omit,
        canary: CanaryConfigParam | Omit = omit,
        final_source_replicas: int | Omit = omit,
        final_target_replicas: int | Omit = omit,
        metrics: Iterable[MetricRuleParam] | Omit = omit,
        rolling: RollingConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """Creates a rollout in the pending state without shifting traffic.

        Start the
        rollout in a separate request after reviewing its strategy and metric gates.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          source_deployment_id: Deployment that traffic shifts away from.

          target_deployment_id: Deployment that traffic shifts toward.

          blue_green: Blue-green strategy configuration for a single cutover to the target deployment.

          canary: Canary strategy configuration for gradual traffic progression. An empty config
              uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair
              left by cancel, the default ladder is derived at start from the pair's current
              served share so it begins above it.

          final_source_replicas: Optional final replica count for the source deployment. Defaults to 0, which
              drains and stops the source.

          final_target_replicas: Optional target replica floor at completion. Must be at least 1 when set;
              defaults to the source deployment's replica count at create time, or to the
              source and target deployments' combined replica count when both already stand in
              the endpoint traffic split after a cancel. The completed target's autoscaling
              max lands at the landing ceiling, max(this value, the source max, the target's
              own max); the rollout may lift the target max at first wake, at the first step
              that needs it, or at completion unless an operator changes max mid-run. The
              lifted ceiling remains after completion, and PreviewRolloutDefaults reports a
              coming lift as ROLLOUT_WILL_RAISE_TARGET_MAX. A pre-existing target whose own
              autoscaling min is higher keeps that floor, reported as
              FINAL_BELOW_INHERITED_MIN. A target that starts stopped lands exactly at this
              value; if the source min was higher, PreviewRolloutDefaults reports
              FINAL_BELOW_SOURCE_MIN.

          metrics: Optional metric gates evaluated after each step's soak. Canary only; rejected on
              rolling and blue-green rollouts.

          rolling: Rolling strategy configuration for capacity-preserving batches that ramp target
              replicas up while draining source replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=await async_maybe_transform(
                {
                    "source_deployment_id": source_deployment_id,
                    "target_deployment_id": target_deployment_id,
                    "blue_green": blue_green,
                    "canary": canary,
                    "final_source_replicas": final_source_replicas,
                    "final_target_replicas": final_target_replicas,
                    "metrics": metrics,
                    "rolling": rolling,
                },
                rollout_create_params.RolloutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    async def retrieve(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Retrieves a rollout's strategy, lifecycle state, current traffic percentage,
        step history, and metric-gate results.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    def list(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        after: str | Omit = omit,
        filter: Literal["ROLLOUT_FILTER_ACTIVE", "ROLLOUT_FILTER_TERMINAL"] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Rollout, AsyncCursorPagination[Rollout]]:
        """Lists rollout histories for an endpoint.

        Use `filter=ROLLOUT_FILTER_ACTIVE` to
        return only the active rollout, if one exists.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          after: Cursor from a previous rollout list response.

          filter: Narrow results to active or terminal rollouts. Omit to list all rollouts.

          limit: Maximum number of rollouts to return. Max 500, defaults to 50.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return self._get_api_list(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            page=AsyncCursorPagination[Rollout],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "filter": filter,
                        "limit": limit,
                    },
                    rollout_list_params.RolloutListParams,
                ),
            ),
            model=Rollout,
        )

    async def delete(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RolloutDeleteResponse:
        """Deletes a rollout record.

        An active rollout must be aborted or completed before
        it can be deleted.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"etag": etag}, rollout_delete_params.RolloutDeleteParams),
            ),
            cast_to=RolloutDeleteResponse,
        )

    async def cancel(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        reason: str,
        disposition: Literal["CANCEL_DISPOSITION_FREEZE", "CANCEL_DISPOSITION_REVERT"] | Omit = omit,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Cancels a running, pausing, paused, system-paused, or stabilizing rollout by
        freezing the current traffic split into standing weights. Revert is removed and
        rejected; after canceling, start another canary rollout in either direction or
        rebalance the traffic split. The response is the accepted rollout snapshot; poll
        GetRollout until it reaches CANCELED.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          reason: Required human-readable reason recorded in the rollout audit trail.

          disposition: Optional cancel behavior. Absent defaults to freeze, which preserves the current
              traffic split. Revert is removed and rejected with FAILED_PRECONDITION; cancel
              with freeze, then run a reverse rollout back to the source.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/cancel",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "reason": reason,
                    "disposition": disposition,
                    "etag": etag,
                },
                rollout_cancel_params.RolloutCancelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    async def pause(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Requests a running or stabilizing rollout to pause and records an optional
        reason. The response returns the PAUSING snapshot; poll GetRollout until state
        is PAUSED to confirm the executor has parked.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          reason: Optional human-readable reason recorded on the rollout pause metadata.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/pause",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform(
                {
                    "etag": etag,
                    "reason": reason,
                },
                rollout_pause_params.RolloutPauseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    async def preview_defaults(
        self,
        endpoint_id: str,
        *,
        project_id: str | None = None,
        source_deployment_id: str,
        target_deployment_id: str,
        blue_green: BlueGreenConfigParam | Omit = omit,
        canary: CanaryConfigParam | Omit = omit,
        final_source_replicas: int | Omit = omit,
        final_target_replicas: int | Omit = omit,
        metrics: Iterable[MetricRuleParam] | Omit = omit,
        rolling: RollingConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RolloutDefaultsPreview:
        """
        Returns the values a create request would pick for any field left unset, plus
        the capacity context needed to display them, without creating a rollout.
        Responses are display state only and re-validated authoritatively at create and
        start; do not copy response values back into a create request.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          source_deployment_id: Deployment that traffic shifts away from.

          target_deployment_id: Deployment that traffic shifts toward.

          blue_green: Blue-green strategy configuration for a single cutover to the target deployment.

          canary: Canary strategy configuration for gradual traffic progression. An empty config
              uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair
              left by cancel, the default ladder is derived at start from the pair's current
              served share so it begins above it.

          final_source_replicas: Optional final replica count for the source deployment. Defaults to 0, which
              drains and stops the source.

          final_target_replicas: Optional target replica floor at completion. Must be at least 1 when set;
              defaults to the source deployment's replica count at create time, or to the
              source and target deployments' combined replica count when both already stand in
              the endpoint traffic split after a cancel. The completed target's autoscaling
              max lands at the landing ceiling, max(this value, the source max, the target's
              own max); the rollout may lift the target max at first wake, at the first step
              that needs it, or at completion unless an operator changes max mid-run. The
              lifted ceiling remains after completion, and PreviewRolloutDefaults reports a
              coming lift as ROLLOUT_WILL_RAISE_TARGET_MAX. A pre-existing target whose own
              autoscaling min is higher keeps that floor, reported as
              FINAL_BELOW_INHERITED_MIN. A target that starts stopped lands exactly at this
              value; if the source min was higher, PreviewRolloutDefaults reports
              FINAL_BELOW_SOURCE_MIN.

          metrics: Optional metric gates evaluated after each step's soak. Canary only; rejected on
              rolling and blue-green rollouts.

          rolling: Rolling strategy configuration for capacity-preserving batches that ramp target
              replicas up while draining source replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/preview-defaults",
                project_id=project_id,
                endpoint_id=endpoint_id,
            ),
            body=await async_maybe_transform(
                {
                    "source_deployment_id": source_deployment_id,
                    "target_deployment_id": target_deployment_id,
                    "blue_green": blue_green,
                    "canary": canary,
                    "final_source_replicas": final_source_replicas,
                    "final_target_replicas": final_target_replicas,
                    "metrics": metrics,
                    "rolling": rolling,
                },
                rollout_preview_defaults_params.RolloutPreviewDefaultsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RolloutDefaultsPreview,
        )

    async def promote(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Completes a running or paused rollout immediately by sending all live traffic to
        the target deployment.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/promote",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform({"etag": etag}, rollout_promote_params.RolloutPromoteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    async def resume(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        etag: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Resumes a pausing, paused, or system-paused rollout from its current step and
        traffic split.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          etag: Optional etag for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/resume",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            body=await async_maybe_transform({"etag": etag}, rollout_resume_params.RolloutResumeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )

    async def start(
        self,
        id: str,
        *,
        project_id: str | None = None,
        endpoint_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Rollout:
        """
        Starts a pending rollout and begins its configured traffic-shifting workflow.

        Args:
          project_id: Project identifier.

          endpoint_id: Endpoint identifier.

          id: Rollout identifier.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_project_id_path_param()
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not endpoint_id:
            raise ValueError(f"Expected a non-empty value for `endpoint_id` but received {endpoint_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            ("https://api.together.ai/v2" if not self._client._base_url_overridden else "")
            + path_template(
                "/projects/{project_id}/endpoints/{endpoint_id}/rollouts/{id}/start",
                project_id=project_id,
                endpoint_id=endpoint_id,
                id=id,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Rollout,
        )


class RolloutsResourceWithRawResponse:
    def __init__(self, rollouts: RolloutsResource) -> None:
        self._rollouts = rollouts

        self.create = to_raw_response_wrapper(
            rollouts.create,
        )
        self.retrieve = to_raw_response_wrapper(
            rollouts.retrieve,
        )
        self.list = to_raw_response_wrapper(
            rollouts.list,
        )
        self.delete = to_raw_response_wrapper(
            rollouts.delete,
        )
        self.cancel = to_raw_response_wrapper(
            rollouts.cancel,
        )
        self.pause = to_raw_response_wrapper(
            rollouts.pause,
        )
        self.preview_defaults = to_raw_response_wrapper(
            rollouts.preview_defaults,
        )
        self.promote = to_raw_response_wrapper(
            rollouts.promote,
        )
        self.resume = to_raw_response_wrapper(
            rollouts.resume,
        )
        self.start = to_raw_response_wrapper(
            rollouts.start,
        )


class AsyncRolloutsResourceWithRawResponse:
    def __init__(self, rollouts: AsyncRolloutsResource) -> None:
        self._rollouts = rollouts

        self.create = async_to_raw_response_wrapper(
            rollouts.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            rollouts.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            rollouts.list,
        )
        self.delete = async_to_raw_response_wrapper(
            rollouts.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            rollouts.cancel,
        )
        self.pause = async_to_raw_response_wrapper(
            rollouts.pause,
        )
        self.preview_defaults = async_to_raw_response_wrapper(
            rollouts.preview_defaults,
        )
        self.promote = async_to_raw_response_wrapper(
            rollouts.promote,
        )
        self.resume = async_to_raw_response_wrapper(
            rollouts.resume,
        )
        self.start = async_to_raw_response_wrapper(
            rollouts.start,
        )


class RolloutsResourceWithStreamingResponse:
    def __init__(self, rollouts: RolloutsResource) -> None:
        self._rollouts = rollouts

        self.create = to_streamed_response_wrapper(
            rollouts.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            rollouts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            rollouts.list,
        )
        self.delete = to_streamed_response_wrapper(
            rollouts.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            rollouts.cancel,
        )
        self.pause = to_streamed_response_wrapper(
            rollouts.pause,
        )
        self.preview_defaults = to_streamed_response_wrapper(
            rollouts.preview_defaults,
        )
        self.promote = to_streamed_response_wrapper(
            rollouts.promote,
        )
        self.resume = to_streamed_response_wrapper(
            rollouts.resume,
        )
        self.start = to_streamed_response_wrapper(
            rollouts.start,
        )


class AsyncRolloutsResourceWithStreamingResponse:
    def __init__(self, rollouts: AsyncRolloutsResource) -> None:
        self._rollouts = rollouts

        self.create = async_to_streamed_response_wrapper(
            rollouts.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            rollouts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            rollouts.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            rollouts.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            rollouts.cancel,
        )
        self.pause = async_to_streamed_response_wrapper(
            rollouts.pause,
        )
        self.preview_defaults = async_to_streamed_response_wrapper(
            rollouts.preview_defaults,
        )
        self.promote = async_to_streamed_response_wrapper(
            rollouts.promote,
        )
        self.resume = async_to_streamed_response_wrapper(
            rollouts.resume,
        )
        self.start = async_to_streamed_response_wrapper(
            rollouts.start,
        )
