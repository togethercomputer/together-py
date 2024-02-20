from __future__ import annotations

import asyncio
import logging
from typing import Iterator

import pytest

import os
from typing import TYPE_CHECKING, AsyncIterator

from together_ai import TogetherAI, AsyncTogetherAI

if TYPE_CHECKING:
  from _pytest.fixtures import FixtureRequest

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("together_ai").setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

access_token = "My Access Token"

@pytest.fixture(scope="session")
def client(request: FixtureRequest) -> Iterator[TogetherAI]:
    strict = getattr(request, 'param', True)
    if not isinstance(strict, bool):
      raise TypeError(f'Unexpected fixture parameter type {type(strict)}, expected {bool}')

    with TogetherAI(base_url=base_url, access_token=access_token, _strict_response_validation=strict) as client :
        yield client

@pytest.fixture(scope="session")
async def async_client(request: FixtureRequest) -> AsyncIterator[AsyncTogetherAI]:
    strict = getattr(request, 'param', True)
    if not isinstance(strict, bool):
      raise TypeError(f'Unexpected fixture parameter type {type(strict)}, expected {bool}')

    async with AsyncTogetherAI(base_url=base_url, access_token=access_token, _strict_response_validation=strict) as client :
        yield client
