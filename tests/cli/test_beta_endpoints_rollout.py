from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.types.beta.endpoint import Endpoint
from together.types.beta.endpoints.rollout import Rollout, StatusStep, StatusCondition, StatusConditionMetric
from together.lib.cli.api.beta.endpoints.rollout import (
    build_canary,
    parse_canary_steps,
    _infer_active_source,
    _verify_rollout_pair,
    resolve_rollout_strategy,
)
from together.lib.cli.api.beta.endpoints.retrieve import (
    rollout_reason_rows,
    format_rollout_progress,
    format_status_step_line,
    format_condition_metric_line,
    format_rollout_condition_summary,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _deployment_summary(
    deployment_id: str,
    *,
    name: str | None = None,
    traffic_mode: str = "TRAFFIC_MODE_LIVE",
    estimated_effective_traffic_share: float = 0.0,
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": deployment_id,
        "name": name or f"my-project/my-endpoint/{deployment_id.removeprefix('dep_')}",
        "model": f"projects/proj/models/model-{deployment_id}/revisions/latest",
        "modelId": f"model-{deployment_id}",
        "hardware": "1x-h100",
        "state": "DEPLOYMENT_STATE_READY",
        "readyReplicas": 1,
        "desiredReplicas": 1,
        "trafficMode": traffic_mode,
        "estimatedEffectiveTrafficShare": estimated_effective_traffic_share,
        "createdAt": "2026-01-01T00:00:00Z",
        "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
    }
    body.update(overrides)
    return body


def _endpoint_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ep_1",
        "projectId": "proj",
        "name": "my-project/my-endpoint",
        "etag": "etag-ep",
        "trafficSplit": [
            {"deploymentId": "dep_source", "weight": 1.0},
            {"deploymentId": "dep_target", "weight": 0.0},
        ],
        "deployments": [
            _deployment_summary("dep_source", estimated_effective_traffic_share=1.0),
            _deployment_summary("dep_target", estimated_effective_traffic_share=0.0),
        ],
        "createdAt": "2026-01-01T00:00:00Z",
    }
    body.update(overrides)
    return body


def _rollout_body(
    *,
    rollout_id: str = "rol_1",
    state: str = "ROLLOUT_STATE_RUNNING",
    strategy: str = "ROLLOUT_STRATEGY_TYPE_BLUE_GREEN",
    current_step: int | None = 0,
    current_traffic_percent: int | None = 0,
    total_steps: int = 1,
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": rollout_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "sourceDeploymentId": "dep_source",
        "targetDeploymentId": "dep_target",
        "state": state,
        "strategy": strategy,
        "createdAt": "2026-01-01T00:00:00Z",
        "startedAt": "2026-01-01T00:01:00Z",
        "currentStep": current_step,
        "currentTrafficPercent": current_traffic_percent,
        "etag": "etag-rol",
        "status": {
            "totalSteps": total_steps,
            "steps": [],
        },
    }
    body.update(overrides)
    return body


def _ab_experiment_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "abx_1",
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "control-ab",
        "members": [
            {
                "deploymentId": "dep_source",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
                "percent": 90,
            },
            {
                "deploymentId": "dep_target",
                "role": "AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                "percent": 10,
            },
        ],
        "createdAt": "2026-01-01T00:00:00Z",
        "etag": "etag-ab",
    }
    body.update(overrides)
    return body


def _shadow_experiment_body(
    *,
    experiment_id: str = "exp_1",
    target_deployment_id: str = "dep_target",
    **overrides: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": experiment_id,
        "projectId": "proj",
        "endpointId": "ep_1",
        "name": "shadow-rate-0.1",
        "source": {"endpoint": {"sampling": {"uniform": {"rate": 0.1}}}},
        "targets": [
            {
                "id": "target_1",
                "experimentId": experiment_id,
                "name": "shadow-target",
                "targetDeploymentId": target_deployment_id,
                "createdAt": "2026-01-01T00:00:00Z",
                "etag": "etag-target",
            }
        ],
        "createdAt": "2026-01-01T00:00:00Z",
        "state": "SHADOW_EXPERIMENT_STATE_ACTIVE",
        "etag": "etag-shadow",
    }
    body.update(overrides)
    return body


def _rollout_args(*extra: str) -> list[str]:
    return ["beta", "endpoints", "rollout", "--project", "proj", *extra]


def _mock_active_rollout(respx_mock: MockRouter, *, rollout: dict[str, Any] | None = None) -> dict[str, Any]:
    body = rollout or _rollout_body()
    respx_mock.get("/projects/proj/endpoints/ep_1").mock(
        return_value=httpx.Response(200, json=_endpoint_body(activeRolloutId=body["id"]))
    )
    respx_mock.get(f"/projects/proj/endpoints/ep_1/rollouts/{body['id']}").mock(
        return_value=httpx.Response(200, json=body)
    )
    return body


