from __future__ import annotations

import os
import time
import asyncio
import logging
from types import TracebackType
from typing import Any, TypeVar, Iterable, cast
from pathlib import Path
from dataclasses import field, dataclass
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor

import httpx

from . import _operations
from ...._types import omit
from ._payloads import prepare_operation_body, resolve_result_payload
from ...._client import AsyncTogether
from ...._base_client import DefaultAsyncHttpxClient
from ....types.beta.rl.sample_result import SampleResult
from ....types.beta.rl.forward_result import ForwardResult
from ....types.beta.rl.training_session import TrainingSession
from ....types.beta.rl.weight_sync_type import WeightSyncType
from ....types.beta.rl.lora_config_param import LoraConfigParam
from ....types.beta.rl.loss_config_param import LossConfigParam
from ....types.beta.rl.optim_step_result import OptimStepResult
from ....types.beta.rl.checkpoint_variant import CheckpointVariant
from ....types.beta.rl.muon_optimizer_params import MuonOptimizerParams
from ....types.beta.rl.adamw_optimizer_params import AdamwOptimizerParams
from ....types.beta.rl.forward_backward_result import ForwardBackwardResult
from ....types.beta.rl.operation_sample_params import Prompt, SamplingParams, OperationSampleParams
from ....types.beta.rl.operation_forward_params import OperationForwardParams
from ....types.beta.rl.training_checkpoint_result import TrainingCheckpointResult
from ....types.beta.rl.inference_checkpoint_result import InferenceCheckpointResult
from ....types.beta.rl.operation_forward_backward_params import Sample, OperationForwardBackwardParams
from ....types.beta.rl.operation_custom_forward_backward_params import Gradient, OperationCustomForwardBackwardParams

logger = logging.getLogger("together")
T = TypeVar("T")


_RUNNING_STATUS = "TRAINING_SESSION_STATUS_RUNNING"
_TERMINAL_STATUSES = {
    "TRAINING_SESSION_STATUS_STOPPED",
    "TRAINING_SESSION_STATUS_STOPPING",
    "TRAINING_SESSION_STATUS_ERROR",
    "TRAINING_SESSION_STATUS_EXPIRED",
}
DEFAULT_SESSION_CREATION_TIMEOUT: float | None = 3600.0
DEFAULT_SESSION_CREATION_INTERVAL: float = 10.0
DEFAULT_OPERATION_TIMEOUT: float | None = 300.0
DEFAULT_CHECKPOINT_TIMEOUT: float | None = 7200.0  # 2 h — large models (e.g. 400B) can take well over 5 min
DEFAULT_OPERATION_INTERVAL: float = 0.1
_MAX_RETRIES = 5

# RL operations are long-lived and chatty; bump httpx defaults so polling and
# concurrent ops don't get strangled by short read timeouts or a small keep-alive pool.
_RL_MAX_CONNECTIONS = int(os.environ.get("TOGETHER_RL_MAX_CONNECTIONS", "256"))
_CLIENT_TIMEOUT = httpx.Timeout(timeout=300, connect=300)
_CLIENT_LIMITS = httpx.Limits(max_connections=_RL_MAX_CONNECTIONS, max_keepalive_connections=_RL_MAX_CONNECTIONS)

# Multi-turn RL rollouts bridge synchronous, network-blocking env steps onto this
# loop via asyncio.to_thread, which dispatches to the loop's default executor.
_THREAD_POOL_SIZE_ENV = "TOGETHER_RL_THREAD_POOL_SIZE"


def _new_event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    pool_size = os.environ.get(_THREAD_POOL_SIZE_ENV)
    if pool_size:
        loop.set_default_executor(ThreadPoolExecutor(max_workers=int(pool_size), thread_name_prefix="together-rl-env"))
        logger.info("RL rollout thread pool widened to %s workers", pool_size)
    return loop


def _prompt_logprobs_from_result(result: SampleResult) -> list[list[float]]:
    """Extract the per-prompt teacher-forced logprobs from a sample result.

    Raises:
        RuntimeError: if any rollout is missing prompt logprobs, which happens when the
            generator does not support them or `return_prompt_logprobs` was not requested.
    """
    logprobs: list[list[float]] = []
    for index, rollout in enumerate(result.rollouts):
        if rollout.prompt_logprobs is None:
            msg = (
                f"Sample result for prompt {index} did not include prompt logprobs; the generator may not support them"
            )
            raise RuntimeError(msg)
        logprobs.append(rollout.prompt_logprobs)
    return logprobs


