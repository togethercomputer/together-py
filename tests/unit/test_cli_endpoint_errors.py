from __future__ import annotations

import httpx
import pytest

from together import APIError
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@pytest.mark.parametrize(
    ("body", "diagnostic"),
    [
        ({"message": "Endpoint not found"}, "Endpoints: endpoint not found"),
        ({"message": "Permission denied"}, "Endpoints: permission denied"),
        ({"message": "Authentication failed"}, "Endpoints: authentication failed"),
    ],
)
async def test_endpoint_api_errors_preserve_diagnostic(body: dict[str, str], diagnostic: str) -> None:
    @handle_endpoint_api_errors("Endpoints")
    async def fail() -> None:
        raise APIError("request failed", httpx.Request("GET", "https://api.together.ai/endpoints"), body=body)

    with pytest.raises(CliDiagnosticExit, match=f"^{diagnostic}$"):
        await fail()
