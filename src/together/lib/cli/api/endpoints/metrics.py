from __future__ import annotations

import re
import math
from typing import Dict, List, NoReturn, Optional, Annotated, AsyncIterator
from datetime import datetime, timezone
from dataclasses import field, dataclass

import httpx
from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together.types import Endpoint
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._whoami import organization_of
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.utils._json_mode import emit_json, exit_with_message
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils._resolve_model import resolve_endpoint
from together.lib.cli.api.endpoints._utils._find_endpoint_by_deployment import (
    AmbiguousDeploymentError,
    resolve_deployment_id,
)

# The metrics service is in beta: it lives on its own host, and both the host and
# the path may change. Keep the host overridable so a move does not need a release.
DEFAULT_METRICS_URL = "https://o11y-de2-metrics.cloud.together.ai"
METRICS_URL_ENV_VAR = "TOGETHER_METRICS_URL"
METRICS_DOCS_URL = "https://docs.together.ai/docs/dedicated-endpoints/monitoring"

# A gauge holding the per-second request rate over the last 5 minutes, with one
# series per replica, status code, and request path.
REQUEST_RATE_METRIC = "router_inference_requests_rate5m"
RATE_WINDOW_SECONDS = 300

# The router answers its own health probes on these paths. They are not inference
# requests, and counting them would report traffic on a deployment that has none.
HEALTH_CHECK_PATHS = frozenset({"/readiness", "/liveness", "/workers"})

_LABEL_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)="((?:[^"\\]|\\.)*)"')

MetricsUrlParameter = Annotated[
    Optional[str],
    Parameter(
        name="--metrics-url",
        env_var=METRICS_URL_ENV_VAR,
        help=(
            "Base URL of the metrics service. The service is in beta and its host may change. "
            f"Defaults to {DEFAULT_METRICS_URL}."
        ),
    ),
]


class MetricsRequestError(Exception):
    """The metrics service answered with something other than 200."""

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code
        self.body = body


@dataclass
class RequestRateSample:
    endpoint_id: str
    deployment_id: str
    status_code: str
    path: str
    rate: float
    timestamp_ms: Optional[int] = None


@dataclass
class DeploymentRequestRates:
    deployment_id: str
    deployment_name: Optional[str] = None
    by_status_code: Dict[str, float] = field(default_factory=lambda: {})

    @property
    def rate(self) -> float:
        return sum(self.by_status_code.values(), 0.0)


def parse_request_rate_line(line: str) -> RequestRateSample | None:
    """Parse one line of Prometheus text into a request-rate sample.

    Returns None for comments, other metrics, and lines this command cannot use.
    """
    if not line.startswith(REQUEST_RATE_METRIC + "{"):
        return None
    # A label value can contain a brace, such as path="/v1/messages/{id}", so the
    # label set ends at the last one on the line.
    labels_end = line.rfind("}")
    if labels_end == -1:
        return None
    labels = dict(_LABEL_RE.findall(line[len(REQUEST_RATE_METRIC) + 1 : labels_end]))
    values = line[labels_end + 1 :].split()
    if not values:
        return None
    try:
        rate = float(values[0])
    except ValueError:
        return None
    if not math.isfinite(rate):
        return None

    endpoint_id = labels.get("endpoint_id")
    deployment_id = labels.get("deployment_id")
    if not endpoint_id or not deployment_id:
        return None

    timestamp_ms: Optional[int] = None
    if len(values) > 1:
        try:
            timestamp_ms = int(values[1])
        except ValueError:
            timestamp_ms = None

    return RequestRateSample(
        endpoint_id=endpoint_id,
        deployment_id=deployment_id,
        status_code=labels.get("status_code", "unknown"),
        path=labels.get("path", ""),
        rate=rate,
        timestamp_ms=timestamp_ms,
    )


def metrics_request_url(base_url: str, organization_id: str) -> str:
    return f"{base_url.rstrip('/')}/organizations/{organization_id}/metrics"


async def _stream_request_rate_samples(config: CLIConfig, url: str) -> AsyncIterator[RequestRateSample]:
    """Yield request-rate samples from the metrics service.

    A full response holds every metric for every endpoint in the organization and
    can run to hundreds of megabytes. Ask for the one metric this command reads,
    and still filter line by line in case the service ignores the selector.
    """
    # Send through the CLI's HTTP client so --debug, --timeout, and the missing
    # API key message behave the same as for every other command.
    http_client = config.client._client
    async with http_client.stream(
        "GET",
        url,
        params={"match[]": REQUEST_RATE_METRIC},
        headers={"Authorization": f"Bearer {config.client.api_key}", "Accept": "text/plain"},
    ) as response:
        if response.status_code != 200:
            body = (await response.aread()).decode("utf-8", errors="replace").strip()
            raise MetricsRequestError(response.status_code, body)
        async for line in response.aiter_lines():
            sample = parse_request_rate_line(line)
            if sample is not None:
                yield sample