class TestParseCanarySteps:
    def test_parses_comma_separated_percents(self) -> None:
        assert parse_canary_steps("10,50,100") == [10, 50, 100]

    def test_strips_whitespace(self) -> None:
        assert parse_canary_steps(" 5 , 25 , 100 ") == [5, 25, 100]

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="comma-separated"):
            parse_canary_steps("")

    def test_rejects_non_integer(self) -> None:
        with pytest.raises(ValueError, match="Invalid canary step"):
            parse_canary_steps("10,abc,100")


class TestBuildCanary:
    def test_empty_uses_server_defaults(self) -> None:
        assert build_canary(steps=None, interval=None) == {}

    def test_builds_steps_and_interval(self) -> None:
        assert build_canary(steps="10,50,100", interval="30s") == {
            "steps": [{"traffic": 10}, {"traffic": 50}, {"traffic": 100}],
            "step_interval": "30s",
        }

    def test_converts_human_interval_to_proto_duration(self) -> None:
        assert build_canary(steps=None, interval="10m") == {"step_interval": "600s"}
        assert build_canary(steps=None, interval="10m30s") == {"step_interval": "630s"}
        assert build_canary(steps=None, interval="1h") == {"step_interval": "3600s"}
        assert build_canary(steps=None, interval="180") == {"step_interval": "180s"}

    def test_rejects_unparseable_interval(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            build_canary(steps=None, interval="abc")
        output = capsys.readouterr().out
        assert "--interval must be a duration" in output
        assert "got 'abc'" in output


class TestResolveRolloutStrategy:
    def test_requires_strategy(self) -> None:
        with pytest.raises(ValueError, match="Must specify a rollout strategy"):
            resolve_rollout_strategy(canary=False, blue_green=False, rolling=False, steps=None, interval=None)

    def test_explicit_blue_green(self) -> None:
        canary, blue_green, rolling = resolve_rollout_strategy(
            canary=False, blue_green=True, rolling=False, steps=None, interval=None
        )
        assert canary is None
        assert blue_green == {}
        assert rolling is None

    def test_rolling(self) -> None:
        canary, blue_green, rolling = resolve_rollout_strategy(
            canary=False, blue_green=False, rolling=True, steps=None, interval=None
        )
        assert canary is None
        assert blue_green is None
        assert rolling == {}

    def test_canary(self) -> None:
        canary, blue_green, rolling = resolve_rollout_strategy(
            canary=True, blue_green=False, rolling=False, steps="10,100", interval="1m"
        )
        assert canary == {
            "steps": [{"traffic": 10}, {"traffic": 100}],
            "step_interval": "60s",
        }
        assert blue_green is None
        assert rolling is None


class TestInferActiveSource:
    def test_infers_sole_active(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body())
        assert _infer_active_source(endpoint, target_id="dep_target") == "dep_source"

    def test_infers_source_when_target_also_has_weight(self) -> None:
        endpoint = Endpoint.construct(
            **_endpoint_body(
                trafficSplit=[
                    {"deploymentId": "dep_source", "weight": 0.9},
                    {"deploymentId": "dep_target", "weight": 0.1},
                ]
            )
        )
        assert _infer_active_source(endpoint, target_id="dep_target") == "dep_source"

    def test_rejects_none_active(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body(trafficSplit=[]))
        with pytest.raises(ValueError, match="No active deployment"):
            _infer_active_source(endpoint, target_id="dep_target")

    def test_rejects_multiple_active(self) -> None:
        endpoint = Endpoint.construct(
            **_endpoint_body(
                trafficSplit=[
                    {"deploymentId": "dep_source", "weight": 0.5},
                    {"deploymentId": "dep_other", "weight": 0.3},
                    {"deploymentId": "dep_target", "weight": 0.2},
                ]
            )
        )
        with pytest.raises(ValueError, match="Multiple active deployments"):
            _infer_active_source(endpoint, target_id="dep_target")


class TestVerifyRolloutPair:
    def test_accepts_active_source_inactive_target(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body())
        _verify_rollout_pair(endpoint, source_id="dep_source", target_id="dep_target")

    def test_accepts_target_already_receiving_traffic(self) -> None:
        endpoint = Endpoint.construct(
            **_endpoint_body(
                trafficSplit=[
                    {"deploymentId": "dep_source", "weight": 0.9},
                    {"deploymentId": "dep_target", "weight": 0.1},
                ]
            )
        )
        _verify_rollout_pair(endpoint, source_id="dep_source", target_id="dep_target")

    def test_rejects_same_source_and_target(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body())
        with pytest.raises(ValueError, match="must be different"):
            _verify_rollout_pair(endpoint, source_id="dep_source", target_id="dep_source")

    def test_rejects_missing_source(self) -> None:
        endpoint = Endpoint.construct(**_endpoint_body())
        with pytest.raises(ValueError, match="not on endpoint"):
            _verify_rollout_pair(endpoint, source_id="dep_missing", target_id="dep_target")

    def test_rejects_source_without_traffic(self) -> None:
        endpoint = Endpoint.construct(
            **_endpoint_body(
                trafficSplit=[
                    {"deploymentId": "dep_source", "weight": 0.0},
                    {"deploymentId": "dep_target", "weight": 0.0},
                ]
            )
        )
        with pytest.raises(ValueError, match="not receiving traffic"):
            _verify_rollout_pair(endpoint, source_id="dep_source", target_id="dep_target")


class TestFormatRolloutProgress:
    def test_pending_unset_step(self) -> None:
        rollout = Rollout.construct(**_rollout_body(currentStep=None, currentTrafficPercent=None))
        assert format_rollout_progress(rollout) == ("—", "—")

    def test_displays_one_based_step(self) -> None:
        # current_step is zero-based; blue-green running reports 0 with total_steps=1.
        rollout = Rollout.construct(**_rollout_body(currentStep=0, currentTrafficPercent=0, total_steps=1))
        assert format_rollout_progress(rollout) == ("0%", "1/1")

    def test_canary_mid_progress(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                currentStep=1,
                currentTrafficPercent=50,
                total_steps=3,
            )
        )
        assert format_rollout_progress(rollout) == ("50%", "2/3")

    def test_annotates_failed_current_step(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_CANCELED",
                strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                current_step=1,
                current_traffic_percent=100,
                status={
                    "totalSteps": 2,
                    "steps": [
                        {"stepIndex": 0, "state": "ROLLOUT_STEP_STATE_PASSED", "targetTrafficPercent": 10},
                        {"stepIndex": 1, "state": "ROLLOUT_STEP_STATE_FAILED", "targetTrafficPercent": 100},
                    ],
                },
            )
        )
        assert format_rollout_progress(rollout) == ("100%", "2/2 [red]Failed[/red]")


