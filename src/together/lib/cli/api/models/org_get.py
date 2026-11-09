from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._whoami import organization_of
from together.lib.cli.utils._console import console
from together.lib.cli.api.models._utils import print_model_detail
from together.lib.cli.components.loader import show_loading_status


async def org_get(
    id: Annotated[str, Parameter(help="Model ID (ml_...) shared with the caller's organization")],
    *,
    config: CLIConfigParameter,
) -> None:
    organization = organization_of(await config.client.whoami())
    if organization is None:
        raise ValueError("This credential has no organization. Run `tg whoami` to see the current identity.")

    model = await show_loading_status(
        "Loading org-scoped model...",
        config.client.models.retrieve_org_model(organization.id, id),
    )

    if config.json:
        console.print_json(openapi_dumps(model.to_dict(use_api_names=True)).decode("utf-8"))
        return

    await print_model_detail(model, config=config)
