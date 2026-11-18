"""Tinker training interface backed by a Together RL session."""

from __future__ import annotations

import asyncio
import warnings
import threading
import importlib.util
from uuid import uuid4
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, TypeVar, NoReturn, cast
from functools import partial
from dataclasses import field, dataclass
from collections.abc import Mapping, Callable, Coroutine, Generator
from concurrent.futures import Future

from .. import Sample as WireSample, LossConfig as WireLossConfig, WeightSyncType
from .._loop import _consume_exception, blocking_would_stall_caller
from ._compat import OptimParamsBase, types, tinker, _missing_attribute_error
from ..._types import omit
from ._pending import _deliver, _PendingClient, _wait_shielded
from .._futures import OperationFuture
from ._sampling import SamplingClient, _PublishedWeights
from ._teardown import _Lifecycle
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
from .._operations import DEFAULT_OPERATION_INTERVAL, OperationResponse
from ..clients.session import SessionClient
from ..clients.trainer import _submit_forward_backward, _submit_custom_forward_backward
from ...types.post_training.forward_backward_result import ForwardBackwardResult
from ...types.post_training.training_checkpoint_result import TrainingCheckpointResult
from ...types.post_training.inference_checkpoint_result import InferenceCheckpointResult
from ...types.post_training.operation_custom_forward_backward_params import Gradient

# The client-side loss for forward_backward_custom: (data, autograd leaves) -> (scalar loss
# tensor, metrics). The leaves are torch tensors, typed Any because torch is optional here.
_CustomLossFn = Callable[[list[types.Datum], list[Any]], tuple[Any, dict[str, float]]]

_R = TypeVar("_R")


