from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner
from together.lib.cli.api.endpoints.metrics import (
    DEFAULT_METRICS_URL,
    RequestRateSample,
    estimated_requests,
    metrics_request_url,
    parse_request_rate_line,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

# Tests point the command at the mocked API host so one respx router serves both.
_METRICS_URL = f"{base_url}/metrics-service"
_METRICS_PATH = "/metrics-service/organizations/org-1/metrics"


def _endpoint_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "ep_1",
        "projectId": "proj",
        "name": "my-project/my-endpoint",
        "endpointType": "ENDPOINT_TYPE_DEDICATED",
        "etag": "etag-1",
        "visibility": "VISIBILITY_PRIVATE",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "trafficSplit": [{"deploymentId": "dep_live", "weight": 1.0}],
        "deployments": [_deployment_summary("dep_live", "live"), _deployment_summary("dep_shadow", "shadow")],
    }
    body.update(overrides)
    return body


def _deployment_summary(deployment_id: str, name: str) -> dict[str, Any]:
    return {
        "id": deployment_id,
        "name": name,
        "model": "projects/proj/models/ml_1/revisions/latest",
        "modelId": "ml_1",
        "hardware": "1x-h100",
        "state": "DEPLOYMENT_STATE_READY",
        "readyReplicas": 1,
        "desiredReplicas": 1,
        "createdAt": "2026-01-01T00:00:00Z",
        "autoscaling": {"minReplicas": 1, "maxReplicas": 1},
    }


def _whoami_body() -> dict[str, Any]:
    return {
        "type": "project_api_key",
        "api_key": {"id": "key-1"},
        "organization": {"id": "org-1", "name": "Acme"},
        "project": {"id": "proj", "name": "My Project", "slug": "my-project"},
    }


def _series(
    rate: float,
    *,
    deployment_id: str = "dep_live",
    endpoint_id: str = "ep_1",
    status_code: str = "200",
    path: str = "/v1/chat/completions",
    replica_id: str = "replica-a",
    metric: str = "router_inference_requests_rate5m",
) -> str:
    return (
        f'{metric}{{availability_zone="us-east-1a",deployment_id="{deployment_id}",'
        f'endpoint_id="{endpoint_id}",owner_organization_id="org-1",path="{path}",'
        f'replica_id="{replica_id}",status_code="{status_code}"}} {rate} 1795014571641'
    )


# 0.1 requests per second is 30 requests in the 5-minute window.
_METRICS_TEXT = "\n".join(
    [
        "# TYPE edge_inference_inflight_requests gauge",
        'edge_inference_inflight_requests{deployment_id="dep_live",endpoint_id="ep_1"} 4 1795014571641',
        "# TYPE router_inference_requests_rate5m gauge",
        _series(0.1, replica_id="replica-a"),
        _series(0.2, replica_id="replica-b"),
        _series(0.01, status_code="429"),
        _series(0.05, path="/v1/messages/{id}"),
        _series(0.02, deployment_id="dep_shadow"),
        # Health checks and other endpoints must not be counted.
        _series(1.0, path="/workers"),
        _series(0.5, path="/readiness"),
        _series(0.5, path="/liveness"),
        _series(9.0, endpoint_id="ep_other", deployment_id="dep_other"),
        # A different metric that shares the name as a prefix.
        _series(7.0, metric="router_inference_requests_rate5m_other"),
        "",
    ]
)


def _mock_api(respx_mock: MockRouter, **endpoint_overrides: Any) -> None:
    endpoint = _endpoint_body(**endpoint_overrides)
    respx_mock.get("/v3/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
    respx_mock.get("/v2/projects/proj/endpoints/ep_1").mock(return_value=httpx.Response(200, json=endpoint))
    respx_mock.get("/v2/projects/proj/endpoints").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": [endpoint], "next_cursor": None})
    )


def _metrics_args(*extra: str) -> list[str]:
    return ["endpoints", "metrics", "--project", "proj", "--metrics-url", _METRICS_URL, *extra]


class TestParseRequestRateLine:
    def test_parses_labels_rate_and_timestamp(self) -> None:
        assert parse_request_rate_line(_series(0.25, status_code="400")) == RequestRateSample(
            endpoint_id="ep_1",
            deployment_id="dep_live",
            status_code="400",
            path="/v1/chat/completions",
            rate=0.25,
            timestamp_ms=1795014571641,
        )

    def test_path_label_can_contain_a_brace(self) -> None:
        sample = parse_request_rate_line(_series(0.5, path="/v1/messages/{id}"))

        assert sample is not None
        assert sample.path == "/v1/messages/{id}"
        assert sample.rate == 0.5

    def test_timestamp_is_optional(self) -> None:
        line = 'router_inference_requests_rate5m{deployment_id="dep_live",endpoint_id="ep_1",status_code="200"} 2'

        sample = parse_request_rate_line(line)

        assert sample is not None
        assert sample.rate == 2.0
        assert sample.timestamp_ms is None

    @pytest.mark.parametrize(
        "line",
        [
            "",
            "# TYPE router_inference_requests_rate5m gauge",
            _series(1.0, metric="router_inference_requests_total"),
            _series(1.0, metric="router_inference_requests_rate5m_other"),
            'router_inference_requests_rate5m{endpoint_id="ep_1",status_code="200"} 1',
            'router_inference_requests_rate5m{deployment_id="dep_live",status_code="200"} 1',
            'router_inference_requests_rate5m{deployment_id="dep_live",endpoint_id="ep_1"} NaN',
            'router_inference_requests_rate5m{deployment_id="dep_live",endpoint_id="ep_1"} +Inf',
            'router_inference_requests_rate5m{deployment_id="dep_live",endpoint_id="ep_1"} not-a-number',
            'router_inference_requests_rate5m{deployment_id="dep_live",endpoint_id="ep_1"}',
        ],
    )
    def test_ignores_lines_it_cannot_use(self, line: str) -> None:
        assert parse_request_rate_line(line) is None


