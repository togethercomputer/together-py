from __future__ import annotations

import os
import time
import asyncio
import warnings
from uuid import uuid4
from types import TracebackType
from typing import TYPE_CHECKING, Any, TypeVar, cast
from dataclasses import field, dataclass
from collections.abc import Coroutine

import httpx

from .. import _operations
from .._loop import LoopGate, run_untracked, on_client_loop, run_untracked_async
from ....._types import omit
from ....._client import AsyncTogether
from .._operations import require_output
from ....._exceptions import NotFoundError
from ....._base_client import DefaultAsyncHttpxClient
from .....types.beta.rl.session import Session
from .....types.beta.rl.lora_config_param import LoraConfigParam as LoraConfig
from .....types.beta.rl.session_metadata_param import SessionMetadataParam as SessionMetadata
from .....types.beta.rl.training_checkpoint_result import TrainingCheckpointResult
from .....types.beta.rl.inference_checkpoint_result import InferenceCheckpointResult

if TYPE_CHECKING:
    from .trainer import Trainer
    from .generator import Generator

_T = TypeVar("_T")


_RUNNING_STATUS = "TRAINING_SESSION_STATUS_RUNNING"
# Create treats STOPPING as failure: the session never became usable.
_TERMINAL_STATUSES = {
    "TRAINING_SESSION_STATUS_STOPPED",
    "TRAINING_SESSION_STATUS_STOPPING",
    "TRAINING_SESSION_STATUS_ERROR",
    "TRAINING_SESSION_STATUS_EXPIRED",
}
# Stop waits until the LoRA slot is released. STOPPING still holds it.
_INACTIVE_STATUSES = {
    "TRAINING_SESSION_STATUS_STOPPED",
    "TRAINING_SESSION_STATUS_ERROR",
    "TRAINING_SESSION_STATUS_EXPIRED",
}
DEFAULT_SESSION_CREATION_TIMEOUT: float | None = 3600.0
DEFAULT_SESSION_CREATION_INTERVAL: float = 10.0
DEFAULT_SESSION_STOP_TIMEOUT: float | None = 300.0
DEFAULT_SESSION_STOP_INTERVAL: float = 2.0
DEFAULT_CHECKPOINT_TIMEOUT: float | None = 7200.0  # 2 h — large models (e.g. 400B) can take well over 5 min
DEFAULT_OPERATION_TIMEOUT: float | None = _operations.DEFAULT_OPERATION_TIMEOUT
DEFAULT_OPERATION_INTERVAL: float = _operations.DEFAULT_OPERATION_INTERVAL
_MAX_RETRIES = 7

# RL operations are long-lived and chatty; bump httpx defaults so polling and
# concurrent ops don't get strangled by short read timeouts or a small keep-alive pool.
_RL_MAX_CONNECTIONS = int(os.environ.get("TOGETHER_RL_MAX_CONNECTIONS", "256"))
_CLIENT_TIMEOUT = httpx.Timeout(timeout=300, connect=300)
_CLIENT_LIMITS = httpx.Limits(max_connections=_RL_MAX_CONNECTIONS, max_keepalive_connections=_RL_MAX_CONNECTIONS)


