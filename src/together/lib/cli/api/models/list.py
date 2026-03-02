from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether, omit
from together.lib.utils.serializer import datetime_serializer

async def list_(
    type_: Annotated[Optional[Literal["dedicated"]], Parameter(name="type")] = None,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List models."""
    models_list = await client.models.list(dedicated=type_ == "dedicated" if type_ else omit)

    if json_output:
        import json as json_lib

        items = [model.model_dump() for model in models_list]
        print(json_lib.dumps(items, indent=2, default=datetime_serializer))
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
