from __future__ import annotations

import time
import asyncio
import warnings
from types import TracebackType
from typing import Any, TypeVar
from dataclasses import field, dataclass
from collections.abc import Coroutine

import httpx

from .._loop import LoopGate, run_untracked, on_client_loop, run_untracked_async
from .session import (
    DEFAULT_SESSION_CREATION_TIMEOUT,
    DEFAULT_SESSION_CREATION_INTERVAL,
    SessionClient,
)
from ..._types import omit
from ..._client import AsyncTogether
from ..._exceptions import NotFoundError, BadRequestError
from ...types.post_training.model_resources import ModelResources
from ...types.post_training.lora_config_param import LoraConfigParam as LoraConfig
from ...types.post_training.optimizer_config_param import OptimizerConfigParam as OptimizerConfig
from ...types.post_training.session_metadata_param import SessionMetadataParam as SessionMetadata
from ...types.post_training.model_resource_create_params import ComputeConfig

_T = TypeVar("_T")

_READY_STATUS = "MODEL_RESOURCES_STATUS_READY"
# STOPPING is terminal here: billing has already stopped. Session stop cannot
# use the same set — TRAINING_SESSION_STATUS_STOPPING still holds the LoRA slot.
_TERMINAL_STATUSES = {
    "MODEL_RESOURCES_STATUS_ERROR",
    "MODEL_RESOURCES_STATUS_STOPPING",
    "MODEL_RESOURCES_STATUS_STOPPED",
}
DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL: float = 10.0
DEFAULT_MODEL_RESOURCES_STOP_TIMEOUT: float | None = 300.0
DEFAULT_MODEL_RESOURCES_STOP_INTERVAL: float = 2.0
_PROVISIONING_TIMEOUT = httpx.Timeout(timeout=300, connect=300)