@dataclass
class _RequestRateReport:
    deployments: List[DeploymentRequestRates]
    # False when the response held no request-rate series for any endpoint.
    organization_has_series: bool
    sampled_at_ms: Optional[int]


async def _load_request_rates(
    config: CLIConfig,
    url: str,
    *,
    endpoint: Endpoint,
    deployment_id: str | None,
) -> _RequestRateReport:
    rates: Dict[str, DeploymentRequestRates] = {}
    for deployment in endpoint.deployments or []:
        if deployment_id is None or deployment.id == deployment_id:
            rates[deployment.id] = DeploymentRequestRates(deployment.id, _short_name(deployment.name))
    if deployment_id is not None and deployment_id not in rates:
        rates[deployment_id] = DeploymentRequestRates(deployment_id)

    organization_has_series = False
    sampled_at_ms: Optional[int] = None
    async for sample in _stream_request_rate_samples(config, url):
        organization_has_series = True
        if sample.endpoint_id != endpoint.id or sample.path in HEALTH_CHECK_PATHS:
            continue
        if deployment_id is not None and sample.deployment_id != deployment_id:
            continue
        # A deployment deleted in the last few minutes still has series, so it
        # will not be in the endpoint's deployment list.
        entry = rates.setdefault(sample.deployment_id, DeploymentRequestRates(sample.deployment_id))
        entry.by_status_code[sample.status_code] = entry.by_status_code.get(sample.status_code, 0.0) + sample.rate
        if sample.timestamp_ms is not None and (sampled_at_ms is None or sample.timestamp_ms > sampled_at_ms):
            sampled_at_ms = sample.timestamp_ms

    return _RequestRateReport(
        deployments=list(rates.values()),
        organization_has_series=organization_has_series,
        sampled_at_ms=sampled_at_ms,
    )


def _short_name(fully_qualified_name: str | None) -> str | None:
    if not fully_qualified_name:
        return None
    return fully_qualified_name.rsplit("/", 1)[-1]


def estimated_requests(rate: float) -> float:
    """Requests in the rate window: the per-second rate times the seconds it covers."""
    return rate * RATE_WINDOW_SECONDS


def _format_count(value: float) -> str:
    return f"{round(value):,}"


def _format_rate(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.4f}" if value < 10 else f"{value:,.2f}"


def _status_code_sort_key(status_code: str) -> tuple[int, str]:
    return (int(status_code), "") if status_code.isdigit() else (1000, status_code)


def _no_requests_message(*, target_id: str, organization_has_series: bool) -> str:
    if not organization_has_series:
        return (
            f"The metrics service returned no {REQUEST_RATE_METRIC} series for this organization. "
            "Either no dedicated endpoint received a request in the last 5 minutes, or the metric was renamed "
            f"(the service is in beta). See {METRICS_DOCS_URL} for the current metric names."
        )
    return (
        f"No inference requests were recorded for {target_id} in the last 5 minutes. "
        "The count covers only that window, so send requests and run this command again. "
        "A stopped deployment reports nothing."
    )


def _fail_for_status(error: MetricsRequestError, *, url: str, organization_id: str) -> NoReturn:
    status = error.status_code
    if status == 401:
        message = (
            "The metrics service rejected these credentials (HTTP 401). It authenticates with a Together API key. "
            "Set TOGETHER_API_KEY to a valid key, or pass one with --api-key."
        )
    elif status == 403:
        message = (
            f"The metrics service refused access to organization {organization_id} (HTTP 403). "
            "The service is in beta and access may need to be enabled for your organization. "
            f"Ask your Together AI contact to enable it. See {METRICS_DOCS_URL}."
        )
    elif status == 404:
        message = (
            f"The metrics service has nothing at {url} (HTTP 404). "
            "The service is in beta and its host or path may have changed. "
            f"Check {METRICS_DOCS_URL} for the current URL, then pass the new host with --metrics-url "
            f"or set {METRICS_URL_ENV_VAR}."
        )
    else:
        detail = f": {error.body[:200]}" if error.body else ""
        message = (
            f"The metrics service returned HTTP {status}{detail}. "
            f"The service is in beta. Try again in a minute, and see {METRICS_DOCS_URL} if it keeps failing."
        )
    exit_with_message(f"[red]Error:[/red] {escape_rich_markup(message)}", error=message)


def _fail_for_transport(error: httpx.HTTPError, *, url: str) -> NoReturn:
    message = (
        f"Could not read from the metrics service at {url} ({type(error).__name__}: {error}). "
        "The service is in beta and its host may have changed. "
        f"Check {METRICS_DOCS_URL} for the current URL, then pass the new host with --metrics-url "
        f"or set {METRICS_URL_ENV_VAR}."
    )
    exit_with_message(f"[red]Error:[/red] {escape_rich_markup(message)}", error=message)