@dataclass
class SessionClient:
    _session_id: str
    _client: AsyncTogether
    _has_generator: bool = True

    _loop: LoopGate = field(init=False, default_factory=LoopGate, repr=False)
    _trainer: Trainer | None = field(
        init=False,
        default=None,
    )
    _generator: Generator | None = field(
        init=False,
        default=None,
    )

    def retrieve(self) -> Session:
        return self.run(self.retrieve_async())

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def trainer(self) -> Trainer:
        if self._trainer is None:
            from .trainer import Trainer

            self._trainer = Trainer(self)

        return self._trainer

    @property
    def has_generator(self) -> bool:
        return self._has_generator

    @property
    def generator(self) -> Generator:
        if not self._has_generator:
            raise RuntimeError(f"Session {self._session_id} does not have generator capability")

        if self._generator is None:
            from .generator import Generator

            self._generator = Generator(self)

        return self._generator

    def __enter__(self) -> SessionClient:
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

    def run(self, coro: Coroutine[Any, Any, _T]) -> _T:
        return self._loop.run(coro)

    async def run_async(self, coro: Coroutine[Any, Any, _T]) -> _T:
        return await self._loop.run_async(coro)

    @classmethod
    def create(
        cls,
        *,
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        display_name: str | None = None,
        metadata: SessionMetadata | None = None,
        resume_from_checkpoint_id: str | None = None,
        load_optimizer: bool | None = None,
        lora_config: LoraConfig | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> SessionClient:
        return run_untracked(
            cls.create_async(
                model_resources_id=model_resources_id,
                api_key=api_key,
                base_url=base_url,
                display_name=display_name,
                metadata=metadata,
                resume_from_checkpoint_id=resume_from_checkpoint_id,
                load_optimizer=load_optimizer,
                lora_config=lora_config,
                timeout=timeout,
                interval=interval,
            )
        )

    @classmethod
    def attach(
        cls,
        *,
        session_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
    ) -> SessionClient:
        """Bind a fully-capable handle to an existing training session."""
        return run_untracked(
            cls.attach_async(
                session_id=session_id,
                api_key=api_key,
                base_url=base_url,
            )
        )

    @classmethod
    async def attach_async(
        cls,
        *,
        session_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
    ) -> SessionClient:
        async def attach_on_process_loop() -> SessionClient:
            client = AsyncTogether(
                api_key=api_key,
                base_url=base_url,
                timeout=_CLIENT_TIMEOUT,
                max_retries=_MAX_RETRIES,
                http_client=DefaultAsyncHttpxClient(limits=_CLIENT_LIMITS),
            )
            try:
                session = await client.beta.rl.sessions.retrieve(session_id)
                model_resources = await client.beta.rl.model_resources.retrieve(session.resources_id)
            except BaseException:
                await client.close()
                raise
            return cls(
                session_id,
                client,
                _has_generator=model_resources.compute_config.num_generator_replicas > 0,
            )

        return await run_untracked_async(attach_on_process_loop())

    def create_inference_checkpoint(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> InferenceCheckpointResult:
        return self.run(
            self.create_inference_checkpoint_async(
                timeout=timeout,
                interval=interval,
            )
        )

    def create_training_checkpoint(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> TrainingCheckpointResult:
        return self.run(
            self.create_training_checkpoint_async(
                timeout=timeout,
                interval=interval,
            )
        )

    def stop(self) -> Session | None:
        """Stop the remote session and wait until it is inactive."""
        return self._loop.run_teardown(self._stop_remote())

    def detach(self) -> None:
        """Release the handle's client without stopping the remote session."""
        self._loop.run_teardown(self._client.close(), stops_remote=False)

    async def detach_async(self) -> None:
        """Release the handle's client without stopping the remote session."""
        await self._loop.run_teardown_async(self._client.close(), stops_remote=False)

    async def __aenter__(self) -> SessionClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if not self._loop.closed:
            await self.stop_async()

    async def _submit_and_wait(
        self,
        operation: _operations.OperationResponse,
        *,
        timeout: float | None,
        interval: float,
    ) -> Any:
        completed = await _operations.async_wait_for_operation(
            client=self._client,
            session_id=self._session_id,
            operation=operation,
            timeout=timeout,
            interval=interval,
        )
        return require_output(completed.output, operation=completed)

    async def _wait_for_creation_async(
        self,
        *,
        timeout: float | None,
        interval: float,
    ) -> None:
        start = time.monotonic()
        while True:
            current = await self._client.beta.rl.sessions.retrieve(self._session_id)
            elapsed = time.monotonic() - start
            print(f"[session:{self._session_id}] status={current.status} elapsed={elapsed:.1f}s")  # noqa: T201
            if current.status == _RUNNING_STATUS:
                print(f"[session:{self._session_id}] ready in {elapsed:.1f}s")  # noqa: T201
                return
            if current.status in _TERMINAL_STATUSES:
                msg = f"Session {self._session_id} entered terminal status {current.status}"
                raise RuntimeError(msg)
            if timeout is not None and elapsed >= timeout:
                msg = "Timed out waiting for session to reach RUNNING"
                raise TimeoutError(msg)
            await asyncio.sleep(interval)

    @on_client_loop
    async def retrieve_async(self) -> Session:
        return await self._client.beta.rl.sessions.retrieve(self._session_id)

    @classmethod
    async def create_async(
        cls,
        *,
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        display_name: str | None = None,
        metadata: SessionMetadata | None = None,
        resume_from_checkpoint_id: str | None = None,
        load_optimizer: bool | None = None,
        lora_config: LoraConfig | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> SessionClient:
        async def create_on_process_loop() -> SessionClient:
            client = AsyncTogether(
                api_key=api_key,
                base_url=base_url,
                timeout=_CLIENT_TIMEOUT,
                max_retries=_MAX_RETRIES,
                http_client=DefaultAsyncHttpxClient(limits=_CLIENT_LIMITS),
            )
            session_id: str | None = None
            try:
                model_resources = await client.beta.rl.model_resources.retrieve(model_resources_id)
                session = await client.beta.rl.sessions.create(
                    model_resources_id=model_resources_id,
                    display_name=display_name if display_name is not None else omit,
                    metadata=metadata if metadata is not None else omit,
                    resume_from_checkpoint_id=resume_from_checkpoint_id
                    if resume_from_checkpoint_id is not None
                    else omit,
                    load_optimizer=load_optimizer if load_optimizer is not None else omit,
                    lora_config=lora_config if lora_config is not None else omit,
                )
                session_id = session.id
                print(f"[session:{session_id}] created, waiting for RUNNING status...")  # noqa: T201

                output = cls(
                    session_id,
                    client,
                    _has_generator=model_resources.compute_config.num_generator_replicas > 0,
                )
                await output._wait_for_creation_async(timeout=timeout, interval=interval)
                return output
            except BaseException as exc:
                if session_id is not None:
                    print(f"[session:{session_id}] stopping session due to {type(exc).__name__}...")  # noqa: T201
                    try:
                        await client.beta.rl.sessions.stop(session_id)
                        print(f"[session:{session_id}] stopped")  # noqa: T201
                    except Exception as cleanup_exc:
                        # Swallowed so it cannot mask exc, the failure that triggered cleanup.
                        print(  # noqa: T201
                            f"[session:{session_id}] failed to stop session during cleanup: {cleanup_exc!r}"
                        )
                await client.close()
                raise

        return await run_untracked_async(create_on_process_loop())

    @on_client_loop
    async def create_inference_checkpoint_async(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> InferenceCheckpointResult:
        operation = await self._client.beta.rl.operations.create_inference_checkpoint(
            self._session_id, idempotency_key=str(uuid4())
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(InferenceCheckpointResult, result)

    @on_client_loop
    async def create_training_checkpoint_async(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> TrainingCheckpointResult:
        operation = await self._client.beta.rl.operations.create_training_checkpoint(
            self._session_id, idempotency_key=str(uuid4())
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(TrainingCheckpointResult, result)

    async def stop_async(self) -> Session | None:
        """Stop the remote session and wait until it is inactive."""
        return await self._loop.run_teardown_async(self._stop_remote())

    async def _stop_remote(self) -> Session:
        output = await self._client.beta.rl.sessions.stop(self._session_id)
        if output.status not in _INACTIVE_STATUSES:
            start = time.monotonic()
            while True:
                try:
                    current = await self._client.beta.rl.sessions.retrieve(self._session_id)
                except NotFoundError:
                    # Already gone. Transient retrieve failures are retried by the
                    # HTTP client (max_retries); remaining errors still raise.
                    break
                if current.status in _INACTIVE_STATUSES:
                    break
                if (
                    DEFAULT_SESSION_STOP_TIMEOUT is not None
                    and time.monotonic() - start >= DEFAULT_SESSION_STOP_TIMEOUT
                ):
                    warnings.warn(
                        f"Timed out waiting for session {self._session_id} to become inactive; "
                        "it may still block model resource stop. Call "
                        "model_resources.stop(force=True) to stop the resource anyway",
                        stacklevel=2,
                    )
                    break
                await asyncio.sleep(DEFAULT_SESSION_STOP_INTERVAL)
        await self._client.close()
        return output
