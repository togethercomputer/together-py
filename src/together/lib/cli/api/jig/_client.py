"""API client for jig deployment tool."""

from __future__ import annotations

import os
from typing import Any

import httpx

# Environment-based configuration
TOGETHER_ENV = os.getenv("TOGETHER_ENV", "prod")

if TOGETHER_ENV == "prod":
    API_URL = "api.together.ai"
    REGISTRY_URL = "registry.together.xyz"
elif TOGETHER_ENV == "qa":
    API_URL = "api.qa.together.ai"
    REGISTRY_URL = "registry.t6r-ai.dev"
elif TOGETHER_ENV == "dev":
    API_URL = os.getenv("TOGETHER_API_URL", "")
    REGISTRY_URL = os.getenv("TOGETHER_REGISTRY_URL", "")
    if not API_URL or not REGISTRY_URL:
        raise ValueError("API_URL and REGISTRY_URL must be set in dev mode")
else:
    raise ValueError(f"Unknown TOGETHER_ENV: {TOGETHER_ENV}")

DEBUG = os.getenv("TOGETHER_DEBUG", "").strip()[:1] in ("y", "1", "t")


class APIClient:
    """Together AI API client for jig operations."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=f"https://{API_URL}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    def request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any] | None:
        """Make API request with error handling."""
        if DEBUG:
            print(f"{method} https://{API_URL}{endpoint}")

        response = self._client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def get_username(self) -> str:
        """Get username from proof-data endpoint."""
        response = self.request("GET", "/api/user/proof-data")
        if response is None:
            raise ValueError("Failed to get username: empty response")
        return str(response["projectId"]).lower()

    def stream(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make streaming API request."""
        return self._client.stream(method, endpoint, **kwargs)

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> APIClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
