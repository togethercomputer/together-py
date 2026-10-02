"""Tinker training interface backed by a Together RL session."""

from __future__ import annotations

import warnings
from uuid import uuid4
from types import TracebackType
from typing import Any, Literal
from functools import partial
from dataclasses import field, dataclass
from collections.abc import Callable

from .. import Sample as WireSample, LossConfig as WireLossConfig, WeightSyncType
from ._compat import types
from .._futures import OperationFuture
from ._sampling import SamplingClient, _PublishedWeights
from ._teardown import _Lifecycle
from ....._types import omit
from .._payloads import resolve_operation_payload
from ._converters import (
    _to_sample,
    _to_adam_params,
    _to_loss_config,
    _with_unit_weights,
    _warn_on_binarized_weights,
    _to_forward_backward_output,
    _with_zero_weights_if_missing,
)
from .._operations import OperationResponse
from ..clients.session import SessionClient
from ..clients.trainer import _submit_forward_backward, _submit_custom_forward_backward
from .....types.beta.rl.forward_backward_result import ForwardBackwardResult
from .....types.beta.rl.training_checkpoint_result import TrainingCheckpointResult
from .....types.beta.rl.inference_checkpoint_result import InferenceCheckpointResult
from .....types.beta.rl.operation_custom_forward_backward_params import Gradient

# The client-side loss for forward_backward_custom: (data, autograd leaves) -> (scalar loss
# tensor, metrics). The leaves are torch tensors, typed Any because torch is optional here.
_CustomLossFn = Callable[[list[types.Datum], list[Any]], tuple[Any, dict[str, float]]]


def _to_forward_backward_request(
    data: list[types.Datum],
    loss_fn: types.LossFnType,
    loss_fn_config: dict[str, float] | None,
) -> tuple[list[WireSample], WireLossConfig]:
    """Render one forward_backward call's wire payload, rejecting caller mistakes.

    Kept out of the submission coroutine so a bad ``loss_fn`` or ``Datum`` raises on the
    caller's own frame; deferred, it would surface through the shared process loop, where a
    pinned or stopped session masks it with its own error.
    """
    loss = _to_loss_config(loss_fn, loss_fn_config)
    samples = [_to_sample(datum, loss_fn) for datum in data]
    _warn_on_binarized_weights(samples, loss_fn)
    return samples, loss


def _to_custom_request(data: list[types.Datum], loss_type_input: str) -> tuple[list[WireSample], WireLossConfig]:
    """Render one forward_backward_custom call's wire payload, rejecting caller mistakes.

    Validated on the caller's frame for the same reason as its forward_backward sibling.
    """
    if loss_type_input != "logprobs":
        raise ValueError(f"Unsupported loss_type_input={loss_type_input!r}; only 'logprobs' is supported")
    prepared = [_with_zero_weights_if_missing(datum) for datum in data]
    return [_to_sample(datum, "cross_entropy") for datum in prepared], _to_loss_config("cross_entropy", None)


def _warn_ignored_publish_args(name: str | None, retry_config: Any) -> None:
    ignored = [arg for arg, value in (("name", name), ("retry_config", retry_config)) if value is not None]
    if ignored:
        warnings.warn(
            f"Together ignores {ignored}: weight publish has no named checkpoints and no caller-controlled retries",
            stacklevel=2,
        )


def _warn_ignored_save_state_args(ttl_seconds: int | None, overwrite: bool) -> None:
    ignored: list[str] = []
    if ttl_seconds is not None:
        ignored.append("ttl_seconds")
    if overwrite:
        ignored.append("overwrite")
    if ignored:
        warnings.warn(
            f"Together ignores {ignored}: training checkpoints are server-assigned UUIDs "
            "with no caller-controlled TTL or overwrite",
            stacklevel=2,
        )


def _warn_ignored_sampler_ttl(ttl_seconds: int | None) -> None:
    if ttl_seconds is not None:
        warnings.warn(
            "Together ignores ttl_seconds: inference checkpoints are registered under a "
            "server-assigned model_name with no caller-controlled TTL",
            stacklevel=2,
        )


