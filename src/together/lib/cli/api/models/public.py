from __future__ import annotations

import re
from typing import Literal, Optional, Sequence, cast
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.supported_model import SupportedModel
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
    """List platform-supported models and the products that offer them."""
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
    table.add_primary_column("Model", ratio=3, overflow="fold")
    table.add_column("Products", ratio=2, overflow="fold")

    for model in response.data:
        table.add_row(_format_model_cell(model), _format_products(model.products))
    console.print(table)

    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg models public --after {response.next_cursor}[/white]")


_PRODUCT_LABELS = {
    "PRODUCT_SERVERLESS": "serverless",
    "PRODUCT_DEDICATED": "dedicated endpoints",
    "PRODUCT_FINE_TUNING": "training",
    "PRODUCT_RESERVED": "reserved",
}
_PRODUCT_ORDER = (
    "PRODUCT_SERVERLESS",
    "PRODUCT_DEDICATED",
    "PRODUCT_FINE_TUNING",
    "PRODUCT_RESERVED",
)


def _format_model_cell(model: SupportedModel) -> str:
    parent = model.name or model.id or ""
    lines = [parent]
    seen: set[str] = {parent} if parent else set()
    for profile in model.deployment_profiles or []:
        name = _profile_cli_model(profile, None)
        if not name or name in seen:
            continue
        seen.add(name)
        lines.append(f"  └ {name}")
    return "\n".join(lines)


def _format_products(products: Sequence[str] | None) -> str:
    present = list(dict.fromkeys(products or []))
    ordered = [product for product in _PRODUCT_ORDER if product in present]
    ordered.extend(product for product in present if product not in _PRODUCT_LABELS)
    return "\n".join(_product_label(product) for product in ordered)


def _product_label(product: str) -> str:
    label = _PRODUCT_LABELS.get(product)
    if label is not None:
        return label
    if product.startswith("PRODUCT_"):
        return product.removeprefix("PRODUCT_").replace("_", " ").lower()
    return product


def _profile_cli_model(profile: object, fallback: str | None = None) -> str:
    return (
        getattr(profile, "api_model_name", None) or _profile_model_id(getattr(profile, "model", None)) or fallback or ""
    )


def _profile_model_id(profile_model: str | None) -> str:
    if not profile_model:
        return ""
    match = re.search(r"/models/(ml_[^/]+)", profile_model)
    return match.group(1) if match else profile_model.rsplit("/", 1)[-1]