def test_estimated_requests_is_rate_times_the_window() -> None:
    assert estimated_requests(0.1) == pytest.approx(30)


def test_metrics_request_url_tolerates_a_trailing_slash() -> None:
    assert (
        metrics_request_url("https://metrics.example/", "org-1")
        == "https://metrics.example/organizations/org-1/metrics"
    )


class TestEndpointsMetrics:
    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_reports_requests_per_deployment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        route = respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=_METRICS_TEXT))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["object"] == "endpoint.request_metrics"
        assert payload["endpoint_id"] == "ep_1"
        assert payload["metric"] == "router_inference_requests_rate5m"
        assert payload["window_seconds"] == 300
        assert payload["sampled_at"] == "2026-11-18T15:09:31.641000+00:00"
        assert payload["estimated_requests"] == pytest.approx(114)
        assert "message" not in payload

        live, shadow = payload["deployments"]
        assert live["deployment_id"] == "dep_live"
        assert live["deployment_name"] == "live"
        # Two replicas and two inference paths add up. Health checks, the other
        # endpoint, and the other metric do not.
        assert live["requests_per_second"] == pytest.approx(0.36)
        assert live["estimated_requests"] == pytest.approx(108)
        assert list(live["status_codes"]) == ["200", "429"]
        assert live["status_codes"]["200"]["estimated_requests"] == pytest.approx(105)
        assert live["status_codes"]["429"]["estimated_requests"] == pytest.approx(3)
        assert shadow["deployment_id"] == "dep_shadow"
        assert shadow["estimated_requests"] == pytest.approx(6)

        request = cast(Call, route.calls[0]).request
        assert request.url.params["match[]"] == "router_inference_requests_rate5m"
        assert request.headers["authorization"].startswith("Bearer ")

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_deployment_id_reports_only_that_deployment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=_METRICS_TEXT))

        result = cli_runner.invoke(_metrics_args("dep_shadow", "--json"))

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["endpoint_id"] == "ep_1"
        assert [entry["deployment_id"] for entry in payload["deployments"]] == ["dep_shadow"]
        assert payload["estimated_requests"] == pytest.approx(6)

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_endpoint_name_resolves(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=_METRICS_TEXT))

        result = cli_runner.invoke(_metrics_args("my-endpoint", "--json"))

        assert result.exit_code == 0, result.output
        assert json.loads(result.out_out)["endpoint_id"] == "ep_1"

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_unknown_name_says_what_to_run(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)

        result = cli_runner.invoke(_metrics_args("no-such-thing", "--json"))

        assert result.exit_code == 1
        error = json.loads(result.out_out)["error"]
        assert "No endpoint or deployment named no-such-thing was found" in error
        assert "tg endpoints ls" in error

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_series_for_a_deleted_deployment_are_kept(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock, deployments=[_deployment_summary("dep_live", "live")])
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=_METRICS_TEXT))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 0, result.output
        deployments = {entry["deployment_id"]: entry for entry in json.loads(result.out_out)["deployments"]}
        assert deployments["dep_shadow"]["deployment_name"] is None
        assert deployments["dep_shadow"]["estimated_requests"] == pytest.approx(6)

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_table_output(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=_METRICS_TEXT))

        result = cli_runner.invoke(_metrics_args("ep_1"))

        output = " ".join(result.output.split())
        assert result.exit_code == 0, result.output
        assert "my-endpoint (ep_1)" in output
        assert "dep_live" in output
        assert "dep_shadow" in output
        assert "200: 105" in output
        assert "429: 3" in output
        assert "108" in output
        assert "Beta. Counts are estimates" in output

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_no_requests_explains_the_window(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        other_endpoint_only = _series(9.0, endpoint_id="ep_other", deployment_id="dep_other")
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=other_endpoint_only + "\n"))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 0, result.output
        payload = json.loads(result.out_out)
        assert payload["estimated_requests"] == 0
        assert payload["sampled_at"] is None
        assert [entry["estimated_requests"] for entry in payload["deployments"]] == [0, 0]
        assert "No inference requests were recorded for ep_1 in the last 5 minutes" in payload["message"]
        assert "send requests and run this command again" in payload["message"]

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_no_requests_table_output(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        other_endpoint_only = _series(9.0, endpoint_id="ep_other", deployment_id="dep_other")
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=other_endpoint_only + "\n"))

        result = cli_runner.invoke(_metrics_args("dep_shadow"))

        output = " ".join(result.output.split())
        assert result.exit_code == 0, result.output
        assert "No inference requests were recorded for dep_shadow in the last 5 minutes" in output

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_empty_response_points_at_the_docs(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(200, text=""))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 0, result.output
        message = json.loads(result.out_out)["message"]
        assert "returned no router_inference_requests_rate5m series for this organization" in message
        assert "https://docs.together.ai/docs/dedicated-endpoints/monitoring" in message

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    @pytest.mark.parametrize(
        ("status_code", "body", "expected"),
        [
            (401, "authentication failed", ["HTTP 401", "TOGETHER_API_KEY", "--api-key"]),
            (403, "Forbidden", ["HTTP 403", "organization org-1", "access may need to be enabled"]),
            (404, "", ["HTTP 404", "host or path may have changed", "--metrics-url", "TOGETHER_METRICS_URL"]),
            (503, "upstream connect error", ["HTTP 503: upstream connect error", "Try again in a minute"]),
        ],
    )
    def test_error_statuses_say_what_to_do(
        self,
        respx_mock: MockRouter,
        cli_runner: CliRunner,
        status_code: int,
        body: str,
        expected: list[str],
    ) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(status_code, text=body))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 1
        error = json.loads(result.out_out)["error"]
        for text in expected:
            assert text in error

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_error_status_in_text_mode(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(return_value=httpx.Response(403, text="Forbidden"))

        result = cli_runner.invoke(_metrics_args("ep_1"))

        output = " ".join(result.output.split())
        assert result.exit_code == 1
        assert "Error: The metrics service refused access to organization org-1 (HTTP 403)." in output

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_unreachable_host_names_the_override(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        respx_mock.get(_METRICS_PATH).mock(side_effect=httpx.ConnectError("no route to host"))

        result = cli_runner.invoke(_metrics_args("ep_1", "--json"))

        assert result.exit_code == 1
        error = json.loads(result.out_out)["error"]
        assert "Could not read from the metrics service" in error
        assert "ConnectError: no route to host" in error
        assert "--metrics-url" in error

    @pytest.mark.respx(base_url=base_url, assert_all_called=False)
    def test_metrics_url_can_come_from_the_environment(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        _mock_api(respx_mock)
        route = respx_mock.get("/from-env/organizations/org-1/metrics").mock(
            return_value=httpx.Response(200, text=_METRICS_TEXT)
        )
        cli_runner.env["TOGETHER_METRICS_URL"] = f"{base_url}/from-env/"

        result = cli_runner.invoke(["endpoints", "metrics", "--project", "proj", "ep_1", "--json"])

        assert result.exit_code == 0, result.output
        assert route.call_count == 1

    @pytest.mark.respx(assert_all_mocked=True)
    def test_default_metrics_host(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get(f"{base_url}/v3/whoami").mock(return_value=httpx.Response(200, json=_whoami_body()))
        respx_mock.get(f"{base_url}/v2/projects/proj/endpoints/ep_1").mock(
            return_value=httpx.Response(200, json=_endpoint_body())
        )
        route = respx_mock.get(f"{DEFAULT_METRICS_URL}/organizations/org-1/metrics").mock(
            return_value=httpx.Response(200, text=_METRICS_TEXT)
        )

        result = cli_runner.invoke(["endpoints", "metrics", "--project", "proj", "ep_1", "--json"])

        assert result.exit_code == 0, result.output
        assert route.call_count == 1
        assert DEFAULT_METRICS_URL == "https://o11y-de2-metrics.cloud.together.ai"


class TestEndpointsMetricsHelp:
    @pytest.mark.usefixtures("plain_cli_help")
    def test_metrics_help_says_beta_and_links_the_docs(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["endpoints", "metrics", "--help"])

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "(beta)" in output
        assert "--metrics-url" in output
        assert "TOGETHER_METRICS_URL" in output
        assert "https://docs.together.ai/docs/dedicated-endpoints/monitoring" in output

    @pytest.mark.usefixtures("plain_cli_help")
    def test_endpoints_help_lists_metrics(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["endpoints", "--help"])

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "metrics: Show how many requests each deployment received" in output
        assert "tg endpoints metrics <endpoint-or-deployment-name-or-id>" in output

    @pytest.mark.usefixtures("plain_cli_help")
    def test_shadow_help_shows_how_to_verify_mirrored_traffic(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(["endpoints", "shadow", "--help"])

        output = " ".join(result.output.split())
        assert result.exit_code == 0
        assert "Verify mirrored traffic reaches the shadow target" in output
        assert "tg endpoints metrics <shadow-target-deployment-id>" in output