async def _resolve_forward_backward(
    completed: OperationResponse, *, session: SessionClient
) -> types.ForwardBackwardOutput:
    resolved = await resolve_operation_payload(completed, session=session)
    return _to_forward_backward_output(ForwardBackwardResult.model_validate(resolved))


async def _resolve_optim_step(completed: OperationResponse) -> types.OptimStepResponse:
    # optim_step legitimately completes with no output; there is nothing to read back.
    del completed
    return types.OptimStepResponse()


async def _resolve_save_state(completed: OperationResponse, *, session: SessionClient) -> types.SaveWeightsResponse:
    resolved = await resolve_operation_payload(completed, session=session)
    saved = TrainingCheckpointResult.model_validate(resolved)
    return types.SaveWeightsResponse(path=saved.checkpoint_id)


async def _resolve_save_weights_for_sampler(
    completed: OperationResponse, *, session: SessionClient
) -> types.SaveWeightsForSamplerResponse:
    resolved = await resolve_operation_payload(completed, session=session)
    saved = InferenceCheckpointResult.model_validate(resolved)
    return types.SaveWeightsForSamplerResponse(path=saved.registered_model_name)


async def _resolve_custom_forward_backward(
    completed: OperationResponse,
    *,
    metrics: dict[str, float],
    loss_fn_outputs: list[dict[str, types.TensorData]],
) -> types.ForwardBackwardOutput:
    # Together's CustomForwardBackwardResult carries no fields; client metrics are the truth.
    del completed
    return types.ForwardBackwardOutput(
        loss_fn_output_type="",
        loss_fn_outputs=loss_fn_outputs,
        metrics=dict(metrics),
    )


def _grads_from_forward(
    data: list[types.Datum],
    forward_out: types.ForwardBackwardOutput,
    loss_fn: _CustomLossFn,
) -> tuple[list[Gradient], dict[str, float]]:
    """Run the client loss on the forward pass's logprobs, on the current thread."""
    if len(forward_out.loss_fn_outputs) != len(data):
        raise RuntimeError(
            f"forward returned {len(forward_out.loss_fn_outputs)} logprob arrays for {len(data)} samples"
        )
    logprobs_list = [list(out["logprobs"].data) for out in forward_out.loss_fn_outputs]
    return _custom_loss_grads(data, logprobs_list, loss_fn)


def _custom_loss_grads(
    data: list[types.Datum],
    logprobs_list: list[Any],
    loss_fn: _CustomLossFn,
) -> tuple[list[Gradient], dict[str, float]]:
    """Run the client loss on autograd leaves; return wire grads + metrics."""
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - depends on optional torch install
        raise ImportError("PyTorch is not installed. Cannot run forward_backward_custom.") from exc

    leaves = [torch.tensor(lp, dtype=torch.float32, requires_grad=True) for lp in logprobs_list]
    loss, metrics = loss_fn(data, leaves)
    if not isinstance(loss, torch.Tensor) or loss.ndim != 0:
        raise ValueError(f"custom loss_fn must return a scalar tensor, got {loss!r}")
    loss.backward()

    gradients: list[Gradient] = []
    for logprob in leaves:
        if logprob.grad is None:
            raise ValueError("No gradient computed for logprob tensor")
        # Gradient.dtype speaks the proto vocabulary, not TensorData's short names.
        gradients.append(Gradient(data=logprob.grad.tolist(), dtype="D_TYPE_FLOAT32"))

    return gradients, {k: float(v) for k, v in metrics.items()}


