from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional

from tabulate import tabulate

from cyclopts import Parameter
from rich import print_json


from together import omit
from together.lib.cli.logger.config import CLIConfig
from together._utils._json import openapi_dumps

async def list_(
    type_: Annotated[Optional[Literal["dedicated"]], Parameter(name="type")] = None,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List models."""
    models_list = await config.client.models.list(dedicated=type_ == "dedicated" if type_ else omit)

    if config.json:
        print_json(openapi_dumps(models_list).decode())
        return

    display_list: List[Dict[str, Any]] = []
    for model in sorted(models_list, key=lambda x: x.type or ""):  # type: ignore
        price_parts: List[str] = []
        if model.pricing and model.pricing.input > 0 and model.pricing.output > 0:
            price_parts.append(f"${model.pricing.input:.2f}")
            price_parts.append(f"${model.pricing.output:.2f}")
        display_list.append(
            {
                "Model": model.id,
                "Type": model.type,
                "Context length": model.context_length if model.context_length else None,
                "Price per 1M Tokens (input/output)": "/".join(price_parts),
            }
        )
    print(tabulate(display_list, headers="keys"))
