from __future__ import annotations

import asyncio
from typing import Any, TypeVar, Coroutine
from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_model_detail


async def retrieve(
    id: Annotated[str, Parameter(help="Model ID to retrieve")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a beta model."""
    model, files = await show_loading_status(
        "Loading beta model...",
        asyncio.gather(
            config.client.beta.models.retrieve(id),
            safe_fetch(config.client.beta.models.list_files(id=id)),
        ),
    )

    if config.json:
        payload = model.to_dict(use_api_names=True)
        if files is not None:
            if files.revision_id:
                payload["revisionId"] = files.revision_id
            if files.revision_created_at:
                payload["revisionCreatedAt"] = files.revision_created_at
            if files.total_size_bytes:
                payload["totalSizeBytes"] = files.total_size_bytes
            payload["files"] = [file.to_dict(use_api_names=True) for file in (files.data or [])]
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    await print_model_detail(model, config=config, files=files)


T = TypeVar("T")


async def safe_fetch(coro: Coroutine[Any, Any, T]) -> T | None:
    try:
        return await coro
    except Exception:
        return None
