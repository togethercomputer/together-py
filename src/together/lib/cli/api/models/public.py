from __future__ import annotations

import re
from typing import List, Literal, Optional, cast
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.supported_model import UnitPrice
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
    """List platform-supported base models usable when creating a model."""
    response = await show_loading_status(
        "Loading supported models...",
        config.client.models.list_supported(
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
    table.add_primary_column("Model", ratio=3)
    table.add_column("GPUs")
    table.add_column("Parallelism")
    table.add_column("Unit Prices", ratio=2)

    for model in response.data:
        unit_prices = _format_unit_prices(model.unit_prices)
        profiles = model.deployment_profiles or []
        if not profiles:
            table.add_row(model.name or model.id or "", "", "", unit_prices)
            continue

        for profile in profiles:
            gpu = ""
            if profile.gpu_count or profile.gpu_type:
                gpu_type = profile.gpu_type or "?"
                gpu_type = " ".join([part.capitalize() for part in gpu_type.split("-") if part.strip()])
                gpu = f"{profile.gpu_count or '?'}x {gpu_type}"
            profile_model = _profile_cli_model(profile, model.id)
            table.add_row(
                profile_model,
                gpu,
                profile.parallelism or "",
                unit_prices,
            )
    console.print(table)

    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg models public --after {response.next_cursor}[/white]")


_UNIT_LABELS = {"PRICING_UNIT_AUDIO_MINUTE": "audio min", "PRICING_UNIT_MILLION_CHARACTERS": "1M chars"}


def _format_unit_prices(unit_prices: Optional[List[UnitPrice]]) -> str:
    return "\n".join(
        f"${_trim_price(price.price_usd)}/{_UNIT_LABELS.get(price.unit, price.unit)} "
        f"({price.tier.removeprefix('PRICING_TIER_').lower()})"
        for price in unit_prices or []
    )


def _trim_price(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _profile_cli_model(profile: object, fallback: str | None = None) -> str:
    return (
        getattr(profile, "api_model_name", None) or _profile_model_id(getattr(profile, "model", None)) or fallback or ""
    )


def _profile_model_id(profile_model: str | None) -> str:
    if not profile_model:
        return ""
    match = re.search(r"/models/(ml_[^/]+)", profile_model)
    return match.group(1) if match else profile_model.rsplit("/", 1)[-1]
