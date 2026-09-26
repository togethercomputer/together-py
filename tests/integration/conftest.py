from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _require_together_api_key() -> None:
    if not os.environ.get("TOGETHER_API_KEY"):
        pytest.skip("TOGETHER_API_KEY is not set")