def _to_forward_backward_request(
    data: list[types.Datum],
    loss_fn: types.LossFnType,
    loss_fn_config: Mapping[str, float | str] | None,
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


def _to_custom_request(
    data: list[types.Datum], loss_fn: Any, loss_type_input: str | None
) -> tuple[list[WireSample], WireLossConfig]:
    """Render one forward_backward_custom call's wire payload, rejecting caller mistakes.

    Validated on the caller's frame for the same reason as its forward_backward sibling.
    """
    if isinstance(loss_fn, tinker.LossHandle):
        raise NotImplementedError("LossHandle losses are not supported; pass a callable loss_fn instead")
    if not data:
        raise ValueError("No data provided")
    if importlib.util.find_spec("torch") is None:
        raise ImportError("PyTorch is not installed. Cannot run forward_backward_custom.")
    # tinker's default None means logprobs.
    if loss_type_input not in (None, "logprobs"):
        raise ValueError(f"Unsupported loss_type_input={loss_type_input!r}; only 'logprobs' is supported")
    prepared = [_with_zero_weights_if_missing(datum) for datum in data]
    return [_to_sample(datum, "cross_entropy") for datum in prepared], _to_loss_config("cross_entropy", None)


def _warn_ignored_publish_args(name: str | None, retry_config: Any, record_stability_info: bool) -> None:
    ignored = [arg for arg, value in (("name", name), ("retry_config", retry_config)) if value is not None]
    if record_stability_info:
        ignored.append("record_stability_info")
    if ignored:
        warnings.warn(
            f"Together ignores {ignored}: weight publish has no named checkpoints, no caller-controlled retries,"
            " and no stability records",
            stacklevel=2,
        )


def _resolve_allow_stale(kind: types.SamplingClientKind, allow_stale: bool) -> bool:
    """Map tinker's sampling-client kind onto Together's staleness gate.

    An ``inflight`` client samples whatever weights the trainer last published, which is what
    ``allow_stale=True`` already means here. A ``snapshot`` keeps the existing default.
    """
    if kind == "inflight":
        return True
    if kind != "snapshot":
        raise ValueError(f"Unknown sampling client kind {kind!r}; expected 'snapshot' or 'inflight'")
    return allow_stale


def _resolve_adam_params(optim_params: Any, adam_params: Any) -> types.AdamParams:
    """Resolve tinker's ``optim_params`` / legacy ``adam_params`` pair to the Adam step Together runs."""
    if optim_params is not None and adam_params is not None:
        raise ValueError("Specify optim_params or legacy adam_params, not both")
    params = optim_params if optim_params is not None else adam_params
    if isinstance(params, types.AdamParams):
        return params
    if params is None:
        raise TypeError("optim_step requires optim_params (types.AdamParams)")
    if isinstance(params, OptimParamsBase):
        raise NotImplementedError(f"Together supports Adam optimizer steps only, not {type(params).__name__}")
    raise TypeError(f"optim_step expects types.AdamParams, got {type(params).__name__}")


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
            "Together ignores ttl_seconds: inference checkpoints are server-assigned UUIDs "
            "with no caller-controlled TTL",
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
    return types.SaveWeightsResponse(path=saved.checkpoint.id)


async def _resolve_save_weights_for_sampler(
    completed: OperationResponse, *, session: SessionClient
) -> types.SaveWeightsForSamplerResponse:
    resolved = await resolve_operation_payload(completed, session=session)
    saved = InferenceCheckpointResult.model_validate(resolved)
    return types.SaveWeightsForSamplerResponse(path=saved.checkpoint.id)


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


async def _settled(future: Future[Any] | None) -> None:
    """Wait for ``future`` to finish without raising its error, which belongs to whoever awaits it."""
    if future is None or future.done():
        return
    waiter = asyncio.wrap_future(future)
    # Retrieved even if the step waiting here is cancelled, so asyncio does not log the
    # failure as never retrieved.
    waiter.add_done_callback(_consume_exception)
    await asyncio.wait([waiter])


@dataclass
class TrainingClient:
    _session: SessionClient
    _lifecycle: _Lifecycle | None = None
    _published_weights: _PublishedWeights = field(default_factory=_PublishedWeights)
    # The latest request this client sent or queued. The next request waits until the server
    # has accepted it (a forward_backward_custom: accumulated its gradients), so the server sees
    # requests in the order they were called.
    _last_request: Future[Any] | None = field(default=None, init=False, repr=False)
    _order_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    # Set when a forward_backward_custom fails. As in tinker, the client then rejects every
    # later training request, so no optimizer step runs without the gradients it expected.
    _custom_loss_error: BaseException | None = field(default=None, init=False, repr=False)

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

    def result(self, timeout: float | None = None) -> TrainingClient:
        """Return this client, for Tinker code that calls ``.result()`` on the client a create call returns.

        The client is already provisioned when the creating call returns, so there is nothing to wait for.
        """
        del timeout
        return self

    async def result_async(self, timeout: float | None = None) -> TrainingClient:
        """See :meth:`result`."""
        del timeout
        return self

    def __await__(self) -> Generator[Any, None, TrainingClient]:
        """Resolve to this client, for Tinker code that awaits what a create call returns."""
        return self.result_async().__await__()

    if not TYPE_CHECKING:  # visible to type checkers, it would let any misspelled attribute through

        def __getattr__(self, name: str) -> NoReturn:
            """Name a tinker method this client leaves out as unsupported, rather than a bare missing attribute."""
            raise _missing_attribute_error(type(self), tinker.TrainingClient, name)

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
        loss_fn_config: Mapping[str, float | str] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Gradient-free scoring pass carrying per-datum logprobs in ``loss_fn_outputs``.

        ``loss_fn`` decides what those logprobs mean: a position it excludes, such as a
        zero-weight one, comes back masked to zero rather than a true log-probability.
        """
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        sent = self._send_forward_backward(
            samples, loss, forward_only=True, return_loss_fn_outputs=return_loss_fn_outputs
        )
        return _deliver(self._session, sent)

    async def forward_async(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: Mapping[str, float | str] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward`."""
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        sent = self._send_forward_backward(
            samples, loss, forward_only=True, return_loss_fn_outputs=return_loss_fn_outputs
        )
        return await _wait_shielded(sent)

    def forward_backward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: Mapping[str, float | str] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Accumulate gradients; per-datum logprobs come back in ``loss_fn_outputs``, as in tinker.

        A position the loss excludes, such as a zero-weight one, comes back masked to zero.
        ``return_loss_fn_outputs=False`` skips them, which shrinks the response and speeds up
        the step for large batches.
        """
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return _deliver(
            self._session, self._send_forward_backward(samples, loss, return_loss_fn_outputs=return_loss_fn_outputs)
        )

    async def forward_backward_async(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: Mapping[str, float | str] | None = None,
        *,
        return_loss_fn_outputs: bool = True,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward_backward`."""
        samples, loss = _to_forward_backward_request(data, loss_fn, loss_fn_config)
        return await _wait_shielded(
            self._send_forward_backward(samples, loss, return_loss_fn_outputs=return_loss_fn_outputs)
        )

    def _send_forward_backward(
        self,
        samples: list[WireSample],
        loss: WireLossConfig,
        *,
        forward_only: bool | None = None,
        return_loss_fn_outputs: bool,
    ) -> Future[OperationFuture[types.ForwardBackwardOutput]]:
        return self._send_in_order(
            partial(
                self._submit_forward_backward_async,
                samples,
                loss,
                forward_only=forward_only,
                return_loss_fn_outputs=return_loss_fn_outputs,
            )
        )

    async def _submit_forward_backward_async(
        self,
        samples: list[WireSample],
        loss: WireLossConfig,
        *,
        forward_only: bool | None = None,
        return_loss_fn_outputs: bool,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        session = self._session
        operation = await session.run_async(
            _submit_forward_backward(
                session,
                samples=samples,
                loss=loss,
                forward_only=forward_only if forward_only is not None else omit,
                return_loss_fn_outputs=return_loss_fn_outputs,
            )
        )
        return OperationFuture(session, operation, partial(_resolve_forward_backward, session=session))

    def forward_backward_custom(
        self,
        data: list[types.Datum],
        loss_fn: _CustomLossFn,
        *,
        loss_type_input: Literal["logprobs"] | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """See :meth:`forward_backward_custom_async`.

        Synchronous code gets the future once the server has accumulated the gradients. Inside a
        running event loop it is returned at once, as in tinker, and the call finishes in the
        background.
        """
        samples, loss = _to_custom_request(data, loss_fn, loss_type_input)
        return _deliver(self._session, self._send_custom_loss(data, samples, loss, loss_fn))

    async def forward_backward_custom_async(
        self,
        data: list[types.Datum],
        loss_fn: _CustomLossFn,
        *,
        loss_type_input: Literal["logprobs"] | None = None,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Two-pass custom loss: forward logprobs → client loss → custom_forward_backward.

        Uses Together's gradient op directly (dL/dlogprobs as-is), not tinker's
        CE-weights surrogate (``weights = -grad``). As in tinker 0.39, the client loss runs
        on a worker thread, and the whole call holds one place in the client's request order:
        a request called while it runs waits until the server has accumulated its gradients.
        That is stricter than tinker, which only waits until they are sent, but no optimizer
        step then runs after gradients the server failed. If the call fails, the client
        rejects every later training request, as tinker does; so does any failure to confirm
        the gradients, such as a network error while polling for them.
        """
        samples, loss = _to_custom_request(data, loss_fn, loss_type_input)
        return await _wait_shielded(self._send_custom_loss(data, samples, loss, loss_fn))

    def _send_custom_loss(
        self,
        data: list[types.Datum],
        samples: list[WireSample],
        loss: WireLossConfig,
        loss_fn: _CustomLossFn,
    ) -> Future[OperationFuture[types.ForwardBackwardOutput]]:
        return self._send_in_order(partial(self._run_custom_loss_async, data, samples, loss, loss_fn))

    async def _run_custom_loss_async(
        self,
        data: list[types.Datum],
        samples: list[WireSample],
        loss: WireLossConfig,
        loss_fn: _CustomLossFn,
    ) -> OperationFuture[types.ForwardBackwardOutput]:
        """Score, run the client loss on a worker thread, and apply its gradients, as one request.

        The loss stays off the shared loop, where it would stall every other handle's polling.
        The request ends only once the server has accumulated the gradients, so a server-side
        failure also rejects the requests queued behind it, before any of them is sent.
        """
        try:
            forward_out = await (await self._submit_scoring_pass_async(samples, loss))
            gradients, metrics = await asyncio.to_thread(_grads_from_forward, data, forward_out, loss_fn)
            applied = await self._submit_custom_grads_async(samples, gradients, metrics, forward_out)
            await applied  # the result is cached, so the caller's own await returns it at once
            return applied
        except BaseException as exc:
            if self._custom_loss_error is None:
                self._custom_loss_error = exc
            raise

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

    def optim_step(
        self,
        optim_params: types.OptimParams | None = None,
        *,
        adam_params: types.AdamParams | None = None,
    ) -> OperationFuture[types.OptimStepResponse]:
        """Apply the accumulated gradients. ``adam_params`` is tinker's legacy alias for ``optim_params``."""
        params = _resolve_adam_params(optim_params, adam_params)
        return _deliver(self._session, self._send_in_order(partial(self._submit_optim_step_async, params)))

    async def optim_step_async(
        self,
        optim_params: types.OptimParams | None = None,
        *,
        adam_params: types.AdamParams | None = None,
    ) -> OperationFuture[types.OptimStepResponse]:
        """See :meth:`optim_step`."""
        params = _resolve_adam_params(optim_params, adam_params)
        return await _wait_shielded(self._send_in_order(partial(self._submit_optim_step_async, params)))

    async def _submit_optim_step_async(self, adam_params: types.AdamParams) -> OperationFuture[types.OptimStepResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.post_training.operations.optim_step(
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
        user_metadata: dict[str, str] | None = None,
    ) -> OperationFuture[types.SaveWeightsResponse]:
        del name, user_metadata
        _warn_ignored_save_state_args(ttl_seconds, overwrite)
        return _deliver(self._session, self._send_in_order(self._submit_save_state_async))

    async def save_state_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
        overwrite: bool = False,
        user_metadata: dict[str, str] | None = None,
    ) -> OperationFuture[types.SaveWeightsResponse]:
        del name, user_metadata
        _warn_ignored_save_state_args(ttl_seconds, overwrite)
        return await _wait_shielded(self._send_in_order(self._submit_save_state_async))

    async def _submit_save_state_async(self) -> OperationFuture[types.SaveWeightsResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.post_training.operations.create_training_checkpoint(
                session.session_id, idempotency_key=str(uuid4())
            )
        )
        return OperationFuture(session, operation, partial(_resolve_save_state, session=session))

    def save_weights_for_sampler(
        self,
        name: str,
        ttl_seconds: int | None = None,
        user_metadata: dict[str, str] | None = None,
    ) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        del name, user_metadata
        _warn_ignored_sampler_ttl(ttl_seconds)
        return _deliver(self._session, self._send_in_order(self._submit_save_weights_for_sampler_async))

    async def save_weights_for_sampler_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
        user_metadata: dict[str, str] | None = None,
    ) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        del name, user_metadata
        _warn_ignored_sampler_ttl(ttl_seconds)
        return await _wait_shielded(self._send_in_order(self._submit_save_weights_for_sampler_async))

    async def _submit_save_weights_for_sampler_async(self) -> OperationFuture[types.SaveWeightsForSamplerResponse]:
        session = self._session
        operation = await session.run_async(
            session._client.post_training.operations.create_inference_checkpoint(
                session.session_id, idempotency_key=str(uuid4())
            )
        )
        return OperationFuture(session, operation, partial(_resolve_save_weights_for_sampler, session=session))

    def save_weights_and_get_sampling_client(
        self,
        name: str | None = None,
        retry_config: Any = None,
        record_stability_info: bool = False,
        kind: types.SamplingClientKind = "snapshot",
        *,
        allow_stale: bool = False,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
    ) -> SamplingClient:
        """Publish the current weights and return a client that samples from them.

        Args:
            name: Ignored, with a warning. Together has no named checkpoints.
            retry_config: Ignored, with a warning. Retries are not caller-controlled.
            record_stability_info: Ignored, with a warning when set. Only ``stable_reinforce``
                reads stability records, and Together does not support it.
            kind: ``"inflight"`` implies ``allow_stale=True``. ``"snapshot"`` keeps ``allow_stale``
                as passed.
            allow_stale: Keep the returned client usable after a later publish.
                This does *not* pin a policy version, because Together has no snapshot checkpoints:
                a stale client samples whatever weights are live at the time of each request.
                Without it, the client goes stale as soon as a later publish is requested, even
                if that publish then fails.
            weight_sync_type: How the publish is performed. ``WEIGHT_SYNC_TYPE_SYNCHRONOUS``
                returns once the new weights are live. ``WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH``
                returns once the sync is queued, which frees the trainer sooner but leaves the
                publish to be paid by whatever samples next.

        Returns:
            SamplingClient: Samples from the weights this call published. Inside a running
            event loop, an awaitable that resolves to that client, as in tinker.
        """
        _warn_ignored_publish_args(name, retry_config, record_stability_info)
        allow_stale = _resolve_allow_stale(kind, allow_stale)
        posted = self._request_publish(weight_sync_type)
        finish = partial(self._finish_publish_async, posted, allow_stale=allow_stale)
        if blocking_would_stall_caller():
            return cast(SamplingClient, _PendingClient(finish, already_sent=True))
        return self._session.run(finish())

    async def save_weights_and_get_sampling_client_async(
        self,
        name: str | None = None,
        retry_config: Any = None,
        record_stability_info: bool = False,
        kind: types.SamplingClientKind = "snapshot",
        *,
        allow_stale: bool = False,
        weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_SYNCHRONOUS",
    ) -> SamplingClient:
        """See :meth:`save_weights_and_get_sampling_client`."""
        _warn_ignored_publish_args(name, retry_config, record_stability_info)
        allow_stale = _resolve_allow_stale(kind, allow_stale)
        posted = self._request_publish(weight_sync_type)
        return await self._finish_publish_async(posted, allow_stale=allow_stale)

    def _request_publish(self, weight_sync_type: WeightSyncType) -> Future[tuple[OperationResponse, int]]:
        """Post the weights sync now, as tinker does, so a step called after the publish cannot reach the server first."""
        return self._send_in_order(partial(self._post_weights_sync_async, weight_sync_type))

    def _send_in_order(self, request: Callable[[], Coroutine[Any, Any, _R]]) -> Future[_R]:
        """Send ``request`` once every request called before it on this client has reached the server.

        tinker runs a client's requests in the order they were called, so a script may call
        ``optim_step`` before awaiting the ``forward_backward`` ahead of it. Each request here
        waits for the one before it to be accepted, or, behind a ``forward_backward_custom``,
        for its gradients to be accumulated, which keeps that order whichever call styles the
        caller mixes. A failed request does not hold back the ones behind it; its
        failure is its caller's to see, except a failed ``forward_backward_custom``'s.
        """
        # Locked: two threads calling at once must still chain, each behind the other.
        with self._order_lock:
            sent = self._session._loop.submit(self._after_earlier(self._last_request, request))
            self._last_request = sent
        return sent

    async def _after_earlier(self, earlier: Future[Any] | None, request: Callable[[], Coroutine[Any, Any, _R]]) -> _R:
        """Send ``request`` once ``earlier`` has reached the server, unless a custom loss failed."""
        await _settled(earlier)
        if self._custom_loss_error is not None:
            raise RuntimeError(
                "a forward_backward_custom on this TrainingClient failed, so, as in tinker, it rejects "
                "every later training request; create a new training client to continue"
            ) from self._custom_loss_error
        return await request()

    async def _post_weights_sync_async(self, weight_sync_type: WeightSyncType) -> tuple[OperationResponse, int]:
        """Request the weights sync and claim the next published version.

        The version moves when the server accepts the request, not when the sync finishes, so
        a snapshot client from an earlier publish stops sampling once new weights are on the
        way, and stays stopped if the sync then fails.
        """
        session = self._session
        operation = await session._client.post_training.operations.weights_sync(
            session.session_id, idempotency_key=str(uuid4()), weight_sync_type=weight_sync_type
        )
        self._published_weights.version += 1
        return operation, self._published_weights.version

    async def _finish_publish_async(
        self,
        posted: Future[tuple[OperationResponse, int]],
        *,
        allow_stale: bool,
    ) -> SamplingClient:
        operation, version = await _wait_shielded(posted)
        session = self._session
        # timeout=None: publish waits as long as the sync takes, unlike Trainer's 300s default.
        await session.run_async(session._submit_and_wait(operation, timeout=None, interval=DEFAULT_OPERATION_INTERVAL))
        return SamplingClient(session, self._published_weights, version, _allow_stale=allow_stale)