class TestRolloutReasonDisplay:
    def test_condition_summary_includes_category_message_and_step(self) -> None:
        condition = StatusCondition.construct(
            category="ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
            message="latency p99 breached",
            atStep=1,
        )
        assert format_rollout_condition_summary(condition) == "Metric Regression — latency p99 breached (step 2)"

    def test_regression_metric_line(self) -> None:
        metric = StatusConditionMetric.construct(
            name="request_latency",
            stat="METRIC_STAT_TYPE_PERCENTILE",
            percentile=99,
            check="METRIC_CHECK_TYPE_REGRESSION",
            sourceValue=120.0,
            targetValue=150.0,
            maxRegressionPercent=10.0,
            verdict="METRIC_VERDICT_BREACHED",
        )
        assert format_condition_metric_line(metric) == (
            "request_latency p99: source=120, target=150, max regression 10%  [red]Breached[/red]"
        )

    def test_threshold_metric_line(self) -> None:
        metric = StatusConditionMetric.construct(
            name="error_rate",
            stat="METRIC_STAT_TYPE_AVG",
            check="METRIC_CHECK_TYPE_THRESHOLD",
            targetValue=0.05,
            threshold=0.01,
            operator="THRESHOLD_OPERATOR_LT",
            verdict="METRIC_VERDICT_PASS",
        )
        assert format_condition_metric_line(metric) == (
            "error_rate avg: value=0.05, threshold < 0.01  [green]Pass[/green]"
        )

    def test_metric_line_appends_rule_failure_reason(self) -> None:
        metric = StatusConditionMetric.construct(
            name="router_latency",
            stat="METRIC_STAT_TYPE_PERCENTILE",
            percentile=99,
            check="METRIC_CHECK_TYPE_THRESHOLD",
            targetValue=600.0,
            threshold=500.0,
            operator="THRESHOLD_OPERATOR_LTE",
            verdict="METRIC_VERDICT_BREACHED",
            failureReason="p99 600ms exceeded 500ms",
        )
        assert format_condition_metric_line(metric) == (
            "router_latency p99: value=600, threshold <= 500  [red]Breached[/red] — p99 600ms exceeded 500ms"
        )

    def test_metric_line_omits_stat_when_unmeasured(self) -> None:
        metric = StatusConditionMetric.construct(
            name="router_error_rate",
            check="METRIC_CHECK_TYPE_THRESHOLD",
            verdict="METRIC_VERDICT_UNAVAILABLE",
        )
        assert format_condition_metric_line(metric) == "router_error_rate  [yellow]Unavailable[/yellow]"

    def test_status_step_line_skipped_paused_canceled(self) -> None:
        skipped = StatusStep.construct(
            stepIndex=2,
            state="ROLLOUT_STEP_STATE_SKIPPED",
            targetTrafficPercent=100,
        )
        paused = StatusStep.construct(stepIndex=1, state="ROLLOUT_STEP_STATE_PAUSED", targetTrafficPercent=50)
        canceled = StatusStep.construct(stepIndex=1, state="ROLLOUT_STEP_STATE_CANCELED", targetTrafficPercent=50)
        assert format_status_step_line(skipped) == "3 100% [dim]Skipped[/dim]"
        assert format_status_step_line(paused) == "2 50% [yellow]Paused[/yellow]"
        assert format_status_step_line(canceled) == "2 50% [red]Canceled[/red]"

    def test_reason_rows_surface_condition_metrics_and_distinct_pause_reason(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_SYSTEM_PAUSED",
                strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                status={
                    "totalSteps": 3,
                    "steps": [],
                    "condition": {
                        "category": "ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
                        "message": "latency p99 breached",
                        "atStep": 1,
                        "metrics": [
                            {
                                "name": "request_latency",
                                "stat": "METRIC_STAT_TYPE_PERCENTILE",
                                "percentile": 99,
                                "check": "METRIC_CHECK_TYPE_REGRESSION",
                                "sourceValue": 120.0,
                                "targetValue": 150.0,
                                "maxRegressionPercent": 10.0,
                                "verdict": "METRIC_VERDICT_BREACHED",
                            }
                        ],
                    },
                },
                pauseInfo={"pausedAt": "2026-01-01T00:02:00Z", "reason": "System paused after metric gate failed"},
            )
        )
        assert rollout_reason_rows(rollout) == [
            ("Reason", "Metric Regression — latency p99 breached (step 2)"),
            (
                "Metric",
                "request_latency p99: source=120, target=150, max regression 10%  [red]Breached[/red]",
            ),
            ("Pause reason", "System paused after metric gate failed"),
        ]

    def test_reason_rows_skip_duplicate_pause_reason(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_SYSTEM_PAUSED",
                status={
                    "totalSteps": 3,
                    "steps": [],
                    "condition": {
                        "category": "ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
                        "message": "same message",
                    },
                },
                pauseInfo={"pausedAt": "2026-01-01T00:02:00Z", "reason": "same message"},
            )
        )
        assert rollout_reason_rows(rollout) == [("Reason", "Metric Regression — same message")]

    def test_reason_rows_empty_when_healthy(self) -> None:
        rollout = Rollout.construct(**_rollout_body())
        assert rollout_reason_rows(rollout) == []

    def test_reason_rows_surface_step_failure_reason_and_metrics(self) -> None:
        failure = "metrics-unavailable: serving_latency target: insufficient samples (87 < 100)"
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_CANCELED",
                strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                current_step=1,
                current_traffic_percent=100,
                status={
                    "totalSteps": 2,
                    "steps": [
                        {"stepIndex": 0, "state": "ROLLOUT_STEP_STATE_PASSED", "targetTrafficPercent": 10},
                        {
                            "stepIndex": 1,
                            "state": "ROLLOUT_STEP_STATE_FAILED",
                            "targetTrafficPercent": 100,
                            "failureReason": failure,
                            "metrics": [
                                {
                                    "name": "serving_latency",
                                    "stat": "METRIC_STAT_TYPE_AVG",
                                    "check": "METRIC_CHECK_TYPE_THRESHOLD",
                                    "sourceValue": 80.0,
                                    "targetValue": 95.0,
                                    "threshold": 100.0,
                                    "operator": "THRESHOLD_OPERATOR_LT",
                                    "verdict": "METRIC_VERDICT_UNAVAILABLE",
                                }
                            ],
                        },
                    ],
                },
            )
        )
        assert rollout_reason_rows(rollout) == [
            ("Steps", "1 10% [green]Passed[/green] · 2 100% [red]Failed[/red]"),
            ("Reason", failure),
            (
                "Metric",
                "serving_latency avg: source=80, value=95, threshold < 100  [yellow]Unavailable[/yellow]",
            ),
        ]

    def test_reason_rows_skip_duplicate_step_failure_reason(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_CANCELED",
                status={
                    "totalSteps": 1,
                    "steps": [
                        {
                            "stepIndex": 0,
                            "state": "ROLLOUT_STEP_STATE_FAILED",
                            "failureReason": "latency p99 breached",
                        }
                    ],
                    "condition": {
                        "category": "ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
                        "message": "latency p99 breached",
                    },
                },
            )
        )
        assert rollout_reason_rows(rollout) == [("Reason", "Metric Regression — latency p99 breached")]

    def test_reason_rows_keep_distinct_step_failure_reason(self) -> None:
        rollout = Rollout.construct(
            **_rollout_body(
                state="ROLLOUT_STATE_CANCELED",
                status={
                    "totalSteps": 1,
                    "steps": [
                        {
                            "stepIndex": 0,
                            "state": "ROLLOUT_STEP_STATE_FAILED",
                            "failureReason": "metrics-unavailable: serving_latency target: insufficient samples (87 < 100)",
                        }
                    ],
                    "condition": {
                        "category": "ROLLOUT_FAILURE_CATEGORY_METRICS_UNAVAILABLE",
                        "message": "metric gate could not be evaluated",
                    },
                },
            )
        )
        assert rollout_reason_rows(rollout) == [
            ("Reason", "Metrics Unavailable — metric gate could not be evaluated"),
            (
                "Failure",
                "metrics-unavailable: serving_latency target: insufficient samples (87 < 100)",
            ),
        ]


