from __future__ import annotations

import time
import asyncio
from types import TracebackType
from typing import Any, TypeVar
from dataclasses import field, dataclass
from collections.abc import Coroutine

import httpx

from ..types import LoraConfig, OptimizerConfig, SessionMetadata
from .session import (
    DEFAULT_SESSION_CREATION_TIMEOUT,
    DEFAULT_SESSION_CREATION_INTERVAL,
    SessionClient,
)
from ....._types import omit
from ....._client import AsyncTogether
from .....types.beta.rl.model_resources import ModelResources

_T = TypeVar("_T")

_READY_STATUS = "MODEL_RESOURCES_STATUS_READY"
_TERMINAL_STATUSES = {
    "MODEL_RESOURCES_STATUS_ERROR",
    "MODEL_RESOURCES_STATUS_STOPPING",
    "MODEL_RESOURCES_STATUS_STOPPED",
}
DEFAULT_MODEL_RESOURCES_CREATION_TIMEOUT: float | None = 3600.0
DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL: float = 10.0
_PROVISIONING_TIMEOUT = httpx.Timeout(timeout=300, connect=300)


@dataclass
class ModelResourcesClient:
    _model_resources_id: str
    _client: AsyncTogether

    _event_loop: asyncio.AbstractEventLoop | None = field(
        init=False,
        default=None,
    )

    @property
    def model_resources_id(self) -> str:
        return self._model_resources_id

    def __enter__(self) -> ModelResourcesClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop()

    async def __aenter__(self) -> ModelResourcesClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.stop_async()

    def run(self, coro: Coroutine[Any, Any, _T]) -> _T:
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()
        return self._event_loop.run_until_complete(coro)

    def _close_event_loop(self) -> None:
        if self._event_loop is not None and not self._event_loop.is_running():
            self._event_loop.close()
            self._event_loop = None

    @classmethod
    def _run_blocking(cls, coro: Coroutine[Any, Any, ModelResourcesClient]) -> ModelResourcesClient:
        """Drive an async constructor to completion on a fresh loop, then adopt that
        loop so subsequent blocking calls on the handle reuse it."""
        event_loop = asyncio.new_event_loop()
        task = event_loop.create_task(coro)
        try:
            output = event_loop.run_until_complete(task)
        except BaseException:
            task.cancel()
            try:
                event_loop.run_until_complete(task)
            except (asyncio.CancelledError, Exception):
                pass
            event_loop.close()
            raise

        assert output._event_loop is None
        output._event_loop = event_loop
        return output

    @classmethod
    def create(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        base_model: str,
        lora_enabled: bool = True,
        num_generator_replicas: int = 1,
        optimizer_config: OptimizerConfig | None = None,
        timeout: float | None = DEFAULT_MODEL_RESOURCES_CREATION_TIMEOUT,
        interval: float = DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL,
    ) -> ModelResourcesClient:
        return cls._run_blocking(
            cls.create_async(
                api_key=api_key,
                base_url=base_url,
                base_model=base_model,
                lora_enabled=lora_enabled,
                num_generator_replicas=num_generator_replicas,
                optimizer_config=optimizer_config,
                timeout=timeout,
                interval=interval,
            )
        )

    @classmethod
    def attach(
        cls,
        *,
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
    ) -> ModelResourcesClient:
        """Bind a fully-capable handle to an existing resource.

        Unlike :meth:`create`, this provisions no GPUs and does not wait for
        READY — it only confirms the resource exists. Releasing the handle with
        :meth:`detach` leaves the remote resource running.
        """
        return cls._run_blocking(
            cls.attach_async(
                model_resources_id=model_resources_id,
                api_key=api_key,
                base_url=base_url,
            )
        )

    @classmethod
    async def attach_async(
        cls,
        *,
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
    ) -> ModelResourcesClient:
        client = AsyncTogether(api_key=api_key, base_url=base_url, timeout=_PROVISIONING_TIMEOUT)
        try:
            await client.beta.rl.model_resources.retrieve(model_resources_id)
        except BaseException:
            await client.close()
            raise
        return cls(model_resources_id, client)

    @classmethod
    async def create_async(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        base_model: str,
        lora_enabled: bool = True,
        num_generator_replicas: int = 1,
        optimizer_config: OptimizerConfig | None = None,
        timeout: float | None = DEFAULT_MODEL_RESOURCES_CREATION_TIMEOUT,
        interval: float = DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL,
    ) -> ModelResourcesClient:
        client = AsyncTogether(api_key=api_key, base_url=base_url, timeout=_PROVISIONING_TIMEOUT)
        model_resources_id: str | None = None
        try:
            model_resources = await client.beta.rl.model_resources.create(
                base_model=base_model,
                lora_enabled=lora_enabled,
                compute_config={"num_generator_replicas": num_generator_replicas},
                optimizer_config=optimizer_config if optimizer_config is not None else omit,
            )
            model_resources_id = model_resources.id
            print(f"[model-resources:{model_resources_id}] created, waiting for READY status...")  # noqa: T201

            output = cls(model_resources_id, client)
            await output._wait_for_ready_async(timeout=timeout, interval=interval)
            return output
        except BaseException as exc:
            if model_resources_id is not None:
                print(f"[model-resources:{model_resources_id}] stopping model resources due to {type(exc).__name__}...")  # noqa: T201
                try:
                    await client.beta.rl.model_resources.stop(model_resources_id)
                    print(f"[model-resources:{model_resources_id}] stopped")  # noqa: T201
                except Exception:
                    print(f"[model-resources:{model_resources_id}] failed to stop model resources during cleanup")  # noqa: T201
            await client.close()
            raise

    async def _wait_for_ready_async(self, *, timeout: float | None, interval: float) -> None:
        start = time.monotonic()
        while True:
            current = await self._client.beta.rl.model_resources.retrieve(self._model_resources_id)
            elapsed = time.monotonic() - start
            print(f"[model-resources:{self._model_resources_id}] status={current.status} elapsed={elapsed:.1f}s")  # noqa: T201
            if current.status == _READY_STATUS:
                print(f"[model-resources:{self._model_resources_id}] ready in {elapsed:.1f}s")  # noqa: T201
                return
            if current.status in _TERMINAL_STATUSES:
                msg = f"Model resources {self._model_resources_id} entered terminal status {current.status}"
                raise RuntimeError(msg)
            if timeout is not None and elapsed >= timeout:
                msg = f"Timed out waiting for model resources {self._model_resources_id} to reach READY"
                raise TimeoutError(msg)
            await asyncio.sleep(interval)

    def retrieve(self) -> ModelResources:
        return self.run(self.retrieve_async())

    async def retrieve_async(self) -> ModelResources:
        return await self._client.beta.rl.model_resources.retrieve(self._model_resources_id)

    def create_session(
        self,
        *,
        display_name: str | None = None,
        metadata: SessionMetadata | None = None,
        resume_from_checkpoint_id: str | None = None,
        lora_config: LoraConfig | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> SessionClient:
        return SessionClient.create(
            api_key=self._client.api_key,
            base_url=self._client.base_url,
            model_resources_id=self._model_resources_id,
            display_name=display_name,
            metadata=metadata,
            resume_from_checkpoint_id=resume_from_checkpoint_id,
            lora_config=lora_config,
            timeout=timeout,
            interval=interval,
        )

    async def create_session_async(
        self,
        *,
        display_name: str | None = None,
        metadata: SessionMetadata | None = None,
        resume_from_checkpoint_id: str | None = None,
        lora_config: LoraConfig | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> SessionClient:
        return await SessionClient.create_async(
            api_key=self._client.api_key,
            base_url=self._client.base_url,
            model_resources_id=self._model_resources_id,
            display_name=display_name,
            metadata=metadata,
            resume_from_checkpoint_id=resume_from_checkpoint_id,
            lora_config=lora_config,
            timeout=timeout,
            interval=interval,
        )

    def stop(self) -> Any:
        output = self.run(self.stop_async())
        self._close_event_loop()
        return output

    async def stop_async(self) -> Any:
        output = await self._client.beta.rl.model_resources.stop(self._model_resources_id)
        self._close_event_loop()
        await self._client.close()
        return output

    def detach(self) -> None:
        """Release the handle's client and event loop without stopping the remote
        resource — the tenant counterpart to :meth:`stop`, so borrowed GPUs keep
        running after we let go of the handle."""
        self.run(self.detach_async())
        self._close_event_loop()

    async def detach_async(self) -> None:
        self._close_event_loop()
        await self._client.close()
