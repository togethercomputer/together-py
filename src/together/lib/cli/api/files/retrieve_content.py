from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Union

from cyclopts import Parameter

from together import AsyncTogether



async def get_filename(client: AsyncTogether, id: str) -> str:
    r = await client.files.retrieve(id=id)
    return r.filename or id


async def retrieve_content(
    id: str,
    output: Union[str, None] = None,
    stdout: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Retrieve file content and output to file."""
    if stdout:
        response = await client.files.content(id=id)
        print(response.read().decode("utf-8"))
        return
    if output is not None:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        has_extension = Path(output).suffix != ""
        out_path = output if has_extension else f"{output}/{await get_filename(client, id)}"
        with open(out_path, "wb") as f:
            response = await client.files.content(id=id)
            f.write(response.read())
        print(f"File saved to {out_path}")
        return
    raise ValueError("Either --output <filename> or --stdout must be specified")