@dataclass
class Trainer:
    _session_id: str
    _client: AsyncTogether
    _event_loop: asyncio.AbstractEventLoop | None = field(init=False, default=None)

    @property
    def session(self) -> TrainingSession:
        return self.run(self.session_async())

    @property
    def session_id(self) -> str:
        return self._session_id

    def __enter__(self) -> Trainer:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop()

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        if self._event_loop is None:
            self._event_loop = _new_event_loop()
        return self._event_loop.run_until_complete(coro)

    @classmethod
    def _run_blocking(cls, coro: Coroutine[Any, Any, Trainer]) -> Trainer:
        """Drive an async constructor to completion on a fresh loop, then adopt that
        loop so subsequent blocking calls on the trainer reuse it."""
        event_loop = _new_event_loop()
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
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        resume_from_checkpoint_id: str | None = None,
        lora_config: LoraConfigParam | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> Trainer:
        return cls._run_blocking(
            cls.create_async(
                model_resources_id=model_resources_id,
                api_key=api_key,
                base_url=base_url,
                resume_from_checkpoint_id=resume_from_checkpoint_id,
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
    ) -> Trainer:
        """Bind a fully-capable handle to an existing training session."""
        return cls._run_blocking(
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
    ) -> Trainer:
        client = AsyncTogether(
            api_key=api_key,
            base_url=base_url,
            timeout=_CLIENT_TIMEOUT,
            http_client=DefaultAsyncHttpxClient(limits=_CLIENT_LIMITS),
        )
        try:
            await client.beta.rl.sessions.retrieve(session_id)
        except BaseException:
            await client.close()
            raise
        return cls(session_id, client)

    def sample(
        self,
        prompt: Prompt,
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        return self.run(
            self.sample_async(
                prompt,
                num_samples=num_samples,
                sampling_params=sampling_params,
                timeout=timeout,
                interval=interval,
            )
        )

    def sample_batch(
        self,
        prompts: Iterable[Prompt],
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        return self.run(
            self.sample_batch_async(
                prompts=prompts,
                num_samples=num_samples,
                sampling_params=sampling_params,
                timeout=timeout,
                interval=interval,
            )
        )

    def compute_logprobs(
        self,
        prompt: Prompt,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[float]:
        return self.run(
            self.compute_logprobs_async(
                prompt,
                timeout=timeout,
                interval=interval,
            )
        )

    def compute_logprobs_batch(
        self,
        prompts: Iterable[Prompt],
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[list[float]]:
        return self.run(
            self.compute_logprobs_batch_async(
                prompts,
                timeout=timeout,
                interval=interval,
            )
        )

    def forward(
        self,
        *,
        samples: Iterable[Sample],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardResult:
        return self.run(
            self.forward_async(
                samples=samples,
                timeout=timeout,
                interval=interval,
            )
        )

    def forward_backward(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfigParam,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        return self.run(
            self.forward_backward_async(
                samples=samples,
                loss=loss,
                timeout=timeout,
                interval=interval,
            )
        )

    def custom_forward_backward(
        self,
        *,
        samples: Iterable[Sample],
        gradients: Iterable[Gradient],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> Any:
        return self.run(
            self.custom_forward_backward_async(
                samples=samples,
                gradients=gradients,
                timeout=timeout,
                interval=interval,
            )
        )

    def optim_step(
        self,
        *,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_UNSPECIFIED",
        adamw_params: AdamwOptimizerParams | None = None,
        max_grad_norm: float | None = None,
        muon_params: MuonOptimizerParams | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> OptimStepResult:
        return self.run(
            self.optim_step_async(
                weight_sync_type=weight_sync_type,
                adamw_params=adamw_params,
                max_grad_norm=max_grad_norm,
                muon_params=muon_params,
                timeout=timeout,
                interval=interval,
            )
        )

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

    def download_checkpoint(
        self,
        checkpoint_id: str,
        *,
        variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
        output_dir: str | Path = ".",
    ) -> list[Path]:
        return self.run(
            self.download_checkpoint_async(
                checkpoint_id=checkpoint_id,
                variant=variant,
                output_dir=output_dir,
            )
        )

    def stop(self) -> Any:
        output = self.run(self.stop_async())
        if self._event_loop is not None:
            self._event_loop.close()
            self._event_loop = None
        return output

    def detach(self) -> None:
        """Release the handle's client and event loop without stopping the remote session."""
        self.run(self.detach_async())
        if self._event_loop is not None:
            self._event_loop.close()
            self._event_loop = None

    async def detach_async(self) -> None:
        if self._event_loop is not None and not self._event_loop.is_running():
            self._event_loop.close()
            self._event_loop = None
        await self._client.close()

    async def __aenter__(self) -> Trainer:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.stop_async()

    async def _submit_and_wait(
        self,
        operation: _operations.OperationResponse,
        *,
        timeout: float | None,
        interval: float,
    ) -> Any:
        result = await _operations.async_wait_for_operation(
            client=self._client,
            session_id=self._session_id,
            operation=operation,
            timeout=timeout,
            interval=interval,
        )
        if result.output is None:
            msg = f"Operation completed with empty output: {operation}"
            raise RuntimeError(msg)
        return result.output

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

    async def session_async(self) -> TrainingSession:
        return await self._client.beta.rl.sessions.retrieve(self._session_id)

    @classmethod
    async def create_async(
        cls,
        *,
        model_resources_id: str,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        resume_from_checkpoint_id: str | None = None,
        lora_config: LoraConfigParam | None = None,
        timeout: float | None = DEFAULT_SESSION_CREATION_TIMEOUT,
        interval: float = DEFAULT_SESSION_CREATION_INTERVAL,
    ) -> Trainer:
        client = AsyncTogether(
            api_key=api_key,
            base_url=base_url,
            timeout=_CLIENT_TIMEOUT,
            http_client=DefaultAsyncHttpxClient(limits=_CLIENT_LIMITS),
        )
        session_id: str | None = None
        try:
            session = await client.beta.rl.sessions.create(
                model_resources_id=model_resources_id,
                resume_from_checkpoint_id=resume_from_checkpoint_id if resume_from_checkpoint_id is not None else omit,
                lora_config=lora_config if lora_config is not None else omit,
            )
            session_id = session.id
            print(f"[session:{session_id}] created, waiting for RUNNING status...")  # noqa: T201

            output = cls(session_id, client)
            await output._wait_for_creation_async(timeout=timeout, interval=interval)
            return output
        except BaseException as exc:
            if session_id is not None:
                print(f"[session:{session_id}] stopping session due to {type(exc).__name__}...")  # noqa: T201
                try:
                    await client.beta.rl.sessions.stop(session_id)
                    print(f"[session:{session_id}] stopped")  # noqa: T201
                except Exception:
                    print(f"[session:{session_id}] failed to stop session during cleanup")  # noqa: T201
            await client.close()
            raise

    async def sample_async(
        self,
        prompt: Prompt,
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        return await self.sample_batch_async(
            [prompt],
            num_samples=num_samples,
            sampling_params=sampling_params,
            timeout=timeout,
            interval=interval,
        )

    async def sample_batch_async(
        self,
        prompts: Iterable[Prompt],
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        prompts = list(prompts)
        body: dict[str, Any] = {"prompts": prompts}
        if sampling_params is not None:
            body["sampling_params"] = sampling_params
        if num_samples is not None:
            body["num_samples"] = num_samples

        body, large_payload_id = await prepare_operation_body(
            self._client,
            session_id=self._session_id,
            body=body,
            expected_type=OperationSampleParams,
        )
        prompts = cast("list[Prompt]", body["prompts"])

        extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
        operation = await self._client.beta.rl.operations.sample(
            self._session_id,
            prompts=prompts,
            num_samples=num_samples if num_samples is not None else omit,
            sampling_params=sampling_params if sampling_params is not None else omit,
            extra_body=extra_body,
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        result = cast(SampleResult, result)
        return await resolve_result_payload(
            self._client,
            session_id=self._session_id,
            result=result,
        )

    async def compute_logprobs_async(
        self,
        prompt: Prompt,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[float]:
        """Teacher-force score the given token sequence on the generator, returning the
        log-probability of each prompt token under the current policy.

        The measurement is taken on the generator rather than the trainer's forward pass, so it
        matches the logprobs the sampler would produce at rollout time. Like `sample`, this requires
        a session with a generator replica.

        Raises:
            RuntimeError: if the generator did not return prompt logprobs.
        """
        result = await self.sample_async(
            prompt,
            num_samples=1,
            sampling_params=SamplingParams(return_prompt_logprobs=True, max_tokens=1),
            timeout=timeout,
            interval=interval,
        )
        return _prompt_logprobs_from_result(result)[0]

    async def compute_logprobs_batch_async(
        self,
        prompts: Iterable[Prompt],
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[list[float]]:
        """Teacher-force score each of the given token sequences on the generator, returning the
        log-probability of each prompt token under the current policy.

        This is the batched form of `compute_logprobs`; one list of logprobs is returned per input
        prompt. Like `sample_batch`, this requires a session with a generator replica.

        Raises:
            RuntimeError: if the generator did not return prompt logprobs.
        """
        result = await self.sample_batch_async(
            prompts,
            num_samples=1,
            sampling_params=SamplingParams(return_prompt_logprobs=True, max_tokens=1),
            timeout=timeout,
            interval=interval,
        )
        return _prompt_logprobs_from_result(result)

    async def forward_async(
        self,
        *,
        samples: Iterable[Sample],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardResult:
        body, large_payload_id = await prepare_operation_body(
            self._client,
            session_id=self._session_id,
            body={"samples": list(samples)},
            expected_type=OperationForwardParams,
        )
        samples = cast(list[Any], body["samples"])

        extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
        operation = await self._client.beta.rl.operations.forward(
            self._session_id,
            samples=samples,
            extra_body=extra_body,
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        result = cast(ForwardResult, result)
        return await resolve_result_payload(
            self._client,
            session_id=self._session_id,
            result=result,
        )

    async def forward_backward_async(
        self,
        *,
        samples: Iterable[Sample],
        loss: LossConfigParam,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> ForwardBackwardResult:
        body, large_payload_id = await prepare_operation_body(
            self._client,
            session_id=self._session_id,
            body={"loss": loss, "samples": list(samples)},
            expected_type=OperationForwardBackwardParams,
        )
        samples = cast(list[Any], body["samples"])

        extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
        operation = await self._client.beta.rl.operations.forward_backward(
            self._session_id,
            loss=loss,
            samples=samples,
            extra_body=extra_body,
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(ForwardBackwardResult, result)

    async def custom_forward_backward_async(
        self,
        *,
        samples: Iterable[Sample],
        gradients: Iterable[Gradient],
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> Any:
        body, large_payload_id = await prepare_operation_body(
            self._client,
            session_id=self._session_id,
            body={
                "samples": list(samples),
                "gradients": list(gradients),
            },
            expected_type=OperationCustomForwardBackwardParams,
        )
        samples = cast(list[Any], body["samples"])
        gradients = cast(list[Any], body["gradients"])

        extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
        operation = await self._client.beta.rl.operations.custom_forward_backward(
            self._session_id,
            samples=samples,
            gradients=gradients,
            extra_body=extra_body,
        )
        return await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )

    async def optim_step_async(
        self,
        *,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_UNSPECIFIED",
        adamw_params: AdamwOptimizerParams | None = None,
        max_grad_norm: float | None = None,
        muon_params: MuonOptimizerParams | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> OptimStepResult:
        operation = await self._client.beta.rl.operations.optim_step(
            self._session_id,
            weight_sync_type=weight_sync_type,
            adamw_params=adamw_params if adamw_params is not None else omit,
            max_grad_norm=max_grad_norm if max_grad_norm is not None else omit,
            muon_params=muon_params if muon_params is not None else omit,
        )
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(OptimStepResult, result)

    async def create_inference_checkpoint_async(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> InferenceCheckpointResult:
        operation = await self._client.beta.rl.operations.create_inference_checkpoint(self._session_id)
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(InferenceCheckpointResult, result)

    async def create_training_checkpoint_async(
        self,
        *,
        timeout: float | None = DEFAULT_CHECKPOINT_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> TrainingCheckpointResult:
        operation = await self._client.beta.rl.operations.create_training_checkpoint(self._session_id)
        result = await self._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        return cast(TrainingCheckpointResult, result)

    async def download_checkpoint_async(
        self,
        checkpoint_id: str,
        *,
        variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
        output_dir: str | Path = ".",
    ) -> list[Path]:
        """Download checkpoint files to a local directory.

        Args:
            checkpoint_id: ID of the inference checkpoint to download.
            variant: Download merged full model or adapter-only weights.
            output_dir: Local directory to save files into. Created if it doesn't exist.

        Returns:
            List of paths to the downloaded files.
        """
        dest = Path(output_dir)
        dest.mkdir(parents=True, exist_ok=True)

        response = await self._client.beta.rl.checkpoints.download(
            id=checkpoint_id,
            variant=variant,
        )
        downloaded: list[Path] = []
        for file_info in response.data:
            file_path = dest / file_info.filename
            logger.info("Downloading %s", file_info.filename)
            stream = await self._client.get(
                file_info.url,
                cast_to=httpx.Response,
                stream=True,
                options={"max_retries": _MAX_RETRIES, "headers": {"Authorization": omit}},
            )
            try:
                with file_path.open("wb") as f:
                    async for chunk in stream.aiter_bytes():
                        f.write(chunk)
            finally:
                await stream.aclose()
            downloaded.append(file_path)
            logger.info("Saved %s", file_path)

        return downloaded

    async def stop_async(self) -> Any:
        output = await self._client.beta.rl.sessions.stop(self._session_id)
        if self._event_loop is not None and not self._event_loop.is_running():
            self._event_loop.close()
            self._event_loop = None
        await self._client.close()
        return output
