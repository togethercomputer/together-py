from together import AsyncClient, omit
from together.types.beta import Endpoint


async def find_endpoint_by_deployment(
    client: AsyncClient,
    deployment_id: str,
) -> Endpoint:
    cursor: str | None = None
    while True:
        page = await client.beta.endpoints.list(after=cursor or omit)
        for endpoint in page.data:
            for deployment in endpoint.deployments or []:
                if deployment.id == deployment_id:
                    return endpoint
        if not page.next_cursor:
            break
        cursor = page.next_cursor

    raise ValueError(f"Deployment {deployment_id} not found in any endpoint.")
