from __future__ import annotations

from pathlib import Path
from typing import Annotated, get_args

from cyclopts import Parameter

from together import AsyncTogether
from together.types import FilePurpose
from together._utils._json import openapi_dumps



async def upload(
    file: Path,
    purpose: str = "fine-tune",
    check: bool = True,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Upload file."""
    purpose_enum = FilePurpose(purpose) if purpose in get_args(FilePurpose) else FilePurpose("fine-tune")
    response = await client.files.upload(file=file, purpose=purpose_enum, check=check)
    if json_output:
        print(openapi_dumps(response.model_dump(exclude_none=True)))
        return
    print(f"> Success! File uploaded for {response.purpose}. File ID: {response.id}")
