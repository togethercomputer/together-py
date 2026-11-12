from __future__ import annotations

from urllib.parse import parse_qs

import httpx

from together.lib.cli.api.endpoints.events import _repeat_event_type_query, _repeat_endpoint_event_types


def _query(url: httpx.URL) -> dict[str, list[str]]:
    return parse_qs(url.query.decode())


def test_repeat_endpoint_event_types_splits_comma_joined_types() -> None:
    request = httpx.Request(
        "GET",
        "https://api.together.ai/v2/projects/proj/endpoints/ep_1/events",
        params={"limit": "50", "deploymentIds": "dep_1,dep_2", "types": "deployment.scaled, condition.set"},
    )

    _repeat_endpoint_event_types(request)

    query = _query(request.url)
    assert query["types"] == ["deployment.scaled", "condition.set"]
    assert query["deploymentIds"] == ["dep_1,dep_2"]
    assert query["limit"] == ["50"]


def test_repeat_endpoint_event_types_leaves_a_single_type() -> None:
    request = httpx.Request(
        "GET",
        "https://api.together.ai/projects/proj/endpoints/ep_1/events",
        params={"types": "deployment.scaled"},
    )
    original = str(request.url)

    _repeat_endpoint_event_types(request)

    assert str(request.url) == original
    assert _query(request.url)["types"] == ["deployment.scaled"]


def test_repeat_endpoint_event_types_ignores_other_event_feeds() -> None:
    request = httpx.Request(
        "GET",
        "https://api.together.ai/v1/fine-tunes/ft_1/events",
        params={"types": "a,b"},
    )
    original = str(request.url)

    _repeat_endpoint_event_types(request)

    assert str(request.url) == original
    assert _query(request.url)["types"] == ["a,b"]


async def test_request_hook_rewrites_types_before_send() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        async with _repeat_event_type_query(http_client):
            await http_client.get(
                "https://api.together.ai/v2/projects/proj/endpoints/ep_1/events",
                params={"types": "deployment.scaled,condition.set", "deploymentIds": "dep_1,dep_2"},
            )
        assert http_client.event_hooks["request"] == []

    assert len(seen) == 1
    query = _query(seen[0].url)
    assert query["types"] == ["deployment.scaled", "condition.set"]
    assert query["deploymentIds"] == ["dep_1,dep_2"]