@dataclass
class ModelResourcesClient:
    _model_resources_id: str
    _client: AsyncTogether

    _loop: LoopGate = field(init=False, default_factory=LoopGate, repr=False)

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
        # A handle released with detach() is already torn down; stopping it here would report
        # a stranded remote for a stop the caller never asked for.
        if not self._loop.closed:
            self.stop()

    async def __aenter__(self) -> ModelResourcesClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if not self._loop.closed:
            await self.stop_async()

    def run(self, coro: Coroutine[Any, Any, _T]) -> _T:
        return self._loop.run(coro)

    @classmethod
    def create(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        base_model: str,
        base_weights_ref: str | None = None,
        lora_enabled: bool = True,
        compute_config: ComputeConfig | None = None,
        optimizer_config: OptimizerConfig | None = None,
        inactive_timeout: int | None = None,
        ready_timeout: float | None = None,
        interval: float = DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL,
        timeout: float | None = None,
    ) -> ModelResourcesClient:
        """Create model resources and wait until they are READY.

        If anything fails after the resource is created, including the wait, the resource is stopped.

        Args:
            api_key: Together API key. ``None`` reads ``TOGETHER_API_KEY``.
            base_url: API base URL. ``None`` reads ``TOGETHER_BASE_URL``, then uses the public API.
            base_model: Base model to train, one of the models listed by ``/rl/supported-models``.
            base_weights_ref: Full-weight model in this project's model registry whose weights the
                resource trains instead of the base model's own. ``None`` uses the base model's weights.
            lora_enabled: ``True`` hosts LoRA sessions. ``False`` hosts a single full-weight session.
            compute_config: GPU type and number of generator replicas. ``None`` lets the server choose.
            optimizer_config: Optimizer for the resource. ``None`` uses the server default.
            inactive_timeout: Seconds (300-86400) the server keeps the resource READY with no training
                operations, after which it stops the resource. ``None`` uses the server default of 3600.
                Use :meth:`extend_expiry` to keep it longer.
            ready_timeout: Seconds this call waits for READY. ``None`` waits with no limit.
            interval: Seconds between status checks while waiting.
            timeout: Deprecated name of ``ready_timeout``. Setting it shows a ``FutureWarning``.
                ``ready_timeout`` wins if both are set.

        Returns:
            A client for the READY resource.

        Raises:
            RuntimeError: If the resource reaches STOPPING, STOPPED or ERROR before READY.
            TimeoutError: If the resource is not READY within ``ready_timeout`` (or ``timeout``).
        """
        return run_untracked(
            cls.create_async(
                api_key=api_key,
                base_url=base_url,
                base_model=base_model,
                base_weights_ref=base_weights_ref,
                lora_enabled=lora_enabled,
                compute_config=compute_config,
                optimizer_config=optimizer_config,
                inactive_timeout=inactive_timeout,
                ready_timeout=ready_timeout,
                interval=interval,
                timeout=timeout,
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
        return run_untracked(
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
        async def attach_on_process_loop() -> ModelResourcesClient:
            client = AsyncTogether(api_key=api_key, base_url=base_url, timeout=_PROVISIONING_TIMEOUT)
            try:
                await client.post_training.model_resources.retrieve(model_resources_id)
            except BaseException:
                await client.close()
                raise
            return cls(model_resources_id, client)

        return await run_untracked_async(attach_on_process_loop())

    @classmethod
    async def create_async(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        base_model: str,
        base_weights_ref: str | None = None,
        lora_enabled: bool = True,
        compute_config: ComputeConfig | None = None,
        optimizer_config: OptimizerConfig | None = None,
        inactive_timeout: int | None = None,
        ready_timeout: float | None = None,
        interval: float = DEFAULT_MODEL_RESOURCES_CREATION_INTERVAL,
        timeout: float | None = None,
    ) -> ModelResourcesClient:
        """See :meth:`create`."""
        if timeout is not None:
            warnings.warn(
                "timeout in ModelResourcesClient.create and create_async is deprecated: use ready_timeout",
                FutureWarning,
                stacklevel=2,
            )
            if ready_timeout is None:
                ready_timeout = timeout

        async def create_on_process_loop() -> ModelResourcesClient:
            client = AsyncTogether(api_key=api_key, base_url=base_url, timeout=_PROVISIONING_TIMEOUT)
            model_resources_id: str | None = None
            try:
                model_resources = await client.post_training.model_resources.create(
                    base_model=base_model,
                    base_weights_ref=base_weights_ref if base_weights_ref is not None else omit,
                    lora_enabled=lora_enabled,
                    compute_config=compute_config if compute_config is not None else omit,
                    optimizer_config=optimizer_config if optimizer_config is not None else omit,
                    inactive_timeout=inactive_timeout if inactive_timeout is not None else omit,
                )
                model_resources_id = model_resources.id
                print(f"[model-resources:{model_resources_id}] created, waiting for READY status...")  # noqa: T201

                output = cls(model_resources_id, client)
                await output._wait_for_ready_async(timeout=ready_timeout, interval=interval)
                return output
            except BaseException as exc:
                if model_resources_id is not None:
                    tag = f"[model-resources:{model_resources_id}]"
                    print(f"{tag} stopping model resources due to {type(exc).__name__}...")  # noqa: T201
                    try:
                        await client.post_training.model_resources.stop(model_resources_id)
                        print(f"{tag} stopped")  # noqa: T201
                    except Exception as cleanup_exc:
                        # Swallowed so it cannot mask exc, the failure that triggered cleanup.
                        print(f"{tag} failed to stop model resources during cleanup: {cleanup_exc!r}")  # noqa: T201
                await client.close()
                raise

        return await run_untracked_async(create_on_process_loop())

    async def _wait_for_ready_async(self, *, timeout: float | None, interval: float) -> None:
        start = time.monotonic()
        while True:
            current = await self._client.post_training.model_resources.retrieve(self._model_resources_id)
            elapsed = time.monotonic() - start
            tag = f"[model-resources:{self._model_resources_id}]"
            queue_position = current.status_details.queue_position
            queue_text = "" if queue_position is None else f" queue_position={queue_position}"
            print(f"{tag} status={current.status}{queue_text} elapsed={elapsed:.1f}s")  # noqa: T201
            if current.status == _READY_STATUS:
                print(f"{tag} ready in {elapsed:.1f}s")  # noqa: T201
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

    @on_client_loop
    async def retrieve_async(self) -> ModelResources:
        return await self._client.post_training.model_resources.retrieve(self._model_resources_id)

    def extend_expiry(self, *, seconds: int) -> ModelResources:
        """Keep the resource from stopping for inactivity for at least ``seconds`` (60-86400) from now.

        It moves ``expires_at`` to at least that time. The API refuses it when the resource is not READY.
        """
        return self.run(self.extend_expiry_async(seconds=seconds))

    @on_client_loop
    async def extend_expiry_async(self, *, seconds: int) -> ModelResources:
        """See :meth:`extend_expiry`."""
        return await self._client.post_training.model_resources.extend_expiry(self._model_resources_id, seconds=seconds)

    def create_session(
        self,
        *,
        display_name: str | None = None,
        metadata: SessionMetadata | None = None,
        resume_from_checkpoint_id: str | None = None,
        load_optimizer: bool | None = None,
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
            load_optimizer=load_optimizer,
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
        load_optimizer: bool | None = None,
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
            load_optimizer=load_optimizer,
            lora_config=lora_config,
            timeout=timeout,
            interval=interval,
        )

    def stop(self, *, force: bool = False) -> ModelResources | None:
        """Stop the resource and wait until billing stops.

        force also stops every session attached to the resource, including sessions this
        process does not own. Without it the API refuses while any session is still active.
        """
        return self._loop.run_teardown(self._stop_remote(force=force))

    async def stop_async(self, *, force: bool = False) -> ModelResources | None:
        """See :meth:`stop`."""
        return await self._loop.run_teardown_async(self._stop_remote(force=force))

    async def _stop_remote(self, *, force: bool) -> ModelResources:
        try:
            output = await self._client.post_training.model_resources.stop(
                self._model_resources_id, force=force if force else omit
            )
        except BadRequestError:
            # The API refuses to stop a resource that already stopped or failed, for example
            # one the server stopped after its expiry time. That resource needs no stop.
            output = await self._client.post_training.model_resources.retrieve(self._model_resources_id)
            if output.status not in _TERMINAL_STATUSES:
                raise
        if output.status not in _TERMINAL_STATUSES:
            start = time.monotonic()
            while True:
                try:
                    current = await self._client.post_training.model_resources.retrieve(self._model_resources_id)
                except NotFoundError:
                    # Already gone. Transient retrieve failures are retried by the
                    # HTTP client; remaining errors still raise.
                    break
                if current.status in _TERMINAL_STATUSES:
                    break
                if (
                    DEFAULT_MODEL_RESOURCES_STOP_TIMEOUT is not None
                    and time.monotonic() - start >= DEFAULT_MODEL_RESOURCES_STOP_TIMEOUT
                ):
                    warnings.warn(
                        f"Timed out waiting for model resources {self._model_resources_id} to stop billing",
                        stacklevel=2,
                    )
                    break
                await asyncio.sleep(DEFAULT_MODEL_RESOURCES_STOP_INTERVAL)
        await self._client.close()
        return output

    def detach(self) -> None:
        """Release the handle without stopping the remote resource (borrowed GPUs keep running)."""
        self._loop.run_teardown(self._client.close(), stops_remote=False)

    async def detach_async(self) -> None:
        """Release the handle without stopping the remote resource (borrowed GPUs keep running)."""
        await self._loop.run_teardown_async(self._client.close(), stops_remote=False)
