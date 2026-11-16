from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

_SERVICE_DISCONTINUED = "Service discontinued"


async def discontinued(
    *_tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
) -> None:
    raise Exception(_SERVICE_DISCONTINUED)
