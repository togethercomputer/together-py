from typing import Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_models_table
from together.lib.cli.utils._mock_pagination import AfterParameter


async def org(
    *,
    config: CLIConfigParameter,
    limit: Annotated[Optional[int], Parameter(help="Maximum models to return")] = None,
    after: AfterParameter = None,
    organization_id: Annotated[
        Optional[str],
        Parameter(name="organization", help="Organization ID to list; defaults to the authenticated organization"),
    ] = None,
) -> None:
    if organization_id is None:
        me = await config.client.whoami()
        organization_id = me.organization_id

    response = await show_loading_status(
        "Loading org-scoped models...",
        config.client.beta.models.list_org_scoped(
            organization_id,
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_models_table(
        response.data or [],
        empty_message="No org-scoped models found.",
    )
