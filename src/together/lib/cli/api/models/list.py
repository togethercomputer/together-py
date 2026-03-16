from typing import Annotated, Any, Coroutine, List, Literal, Optional
import asyncio
from cyclopts import Parameter

from together.lib.cli.logger.list import ListTable
from together import omit
from together.lib.cli.api._utils import Config
from together._utils._json import openapi_dumps
from together.lib.cli.logger.console import console
from together.types import ModelListResponse

async def list(
    config: Annotated[Config, Parameter(name="*", group="General")] = Config(),
    type: Annotated[Optional[Literal["dedicated"]], Parameter(name="--type", show_choices=True, help="Filter models by specified type.")] = None,
    after: Annotated[Optional[str], Parameter(name="--after", help="Continue pagination from a specific model ID.")] = None,
    json: Annotated[Optional[bool], Parameter(name="--json", negative_bool="", help="Print output in JSON format", group="General")] = None
) -> None:
    client = config.client()

    models_list = await show_loading_status(client.models.list(dedicated=type == "dedicated" if type else omit))

    sorted_models_list = sorted(models_list, key=lambda x: x.type or "")

    index_of_start = next((i for i, model in enumerate(sorted_models_list) if model.id == after), 0) if after else 0

    models_to_display = sorted_models_list[index_of_start:index_of_start + 10]

    if json:
        console.print_json(openapi_dumps(models_to_display).decode())
        return

    table = ListTable()
    table.add_column("Type")
    table.add_primary_column("Model", ratio=4)
    table.add_column("Context Length", justify="right")
    table.add_column("Pricing per 1M Tokens", justify="right")

    # If the server has a bug and returns an empty .type this will crash if we don't do the or "".
    for model in models_to_display:
        price_parts: List[str] = []

        # Only show pricing if a value actually exists
        if model.pricing and model.pricing.input > 0 and model.pricing.output > 0:
            price_parts.append(f"${model.pricing.input:.2f}")
            price_parts.append(f"${model.pricing.output:.2f}")
        else:
            price_parts.append(f"[link=https://api.together.xyz/models/{model.id}]see pricing[/link]")

        table.add_row(
            model.type or "other",
            f"[link=https://api.together.xyz/models/{model.id}]{model.id}[/link]",
            str(model.context_length) if model.context_length else '',
            ' / '.join(price_parts)
        )

    console.print(table)
    next_index = index_of_start + 10
    if next_index < len(sorted_models_list):
        console.print(f"\n[dim]>[/dim] To display the next page, run `tg models list --after {sorted_models_list[next_index].id}`")



async def show_loading_status(request: Coroutine[Any, Any, ModelListResponse]) -> ModelListResponse:
    task = asyncio.create_task(request)
    with console.status(
        "[progress.description]Loading models...[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",
    ):
        await task
    return task.result()