from __future__ import annotations

import re
from typing import Literal, Optional, cast
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter

ModalityFilter = Literal["MODALITY_TEXT", "MODALITY_IMAGE", "MODALITY_AUDIO", "MODALITY_VIDEO"]
ProductFilter = Literal["PRODUCT_SERVERLESS", "PRODUCT_DEDICATED", "PRODUCT_FINE_TUNING"]


async def public(
    search: Annotated[Optional[str], Parameter(help="Search by id, name, or description")] = None,
    limit: Annotated[Optional[int], Parameter(help="Maximum models to return")] = None,
    after: AfterParameter = None,
    modality: Annotated[
        Optional[Literal["text", "image", "audio", "video"]],
        Parameter(help="Filter by input modality"),
    ] = None,
    product: Annotated[
        Optional[Literal["serverless", "dedicated", "fine-tuning"]],
        Parameter(help="Filter by product surface"),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List platform-supported base models usable when creating a beta model."""
    response = await show_loading_status(
        "Loading supported models...",
        config.client.beta.models.list_supported(
            limit=limit if limit is not None else omit,
            after=after or omit,
            search=search or omit,
            modality=cast(ModalityFilter, f"MODALITY_{modality.upper()}") if modality is not None else omit,
            product=cast(ProductFilter, f"PRODUCT_{product.upper().replace('-', '_')}")
            if product is not None
            else omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable("Supported Models", empty_message="No supported models found.")
    table.add_primary_column("Name")
    table.add_column("ID", ratio=2)
    table.add_column("Quant")
    table.add_column("GPUs")
    table.add_column("Parallelism")

    for model in response.data:
        profiles = model.deployment_profiles or []
        if not profiles:
            table.add_row(model.name or "", "", "", "", "", "")
            continue

        for profile in profiles:
            gpu = ""
            if profile.gpu_count or profile.gpu_type:
                gpu = f"{profile.gpu_count or '?'}x {profile.gpu_type or '?'}"
            table.add_row(
                model.name or "",
                f"    ID: [primary]{_profile_model_id(profile.model) or model.id or ''}[/primary]\nConfig: [primary]{profile.certified_config_revision_id or ''}[/primary]",
                profile.quantization or "",
                gpu,
                profile.parallelism or "",
            )
    console.print(table)

    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta models public --after {response.next_cursor}[/white]")


def _profile_model_id(profile_model: str | None) -> str:
    if not profile_model:
        return ""
    match = re.search(r"/models/(ml_[^/]+)", profile_model)
    return match.group(1) if match else profile_model.rsplit("/", 1)[-1]