async def _resolve_target(config: CLIConfig, id: str) -> tuple[Endpoint, str | None]:
    """Resolve an endpoint or deployment reference to ``(endpoint, deployment_id)``."""
    if id.startswith("dep_"):
        return await resolve_deployment_id(config.client, id)
    if id.startswith("ep_"):
        return await resolve_endpoint(config, id), None
    try:
        return await resolve_endpoint(config, id), None
    except ValueError:
        pass
    # Not an endpoint name, so try it as a deployment name before failing.
    try:
        return await resolve_deployment_id(config.client, id)
    except AmbiguousDeploymentError:
        raise
    except ValueError:
        raise ValueError(
            f"No endpoint or deployment named {id} was found. Run `tg endpoints ls` to list endpoints."
        ) from None


async def metrics(
    id: Annotated[
        str,
        Parameter(
            help=(
                "Endpoint name or ID (ep_...) to report every deployment under it, "
                "or a deployment name or ID (dep_...) to report that deployment only"
            )
        ),
    ],
    *,
    metrics_url: MetricsUrlParameter = None,
    config: CLIConfigParameter,
) -> None:
    """Show how many requests each deployment received in the last 5 minutes (beta)."""
    endpoint, deployment_id = await show_loading_status("Resolving endpoint...", _resolve_target(config, id))

    organization = organization_of(await config.client.whoami())
    if organization is None:
        message = (
            "Could not find an organization for these credentials, and metrics are served per organization. "
            "Run `tg whoami` to check which account the CLI is using."
        )
        exit_with_message(f"[red]Error:[/red] {escape_rich_markup(message)}", error=message)

    url = metrics_request_url(metrics_url or DEFAULT_METRICS_URL, organization.id)
    try:
        report = await show_loading_status(
            "Loading request metrics...",
            _load_request_rates(config, url, endpoint=endpoint, deployment_id=deployment_id),
        )
    except MetricsRequestError as error:
        _fail_for_status(error, url=url, organization_id=organization.id)
    except httpx.HTTPError as error:
        _fail_for_transport(error, url=url)

    deployments = sorted(report.deployments, key=lambda entry: (-entry.rate, entry.deployment_id))
    total_rate = sum((entry.rate for entry in deployments), 0.0)
    note = (
        None
        if total_rate > 0
        else _no_requests_message(
            target_id=deployment_id or endpoint.id, organization_has_series=report.organization_has_series
        )
    )

    if config.json:
        payload: Dict[str, object] = {
            "object": "endpoint.request_metrics",
            "endpoint_id": endpoint.id,
            "endpoint_name": endpoint.name,
            "metric": REQUEST_RATE_METRIC,
            "window_seconds": RATE_WINDOW_SECONDS,
            "sampled_at": (
                datetime.fromtimestamp(report.sampled_at_ms / 1000, tz=timezone.utc).isoformat()
                if report.sampled_at_ms is not None
                else None
            ),
            "requests_per_second": total_rate,
            "estimated_requests": round(estimated_requests(total_rate), 2),
            "deployments": [
                {
                    "deployment_id": entry.deployment_id,
                    "deployment_name": entry.deployment_name,
                    "requests_per_second": entry.rate,
                    "estimated_requests": round(estimated_requests(entry.rate), 2),
                    "status_codes": {
                        status_code: {
                            "requests_per_second": rate,
                            "estimated_requests": round(estimated_requests(rate), 2),
                        }
                        for status_code, rate in sorted(
                            entry.by_status_code.items(), key=lambda item: _status_code_sort_key(item[0])
                        )
                    },
                }
                for entry in deployments
            ],
        }
        if note is not None:
            payload["message"] = note
        emit_json(payload)
        return

    endpoint_name = _short_name(endpoint.name) or endpoint.id
    table = ListTable(
        title=f"Requests in the last 5 minutes: {escape_rich_markup(endpoint_name)} ({endpoint.id})",
        empty_message=f"No deployments found for endpoint {endpoint.id}.",
    )
    table.add_primary_column("Deployment", ratio=3, overflow="fold")
    table.add_column("Req/s", ratio=None, width=10, justify="right", no_wrap=True)
    table.add_column("Requests", ratio=None, width=10, justify="right", no_wrap=True)
    table.add_column("By status code", ratio=2, overflow="fold")
    for entry in deployments:
        by_status_code = "\n".join(
            f"{status_code}: {_format_count(estimated_requests(rate))}"
            for status_code, rate in sorted(
                entry.by_status_code.items(), key=lambda item: _status_code_sort_key(item[0])
            )
        )
        table.add_row(
            f"{escape_rich_markup(entry.deployment_name or '(not in endpoint)')}\n[muted]{entry.deployment_id}[/muted]",
            _format_rate(entry.rate),
            _format_count(estimated_requests(entry.rate)),
            by_status_code or "-",
        )
    console.print(table)
    console.print(
        f"[dim]Beta. Counts are estimates: the {REQUEST_RATE_METRIC} rate, a per-second average "
        f"over the last 5 minutes, times {RATE_WINDOW_SECONDS}.[/dim]"
    )
    if note is not None:
        console.print(f"\n[yellow]{escape_rich_markup(note)}[/yellow]")
