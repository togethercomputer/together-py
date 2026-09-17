from __future__ import annotations

from together import AsyncClient, omit
from together.types.beta.endpoints.rollout import Rollout

_TERMINAL_ROLLOUT_STATES = frozenset(
    {
        "ROLLOUT_STATE_COMPLETED",
        "ROLLOUT_STATE_CANCELED",
        "ROLLOUT_STATE_CANCELLING",
    }
)


async def fallback_active_rollout_from_list(client: AsyncClient, endpoint_id: str) -> Rollout | None:
    """Pick a controllable rollout when ``activeRolloutId`` is missing.

    HACK / workaround: the server should always set ``endpoint.activeRolloutId``
    for the in-progress rollout. It sometimes fails to. Until that is fixed, list
    rollouts and use the newest non-terminal one if present.

    Intentionally omits ``filter=ROLLOUT_FILTER_ACTIVE``: that server filter can
    exclude paused / system-paused rollouts. Non-terminal is enforced client-side
    so we never treat a completed/canceled rollout as active.
    """
    candidates: list[Rollout] = []
    async for rollout in client.beta.endpoints.rollouts.list(endpoint_id=endpoint_id, limit=50):
        if rollout.state not in _TERMINAL_ROLLOUT_STATES:
            candidates.append(rollout)

    if not candidates:
        return None

    return max(candidates, key=lambda r: r.created_at)


async def resolve_rollout_by_id(
    client: AsyncClient,
    rollout_id: str,
) -> Rollout:
    """Resolve a rollout ID, preferring the endpoint's active_rollout_id fast path."""
    cursor: str | None = None
    # Cache endpoint IDs so the fallback scan only needs to scan the endpoints that have rollouts.
    endpoint_ids: list[str] = []

    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            endpoint_ids.append(endpoint.id)
            if endpoint.active_rollout_id == rollout_id:
                rollout = await client.beta.endpoints.rollouts.retrieve(
                    rollout_id,
                    endpoint_id=endpoint.id,
                )
                return rollout
        if not page.next_cursor:
            break
        cursor = page.next_cursor

    # Not currently active — fall back to a full scan (e.g. stale ID).
    return await _lazy_scan_for_rollout(client, endpoint_ids, rollout_id)


async def _lazy_scan_for_rollout(
    client: AsyncClient,
    endpoint_ids: list[str],
    rollout_id: str,
) -> Rollout:
    """Locate a rollout by ID via full endpoint × rollout-page scan.

    This is a fallback for when the rollout ID is not the active rollout ID.
    """
    for endpoint_id in endpoint_ids:
        async for rollout in client.beta.endpoints.rollouts.list(
            endpoint_id=endpoint_id,
            limit=50,
        ):
            if rollout.id == rollout_id:
                return rollout

    raise ValueError(f"Rollout {rollout_id} not found.")
