from __future__ import annotations

from typing import Any, Iterable, cast
from dataclasses import dataclass

from .session import DEFAULT_OPERATION_TIMEOUT, DEFAULT_OPERATION_INTERVAL, SessionClient
from ....._types import omit
from .._payloads import prepare_operation_body, resolve_result_payload
from .....types.beta.rl.sample_result import SampleResult
from .....types.beta.rl.sampling_params import SamplingParams
from .....types.beta.rl.sample_operation import Output as SampleBatchResult
from .....types.beta.rl.model_input_param import ModelInput
from .....types.beta.rl.operation_sample_params import OperationSampleParams


def _prompt_logprobs_from_results(results: Iterable[SampleResult]) -> list[list[float]]:
    logprobs: list[list[float]] = []
    for index, result in enumerate(results):
        if result.prompt_logprobs is None:
            msg = (
                f"Sample result for prompt {index} did not include prompt logprobs; the generator may not support them"
            )
            raise RuntimeError(msg)
        logprobs.append(result.prompt_logprobs)
    return logprobs


@dataclass(frozen=True)
class SamplingClient:
    _session: SessionClient

    @property
    def session_id(self) -> str:
        return self._session.session_id

    def sample(
        self,
        prompt: ModelInput,
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        prompt_logprobs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        return self._session.run(
            self.sample_async(
                prompt,
                num_samples=num_samples,
                sampling_params=sampling_params,
                prompt_logprobs=prompt_logprobs,
                timeout=timeout,
                interval=interval,
            )
        )

    async def sample_async(
        self,
        prompt: ModelInput,
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        prompt_logprobs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> SampleResult:
        results = await self.sample_batch_async(
            [prompt],
            num_samples=num_samples,
            sampling_params=sampling_params,
            prompt_logprobs=prompt_logprobs,
            timeout=timeout,
            interval=interval,
        )
        return results[0]

    def sample_batch(
        self,
        prompts: Iterable[ModelInput],
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        prompt_logprobs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[SampleResult]:
        return self._session.run(
            self.sample_batch_async(
                prompts,
                num_samples=num_samples,
                sampling_params=sampling_params,
                prompt_logprobs=prompt_logprobs,
                timeout=timeout,
                interval=interval,
            )
        )

    async def sample_batch_async(
        self,
        prompts: Iterable[ModelInput],
        num_samples: int | None = None,
        sampling_params: SamplingParams | None = None,
        *,
        prompt_logprobs: bool | None = None,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[SampleResult]:
        model_inputs = list(prompts)
        body: dict[str, Any] = {"model_inputs": model_inputs}
        if sampling_params is not None:
            body["sampling_params"] = sampling_params
        if num_samples is not None:
            body["num_samples"] = num_samples
        if prompt_logprobs is not None:
            body["prompt_logprobs"] = prompt_logprobs

        body, large_payload_id = await prepare_operation_body(
            self._session._client,
            session_id=self._session._session_id,
            body=body,
            expected_type=OperationSampleParams,
        )
        model_inputs = cast("list[ModelInput]", body["model_inputs"])

        extra_body = {"payload_id": large_payload_id} if large_payload_id is not None else None
        operation = await self._session._client.beta.rl.operations.sample(
            self._session._session_id,
            model_inputs=model_inputs,
            num_samples=body.get("num_samples", omit),
            sampling_params=body.get("sampling_params", omit),
            prompt_logprobs=body.get("prompt_logprobs", omit),
            extra_body=extra_body,
        )
        result = await self._session._submit_and_wait(
            operation,
            timeout=timeout,
            interval=interval,
        )
        resolved = await resolve_result_payload(
            self._session._client,
            session_id=self._session._session_id,
            result=cast(SampleBatchResult, result),
        )
        return resolved.results

    def compute_logprobs(
        self,
        prompt: ModelInput,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[float]:
        return self._session.run(self.compute_logprobs_async(prompt, timeout=timeout, interval=interval))

    async def compute_logprobs_async(
        self,
        prompt: ModelInput,
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[float]:
        logprobs = await self.compute_logprobs_batch_async(
            [prompt],
            timeout=timeout,
            interval=interval,
        )
        return logprobs[0]

    def compute_logprobs_batch(
        self,
        prompts: Iterable[ModelInput],
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[list[float]]:
        return self._session.run(self.compute_logprobs_batch_async(prompts, timeout=timeout, interval=interval))

    async def compute_logprobs_batch_async(
        self,
        prompts: Iterable[ModelInput],
        *,
        timeout: float | None = DEFAULT_OPERATION_TIMEOUT,
        interval: float = DEFAULT_OPERATION_INTERVAL,
    ) -> list[list[float]]:
        results = await self.sample_batch_async(
            prompts,
            num_samples=1,
            sampling_params=SamplingParams(max_tokens=1),
            prompt_logprobs=True,
            timeout=timeout,
            interval=interval,
        )
        return _prompt_logprobs_from_results(results)