@dataclass
class TrainingClient:
    _session: SessionClient
    _lifecycle: _Lifecycle | None = None
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)

    def __post_init__(self) -> None:
        if self._lifecycle is None:
            self._lifecycle = _Lifecycle(self._session)

    def __enter__(self) -> TrainingClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    async def __aenter__(self) -> TrainingClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close_async()

    def close(self) -> None:
        assert self._lifecycle is not None
        self._lifecycle.close()

    async def close_async(self) -> None:
        assert self._lifecycle is not None
        await self._lifecycle.aclose()

    def forward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Gradient-free scoring pass carrying per-datum logprobs in ``loss_fn_outputs``.

        ``loss_fn`` decides what those logprobs mean: a position it excludes, such as a
        zero-weight one, comes back masked to zero rather than a true log-probability.
        """
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return self._session.run(
            self._submit_forward_backward_async(
                samples, loss, forward_only=True, return_loss_fn_outputs=return_loss_fn_outputs
            )
        )

    async def forward_async(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward`."""
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return await self._submit_forward_backward_async(
            samples, loss, forward_only=True, return_loss_fn_outputs=return_loss_fn_outputs
        )

    def forward_backward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
        *,
        return_loss_fn_outputs: bool | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Set ``return_loss_fn_outputs`` to read per-datum logprobs back with the update."""
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return self._session.run(
            self._submit_forward_backward_async(samples, loss, return_loss_fn_outputs=return_loss_fn_outputs)
        )

    async def forward_backward_async(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
        *,
        return_loss_fn_outputs: bool | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward_backward`."""
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return await self._submit_forward_backward_async(
            samples,
            loss,
            return_loss_fn_outputs=return_loss_fn_outputs,
        )

    async def _submit_forward_backward_async(
        self,
        samples: list[WireSample],
        loss: WireLossConfig,
        *,
        forward_only: bool | None = None,
        return_loss_fn_outputs: bool | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        session = self._session
        operation = await session.run_async(
            _submit_forward_backward(
                session,
                samples=samples,
                loss=loss,
                forward_only=forward_only if forward_only is not None else omit,
                return_loss_fn_outputs=return_loss_fn_outputs if return_loss_fn_outputs is not None else omit,
            )
        )
        return OperationFuture(session, operation, partial(_resolve_forward_backward, session=session))

    def forward_backward_custom(
        self,
        data: list[types.Datum],
        loss_fn: _CustomLossFn,
        *,
        loss_type_input: Literal["logprobs"] = "logprobs",
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward_backward_custom_async`."""
        # The two loop hops stay separate so the torch backward in between runs on the
        # calling thread, not the shared session loop, where it would stall every other
        # handle's in-flight polling.
        samples, loss = _to_custom_request(data, loss_type_input)
        forward_out = self._session.run(self._submit_scoring_pass_async(samples, loss)).result()
        gradients, metrics = _grads_from_forward(data, forward_out, loss_fn)
        return self._session.run(self._submit_custom_grads_async(samples, gradients, metrics, forward_out))

    async def forward_backward_custom_async(
        self,
        data: list[types.Datum],
        loss_fn: _CustomLossFn,
        *,
        loss_type_input: Literal["logprobs"] = "logprobs",
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Two-pass custom loss: forward logprobs → client loss → custom_forward_backward.

        Uses Together's gradient op directly (dL/dlogprobs as-is), not tinker's
        CE-weights surrogate (``weights = -grad``). The torch backward runs on the
        caller's own frame, like tinker's.
        """
        samples, loss = _to_custom_request(data, loss_type_input)
        forward_out = await (await self._submit_scoring_pass_async(samples, loss))
        gradients, metrics = _grads_from_forward(data, forward_out, loss_fn)
        return await self._submit_custom_grads_async(samples, gradients, metrics, forward_out)

    async def _submit_scoring_pass_async(
        self, samples: list[WireSample], loss: WireLossConfig
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        return await self._submit_forward_backward_async(
            [_with_unit_weights(sample) for sample in samples],
            loss,
            forward_only=True,
            return_loss_fn_outputs=True,
        )

    async def _submit_custom_grads_async(
        self,
        samples: list[WireSample],
        gradients: list[Gradient],
        metrics: dict[str, float],
        forward_out: types.ForwardBackwardOutput,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        session = self._session
        operation = await session.run_async(
            _submit_custom_forward_backward(session, samples=samples, gradients=gradients)
        )
        resolve = partial(
            _resolve_custom_forward_backward, metrics=metrics, loss_fn_outputs=forward_out.loss_fn_outputs
        )
        return OperationFuture(session, operation, resolve)

    def optim_step(self, adam_params: types.AdamParams) -> OperationFuture[types.OptimStepResponse]:
        # Drives its own twin, unlike the pairs above: there is nothing to validate on the
        # caller's frame first, so there is no shared submit helper to split out.
        return self._session.run(self.optim_step_async(adam_params))

    async def optim_step_async(self, adam_params: types.AdamParams) -> OperationFuture[types.OptimStepResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.beta.rl.operations.optim_step(
                session.session_id,
                idempotency_key=str(uuid4()),
                adam_params=_to_adam_params(adam_params),
            )
        )
        return OperationFuture(session, operation, _resolve_optim_step)

    def save_state(
        self,
        name: str,
        ttl_seconds: int | None = None,
        overwrite: bool = False,
    ) -> OperationFuture[types.SaveWeightsResponse]:
        del name
        _warn_ignored_save_state_args(ttl_seconds, overwrite)
        return self._session.run(self._submit_save_state_async())

    async def save_state_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
        overwrite: bool = False,
    ) -> OperationFuture[types.SaveWeightsResponse]:
        del name
        _warn_ignored_save_state_args(ttl_seconds, overwrite)
        return await self._submit_save_state_async()

    async def _submit_save_state_async(self) -> OperationFuture[types.SaveWeightsResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.beta.rl.operations.create_training_checkpoint(
                session.session_id, idempotency_key=str(uuid4())
            )
        )
        return OperationFuture(session, operation, partial(_resolve_save_state, session=session))

    def save_weights_for_sampler(
        self,
        name: str,
        ttl_seconds: int | None = None,
    ) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        del name
        _warn_ignored_sampler_ttl(ttl_seconds)
        return self._session.run(self._submit_save_weights_for_sampler_async())

    async def save_weights_for_sampler_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
    ) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        del name
        _warn_ignored_sampler_ttl(ttl_seconds)
        return await self._submit_save_weights_for_sampler_async()

    async def _submit_save_weights_for_sampler_async(self) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.beta.rl.operations.create_inference_checkpoint(
                session.session_id, idempotency_key=str(uuid4())
            )
        )
        return OperationFuture(session, operation, partial(_resolve_save_weights_for_sampler, session=session))

    def save_weights_and_get_sampling_client(
        self,
        name: str | None = None,
        retry_config: Any = None,
        *,
        allow_stale: bool = False,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
    ) -> SamplingClient:
        """Publish the current weights and return a client that samples from them.

        Args:
            name: Ignored, with a warning. Together has no named checkpoints.
            retry_config: Ignored, with a warning. Retries are not caller-controlled.
            allow_stale: Keep the returned client usable after a later publish.
                This does *not* pin a policy version, because Together has no snapshot checkpoints:
                a stale client samples whatever weights are live at the time of each request.
            weight_sync_type: How the publish is performed. ``WEIGHT_SYNC_TYPE_SYNCHRONOUS``
                returns once the new weights are live. ``WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH``
                returns once the sync is queued, which frees the trainer sooner but leaves the
                publish to be paid by whatever samples next.

        Returns:
            SamplingClient: Samples from the weights this call published.
        """
        _warn_ignored_publish_args(name, retry_config)
        return self._session.run(
            self._publish_weights_async(allow_stale=allow_stale, weight_sync_type=weight_sync_type)
        )

    async def save_weights_and_get_sampling_client_async(
        self,
        name: str | None = None,
        retry_config: Any = None,
        *,
        allow_stale: bool = False,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
    ) -> SamplingClient:
        """See :meth:`save_weights_and_get_sampling_client`."""
        _warn_ignored_publish_args(name, retry_config)
        return await self._publish_weights_async(allow_stale=allow_stale, weight_sync_type=weight_sync_type)

    async def _publish_weights_async(
        self,
        *,
        allow_stale: bool,
        weight_sync_type: WeightSyncType,
    ) -> SamplingClient:
        session = self._session
        # timeout=None: publish waits as long as the sync takes, unlike Trainer's 300s default.
        await session.trainer.weights_sync_async(weight_sync_type=weight_sync_type, timeout=None)
        self._published_weights.version += 1
        return SamplingClient(
            session, self._published_weights, self._published_weights.version, _allow_stale=allow_stale
        )