class TestBetaEndpointsRollout:
    @pytest.mark.respx(base_url=base_url)
    def test_create_blue_green(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        start_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--json"))

        assert result.exit_code == 0, result.output
        assert create_route.called
        assert start_route.called
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["sourceDeploymentId"] == "dep_source"
        assert body["targetDeploymentId"] == "dep_target"
        assert body["blueGreen"] == {}
        assert "canary" not in body
        assert "rolling" not in body
        payload = json.loads(result.out_out)
        assert payload["rollout"]["id"] == "rol_1"

    @pytest.mark.respx(base_url=base_url)
    def test_create_requires_strategy(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("dep_target", "--json"))
        assert result.exit_code != 0
        assert "Must specify a rollout strategy" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_create_canary_with_steps(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(
                    state="ROLLOUT_STATE_PENDING",
                    strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                    currentStep=None,
                    total_steps=3,
                ),
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(strategy="ROLLOUT_STRATEGY_TYPE_CANARY", total_steps=3),
            )
        )

        result = cli_runner.invoke(
            _rollout_args("dep_target", "--canary", "--steps", "10,50,100", "--interval", "30s", "--json")
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["canary"] == {
            "steps": [{"traffic": 10}, {"traffic": 50}, {"traffic": 100}],
            "stepInterval": "30s",
        }

    @pytest.mark.respx(base_url=base_url)
    def test_create_canary_with_threshold_metric(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(
                    state="ROLLOUT_STATE_PENDING",
                    strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                    currentStep=None,
                    total_steps=3,
                ),
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(strategy="ROLLOUT_STRATEGY_TYPE_CANARY", total_steps=3),
            )
        )

        result = cli_runner.invoke(
            _rollout_args(
                "dep_target",
                "--canary",
                "--metric",
                "router_latency",
                "--metric-stat",
                "p99",
                "--metric-threshold",
                "500",
                "--metric-operator",
                "lte",
                "--metric-window",
                "60s",
                "--json",
            )
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["canary"] == {}
        assert body["metrics"] == [
            {
                "name": "router_latency",
                "stat": "METRIC_STAT_TYPE_PERCENTILE",
                "percentile": 99,
                "thresholdCheck": {
                    "operator": "THRESHOLD_OPERATOR_LTE",
                    "value": 500,
                },
                "window": "60s",
            }
        ]

    @pytest.mark.respx(base_url=base_url)
    def test_create_canary_with_regression_metric(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(
                    state="ROLLOUT_STATE_PENDING",
                    strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                    currentStep=None,
                    total_steps=3,
                ),
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(strategy="ROLLOUT_STRATEGY_TYPE_CANARY", total_steps=3),
            )
        )

        result = cli_runner.invoke(
            _rollout_args(
                "dep_target",
                "--canary",
                "--metric",
                "router_error_rate",
                "--metric-stat",
                "avg",
                "--metric-max-regression",
                "10",
                "--metric-direction",
                "higher-is-worse",
                "--json",
            )
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["metrics"] == [
            {
                "name": "router_error_rate",
                "stat": "METRIC_STAT_TYPE_AVG",
                "regressionCheck": {
                    "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                    "maxRegressionPercent": 10,
                },
            }
        ]

    @pytest.mark.respx(base_url=base_url)
    def test_create_canary_omits_optional_stat_and_regression_budget(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(
                    state="ROLLOUT_STATE_PENDING",
                    strategy="ROLLOUT_STRATEGY_TYPE_CANARY",
                    currentStep=None,
                    total_steps=3,
                ),
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(strategy="ROLLOUT_STRATEGY_TYPE_CANARY", total_steps=3),
            )
        )

        result = cli_runner.invoke(
            _rollout_args(
                "dep_target",
                "--canary",
                "--metric",
                "router_error_rate",
                "--metric-direction",
                "higher-is-worse",
                "--json",
            )
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["metrics"] == [
            {
                "name": "router_error_rate",
                "regressionCheck": {
                    "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                },
            }
        ]

    @pytest.mark.respx(base_url=base_url)
    def test_create_detaches_ab_member_with_zero_share(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        endpoint = _endpoint_body()
        for deployment in endpoint["deployments"]:
            if deployment["id"] == "dep_target":
                deployment["estimatedEffectiveTrafficShare"] = 0.0
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        delete_ab = respx_mock.delete("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(200, json={"id": "abx_1"})
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--detach", "--json"))

        assert result.exit_code == 0, result.output
        assert delete_ab.called
        assert create_route.called
        payload = json.loads(result.out_out)
        assert any("deleted A/B experiment" in action for action in payload["actions"])

    @pytest.mark.respx(base_url=base_url)
    def test_create_start_failure_reports_irreversible_actions(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        endpoint = _endpoint_body()
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_ab_experiment_body()], "next_cursor": None},
            )
        )
        respx_mock.delete("/projects/proj/endpoints/ep_1/abExperiments/abx_1").mock(
            return_value=httpx.Response(200, json={"id": "abx_1"})
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                400,
                json={"error": {"message": "cannot start rollout", "type": "invalid_request_error"}},
            )
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--detach", "--json"))

        assert result.exit_code != 0
        payload = json.loads(result.out_out)
        assert payload["id"] == "rol_1"
        assert payload["type"] == "rollout"
        assert payload["command"] == "tg beta endpoints rm rol_1"
        assert "deleted A/B experiment abx_1" in payload["actions"]
        assert "rol_1" in payload["hint"]
        assert "tg beta endpoints rm rol_1" in payload["hint"]

    @pytest.mark.respx(base_url=base_url)
    def test_create_start_failure_reports_orphan_rollout_without_detach(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        endpoint = _endpoint_body()
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(
                400,
                json={"error": {"message": "cannot start rollout", "type": "invalid_request_error"}},
            )
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green"))

        assert result.exit_code != 0
        assert "Created rollout rol_1 but failed to start it" in result.output
        assert "Clean up with: tg beta endpoints rm rol_1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_create_with_explicit_source(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # Ambiguous traffic split — explicit --source selects via resolve_deployment_ids.
        endpoint = _endpoint_body(
            trafficSplit=[
                {"deploymentId": "dep_source", "weight": 0.7},
                {"deploymentId": "dep_other", "weight": 0.3},
                {"deploymentId": "dep_target", "weight": 0.0},
            ],
            deployments=[
                _deployment_summary("dep_source", estimated_effective_traffic_share=0.7),
                _deployment_summary("dep_other", estimated_effective_traffic_share=0.3),
                _deployment_summary("dep_target", estimated_effective_traffic_share=0.0),
            ],
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--source", "dep_source", "--json"))

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["sourceDeploymentId"] == "dep_source"
        assert body["targetDeploymentId"] == "dep_target"

    @pytest.mark.respx(base_url=base_url)
    def test_create_infers_source_when_target_already_has_weight(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        endpoint = _endpoint_body(
            trafficSplit=[
                {"deploymentId": "dep_source", "weight": 0.9},
                {"deploymentId": "dep_target", "weight": 0.1},
            ],
            deployments=[
                _deployment_summary("dep_source", estimated_effective_traffic_share=0.9),
                _deployment_summary("dep_target", estimated_effective_traffic_share=0.1),
            ],
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--json"))

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["sourceDeploymentId"] == "dep_source"
        assert body["targetDeploymentId"] == "dep_target"

    @pytest.mark.respx(base_url=base_url)
    def test_create_rejects_cross_endpoint_source(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        other = _endpoint_body(
            id="ep_2",
            name="my-project/other-endpoint",
            trafficSplit=[{"deploymentId": "dep_foreign", "weight": 1.0}],
            deployments=[_deployment_summary("dep_foreign", estimated_effective_traffic_share=1.0)],
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body(), other], "next_cursor": None},
            )
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--source", "dep_foreign", "--json"))

        assert result.exit_code != 0
        assert "Source deployment dep_foreign is on endpoint ep_2" in result.output
        assert "target deployment dep_target is on endpoint ep_1" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_create_passes_final_target_replicas(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(
            _rollout_args("dep_target", "--blue-green", "--final-target-replicas", "4", "--json")
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["finalTargetReplicas"] == 4

    @pytest.mark.respx(base_url=base_url)
    def test_create_passes_final_source_replicas(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [_endpoint_body()], "next_cursor": None},
            )
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(
            _rollout_args("dep_target", "--blue-green", "--final-source-replicas", "2", "--json")
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, create_route.calls[0]).request.content.decode())
        assert body["finalSourceReplicas"] == 2

    @pytest.mark.respx(base_url=base_url)
    def test_create_detaches_shadow_target(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # Server may mis-label shadow deployments as LIVE; membership is authoritative.
        endpoint = _endpoint_body(
            deployments=[
                _deployment_summary("dep_source", estimated_effective_traffic_share=1.0),
                _deployment_summary(
                    "dep_target",
                    traffic_mode="TRAFFIC_MODE_LIVE",
                    estimated_effective_traffic_share=0.0,
                ),
            ]
        )
        respx_mock.get("/projects/proj/endpoints").mock(
            return_value=httpx.Response(
                200,
                json={"object": "list", "data": [endpoint], "next_cursor": None},
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/shadowExperiments").mock(
            return_value=httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [_shadow_experiment_body(target_deployment_id="dep_target")],
                    "next_cursor": None,
                },
            )
        )
        respx_mock.get("/projects/proj/endpoints/ep_1/abExperiments").mock(
            return_value=httpx.Response(200, json={"object": "list", "data": [], "next_cursor": None})
        )
        delete_target = respx_mock.delete(
            "/projects/proj/endpoints/ep_1/shadowExperiments/exp_1/targets/target_1"
        ).mock(return_value=httpx.Response(200, json={"id": "target_1"}))
        delete_shadow = respx_mock.delete("/projects/proj/endpoints/ep_1/shadowExperiments/exp_1").mock(
            return_value=httpx.Response(200, json={"id": "exp_1"})
        )
        create_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_PENDING", currentStep=None))
        )
        respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/start").mock(
            return_value=httpx.Response(200, json=_rollout_body())
        )

        result = cli_runner.invoke(_rollout_args("dep_target", "--blue-green", "--detach", "--json"))

        assert result.exit_code == 0, result.output
        assert delete_target.called
        assert delete_shadow.called
        assert create_route.called
        payload = json.loads(result.out_out)
        assert any("deleted empty shadow experiment" in action for action in payload["actions"])

    @pytest.mark.respx(base_url=base_url)
    def test_cancel_by_endpoint_id(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_active_rollout(respx_mock)
        cancel_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/cancel").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_CANCELED"))
        )

        result = cli_runner.invoke(_rollout_args("ep_1", "--cancel", "--reason", "ship reverted", "--json"))

        assert result.exit_code == 0, result.output
        assert cancel_route.called
        body = json.loads(cast(Call, cancel_route.calls[0]).request.content.decode())
        assert body["reason"] == "ship reverted"
        payload = json.loads(result.out_out)
        assert payload["rollout"]["state"] == "ROLLOUT_STATE_CANCELED"

    @pytest.mark.respx(base_url=base_url)
    def test_resume_by_endpoint_id(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_active_rollout(respx_mock, rollout=_rollout_body(state="ROLLOUT_STATE_PAUSED"))
        resume_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/resume").mock(
            return_value=httpx.Response(200, json=_rollout_body(state="ROLLOUT_STATE_RUNNING"))
        )

        result = cli_runner.invoke(_rollout_args("ep_1", "--resume", "--json"))

        assert result.exit_code == 0, result.output
        assert resume_route.called
        payload = json.loads(result.out_out)
        assert payload["rollout"]["state"] == "ROLLOUT_STATE_RUNNING"

    @pytest.mark.respx(base_url=base_url)
    def test_promote_by_endpoint_id(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        _mock_active_rollout(respx_mock)
        promote_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_1/promote").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(
                    state="ROLLOUT_STATE_COMPLETED",
                    current_step=0,
                    current_traffic_percent=100,
                ),
            )
        )

        result = cli_runner.invoke(_rollout_args("ep_1", "--promote", "--json"))

        assert result.exit_code == 0, result.output
        assert promote_route.called
        payload = json.loads(result.out_out)
        assert payload["rollout"]["state"] == "ROLLOUT_STATE_COMPLETED"

    @pytest.mark.respx(base_url=base_url)
    def test_pause_falls_back_when_active_rollout_id_missing(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        # List/retrieve omit activeRolloutId; fallback picks newest non-terminal.
        # Newer COMPLETED must lose to older PAUSED (client-side state filter).
        # filter=ROLLOUT_FILTER_ACTIVE is omitted — that filter can drop paused.
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))

        def list_rollouts(request: httpx.Request) -> httpx.Response:
            assert "filter" not in request.url.params
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _rollout_body(
                            rollout_id="rol_paused",
                            state="ROLLOUT_STATE_PAUSED",
                            createdAt="2026-01-02T00:00:00Z",
                        ),
                        _rollout_body(
                            rollout_id="rol_done",
                            state="ROLLOUT_STATE_COMPLETED",
                            createdAt="2026-01-03T00:00:00Z",
                        ),
                    ],
                    "next_cursor": None,
                },
            )

        list_route = respx_mock.get("/projects/proj/endpoints/ep_1/rollouts").mock(side_effect=list_rollouts)
        pause_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_paused/pause").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(rollout_id="rol_paused", state="ROLLOUT_STATE_PAUSED"),
            )
        )

        result = cli_runner.invoke(_rollout_args("ep_1", "--pause", "--json"))

        assert result.exit_code == 0, result.output
        assert list_route.called
        assert pause_route.called

    @pytest.mark.respx(base_url=base_url)
    def test_resume_falls_back_to_paused_when_active_rollout_id_missing(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
    ) -> None:
        respx_mock.get("/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=_endpoint_body()))

        def list_rollouts(request: httpx.Request) -> httpx.Response:
            # Server ACTIVE filter would omit paused — CLI must not send it.
            assert "filter" not in request.url.params
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        _rollout_body(
                            rollout_id="rol_paused",
                            state="ROLLOUT_STATE_PAUSED",
                            createdAt="2026-01-02T00:00:00Z",
                        ),
                        _rollout_body(
                            rollout_id="rol_done",
                            state="ROLLOUT_STATE_COMPLETED",
                            createdAt="2026-01-03T00:00:00Z",
                        ),
                    ],
                    "next_cursor": None,
                },
            )

        respx_mock.get("/projects/proj/endpoints/ep_1/rollouts").mock(side_effect=list_rollouts)
        resume_route = respx_mock.post("/projects/proj/endpoints/ep_1/rollouts/rol_paused/resume").mock(
            return_value=httpx.Response(
                200,
                json=_rollout_body(rollout_id="rol_paused", state="ROLLOUT_STATE_RUNNING"),
            )
        )

        result = cli_runner.invoke(_rollout_args("ep_1", "--resume", "--json"))

        assert result.exit_code == 0, result.output
        assert resume_route.called

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_strategy_with_control_flag(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("dep_target", "--canary", "--cancel"))
        assert result.exit_code != 0
        assert "cannot be combined" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_mutually_exclusive_controls(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("ep_1", "--cancel", "--pause"))
        assert result.exit_code != 0
        assert "Mutually exclusive" in result.output
        assert "--cancel" in result.output
        assert "--pause" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_mutually_exclusive_strategies(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("dep_target", "--canary", "--rolling"))
        assert result.exit_code != 0
        assert "Mutually exclusive" in result.output
        assert "--canary" in result.output
        assert "--rolling" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_steps_without_canary(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("dep_target", "--steps", "10,100"))
        assert result.exit_code != 0
        assert "require --canary" in result.output.replace("\n", " ")

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_metric_without_canary(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(
            _rollout_args(
                "dep_target",
                "--metric",
                "router_latency",
                "--metric-stat",
                "p99",
                "--metric-threshold",
                "500",
                "--metric-operator",
                "lte",
            )
        )
        assert result.exit_code != 0
        assert "require --canary" in result.output.replace("\n", " ")

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_incomplete_metric_gate(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(
            _rollout_args("dep_target", "--canary", "--metric", "router_latency", "--metric-stat", "p99")
        )
        assert result.exit_code != 0
        assert "requires either --metric-operator" in result.output.replace("\n", " ")

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_reason_without_cancel_or_pause(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(_rollout_args("dep_target", "--reason", "nope"))
        assert result.exit_code != 0
        assert "--reason is only valid with --cancel or --pause" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_rejects_retired_min_max_metric_stat(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(
            _rollout_args(
                "dep_target",
                "--canary",
                "--metric",
                "router_error_rate",
                "--metric-stat",
                "min",
                "--metric-operator",
                "lte",
            )
        )
        assert result.exit_code != 0
        output = result.output.replace("\n", " ")
        assert "--metric-stat" in output
        assert "min" in output
