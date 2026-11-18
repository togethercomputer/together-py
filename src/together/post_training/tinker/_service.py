"""Resource provisioning for Together-backed Tinker training clients."""

from __future__ import annotations

import warnings
import threading
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, NoReturn, cast
from functools import partial

from .. import LoraConfig, ModelResources, ModelResourcesClient
from .._loop import run_untracked, submit_untracked, blocking_would_stall_caller
from ._compat import types, tinker, _missing_attribute_error
from ._pending import _Closing, _PendingClient
from ..._client import Together, AsyncTogether
from ._teardown import _Lifecycle, _stop_on_exit, _exit_on_sigterm
from ._training import TrainingClient
from ..clients.session import SessionClient
from ...types.post_training.checkpoint import Checkpoint

# Tinker HTTP-client options that Together's resource client does not honor.
_KNOWN_IGNORED_KWARGS = frozenset(
    {
        "default_headers",
        "default_headers_overrides",
        "default_query",
        "http_client",
        "max_retries",
        "timeout",
    }
)
# Ops/transport knobs a migrator likely tuned on purpose; warn so "work or warn" holds.
# Headers (and header overrides)/query stay silent — boilerplate plumbing nobody verifies after the import swap.
_WARNED_IGNORED_KWARGS = frozenset({"http_client", "max_retries", "timeout"})
# The RL API rejects longer session display names; tinker has no limit.
_MAX_DISPLAY_NAME_LENGTH = 128


def _check_attached(attached: ModelResources, base_model: str) -> None:
    """Reject borrowed resources a LoRA session cannot legitimately run on."""
    if attached.base_model != base_model:
        raise ValueError(
            f"Attached model resources use base model {attached.base_model!r}, not requested {base_model!r}"
        )
    if not attached.lora_enabled:
        raise ValueError("Attached model resources do not support LoRA training sessions")


def _build_lora_config(rank: int, seed: int | None, train_unembed: bool) -> LoraConfig:
    lora_config = LoraConfig(rank=rank)
    if seed is not None:
        lora_config["seed"] = seed
    if not train_unembed:
        lora_config["train_unembed"] = False
    return lora_config


def _start_training_client(
    session: SessionClient,
    model_resources: ModelResourcesClient,
    *,
    owns_model_resources: bool,
) -> TrainingClient:
    lifecycle = _Lifecycle(session, model_resources, owns_model_resources=owns_model_resources)
    _stop_on_exit(lifecycle)
    return TrainingClient(session, lifecycle)


def _check_optimizer(optimizer: types.OptimizerConfig | None) -> None:
    """Allow tinker's default Adam; Together trains LoRA sessions with Adam only."""
    if optimizer is not None and not isinstance(optimizer, types.AdamOptimizerConfig):
        raise NotImplementedError(f"Together trains LoRA sessions with Adam only, not {type(optimizer).__name__}")


def _fit_display_name(display_name: str | None) -> str | None:
    """Truncate a name the RL API would reject, so the run starts instead of failing after provisioning."""
    if display_name is None or len(display_name) <= _MAX_DISPLAY_NAME_LENGTH:
        return display_name
    truncated = display_name[:_MAX_DISPLAY_NAME_LENGTH]
    warnings.warn(
        f"Together limits session display names to {_MAX_DISPLAY_NAME_LENGTH} characters; using {truncated!r}",
        stacklevel=3,  # _fit_display_name -> ServiceClient.__init__ -> caller
    )
    return truncated


def _check_weights_access_token(weights_access_token: str | None) -> None:
    if weights_access_token is not None:
        raise NotImplementedError("Together's Tinker-compatible client does not support weights_access_token")


def _warn_ignored_train_options(train_mlp: bool, train_attn: bool) -> None:
    unsupported = [
        name
        for name, enabled in (
            ("train_mlp", train_mlp),
            ("train_attn", train_attn),
        )
        if not enabled
    ]
    if unsupported:
        warnings.warn(
            f"Together ignores {unsupported}: per-module training selection is not "
            "configurable for mlp/attn, so runs will not reproduce Tinker behavior exactly",
            stacklevel=2,
        )


class ServiceClient:
    """Create training sessions, optionally on existing model resources.

    ``display_name`` names every session this client creates; names longer than 128
    characters are truncated, with a warning. ``user_metadata`` and ``project_id`` are
    accepted for Tinker compatibility but Together does not use them.
    Known Tinker HTTP options (``default_headers``, ``timeout``, …) are accepted and
    ignored because Together's resource client owns its transport policy;
    ``http_client`` / ``max_retries`` / ``timeout`` warn when passed, while
    ``default_headers`` / ``default_headers_overrides`` / ``default_query`` stay
    silent. Any other kwargs raise ``TypeError``. Resources supplied with ``model_resources_id`` are
    borrowed and left running; resources provisioned by this client are owned and
    stopped by :meth:`TrainingClient.close`, by :meth:`close`, or by the interpreter-exit
    fallback. Sessions created by this client are always stopped.

    As in tinker, ``with ServiceClient(...) as service_client:`` closes every training
    client it created on exit. Inside a running event loop that close continues in the
    background instead of blocking the loop.
    """

    def __init__(
        self,
        user_metadata: dict[str, str] | None = None,
        project_id: str | None = None,
        *,
        display_name: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        model_resources_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        del user_metadata, project_id
        unknown = kwargs.keys() - _KNOWN_IGNORED_KWARGS
        if unknown:
            raise TypeError(f"Unsupported ServiceClient kwargs: {sorted(unknown)}")
        ignored = sorted(kwargs.keys() & _WARNED_IGNORED_KWARGS)
        if ignored:
            warnings.warn(
                f"Together's Tinker-compatible client ignores these options: {', '.join(ignored)}",
                stacklevel=2,
            )
        self._display_name = _fit_display_name(display_name)
        self._base_url = base_url
        self._api_key = api_key
        self._model_resources_id = model_resources_id
        self._training_clients: list[TrainingClient] = []
        self._closed = False
        # Guards _closed and _training_clients: close() runs on the caller's thread, creates on the process loop.
        self._lock = threading.Lock()

    def __enter__(self) -> ServiceClient:
        self._check_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc, traceback
        if exc_type is None:
            status: Literal["success", "errored", "interrupted"] = "success"
        elif issubclass(exc_type, Exception):
            status = "errored"
        else:
            status = "interrupted"
        closing = self.close(status)
        if not blocking_would_stall_caller():
            closing.result()

    def close(
        self,
        status: Literal["success", "errored", "interrupted"],
        detail: str | None = None,
    ) -> _Closing:
        """Close every training client this client created, and refuse new ones.

        Together keeps no session-level finish reason, so ``status`` and ``detail`` are
        accepted for tinker compatibility and ignored. The close starts at once; the
        returned object can be awaited or, outside a running event loop, ``.result()``-ed.
        """
        del status, detail
        with self._lock:
            self._closed = True
            clients, self._training_clients = self._training_clients, []
        return _Closing(submit_untracked(_close_training_clients(clients)))

    if not TYPE_CHECKING:  # visible to type checkers, it would let any misspelled attribute through

        def __getattr__(self, name: str) -> NoReturn:
            """Name a tinker method this client leaves out as unsupported, rather than a bare missing attribute."""
            raise _missing_attribute_error(type(self), tinker.ServiceClient, name)

    def _check_open(self) -> None:
        if self._closed:
            raise RuntimeError("ServiceClient is closed")

    def create_lora_training_client(
        self,
        base_model: str,
        rank: int = 32,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        user_metadata: dict[str, str] | None = None,
        optimizer: types.OptimizerConfig | None = None,
    ) -> TrainingClient:
        """Create a LoRA session.

        Per-session ``user_metadata`` is accepted and ignored. ``train_unembed`` is
        forwarded into the session LoRA config. ``train_mlp`` / ``train_attn`` cannot
        be selected independently, so non-default values warn and are ignored.
        ``optimizer`` accepts tinker's default Adam only. Inside a running event loop
        this returns an awaitable that resolves to the client, as in tinker.
        """
        del user_metadata
        self._check_open()
        _check_optimizer(optimizer)
        _warn_ignored_train_options(train_mlp, train_attn)
        # Before handing the work off: signals can only be installed from the main thread,
        # and _provision_async runs on the process loop.
        _exit_on_sigterm()
        provision = partial(self._provision_async, base_model, _build_lora_config(rank, seed, train_unembed))
        if blocking_would_stall_caller():
            return cast(TrainingClient, _PendingClient(provision, already_sent=False))
        return run_untracked(provision())

    def create_training_client_from_state(
        self,
        path: str,
        base_model: str | None = None,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
        optimizer: types.OptimizerConfig | None = None,
    ) -> TrainingClient:
        """Resume a LoRA session from a training checkpoint (weights only).

        ``base_model`` overrides the checkpoint's base model, as in tinker. The server
        rejects one the checkpoint cannot resume on at session start, after the model
        resources are provisioned. ``optimizer`` accepts Adam only. Inside a running
        event loop this returns an awaitable that resolves to the client, as in tinker.
        """
        del user_metadata
        _check_optimizer(optimizer)
        return self._resume_from_checkpoint(path, base_model, weights_access_token, load_optimizer=False)

    def create_training_client_from_state_with_optimizer(
        self,
        path: str,
        base_model: str | None = None,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> TrainingClient:
        """Resume a LoRA session from a training checkpoint, including optimizer state.

        ``base_model`` and running inside an event loop behave as in
        :meth:`create_training_client_from_state`.
        """
        del user_metadata
        return self._resume_from_checkpoint(path, base_model, weights_access_token, load_optimizer=True)

    async def create_training_client_from_state_async(
        self,
        path: str,
        base_model: str | None = None,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
        optimizer: types.OptimizerConfig | None = None,
    ) -> TrainingClient:
        """Async twin of :meth:`create_training_client_from_state`."""
        del user_metadata
        _check_optimizer(optimizer)
        return await self._resume_async(path, base_model, weights_access_token, load_optimizer=False)

    async def create_training_client_from_state_with_optimizer_async(
        self,
        path: str,
        base_model: str | None = None,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> TrainingClient:
        """Async twin of :meth:`create_training_client_from_state_with_optimizer`."""
        del user_metadata
        return await self._resume_async(path, base_model, weights_access_token, load_optimizer=True)

    def create_rest_client(self) -> NoReturn:
        raise tinker.TinkerError("Together's Tinker-compatible client does not support RestClient")

    def create_custom_loss(self, fn: Any, input_ranks: Any) -> NoReturn:
        del fn, input_ranks
        raise tinker.TinkerError(
            "Together's Tinker-compatible client does not support create_custom_loss; "
            "pass a callable loss_fn to forward_backward_custom instead"
        )

    def _resume_from_checkpoint(
        self,
        path: str,
        base_model: str | None,
        weights_access_token: str | None,
        *,
        load_optimizer: bool,
    ) -> TrainingClient:
        self._check_open()
        _check_weights_access_token(weights_access_token)
        if blocking_would_stall_caller():
            # _resume_async repeats these checks and installs the SIGTERM hook when awaited.
            resume = partial(self._resume_async, path, base_model, weights_access_token, load_optimizer=load_optimizer)
            return cast(TrainingClient, _PendingClient(resume, already_sent=False))
        _exit_on_sigterm()
        checkpoint = _describe_training_checkpoint(path, api_key=self._api_key, base_url=self._base_url)
        return run_untracked(self._provision_resumed_async(checkpoint, base_model, load_optimizer=load_optimizer))

    async def _resume_async(
        self, path: str, base_model: str | None, weights_access_token: str | None, *, load_optimizer: bool
    ) -> TrainingClient:
        self._check_open()
        _check_weights_access_token(weights_access_token)
        _exit_on_sigterm()
        checkpoint = await _describe_training_checkpoint_async(path, api_key=self._api_key, base_url=self._base_url)
        return await self._provision_resumed_async(checkpoint, base_model, load_optimizer=load_optimizer)

    async def _provision_resumed_async(
        self, checkpoint: Checkpoint, base_model: str | None, *, load_optimizer: bool
    ) -> TrainingClient:
        return await self._provision_async(
            base_model if base_model is not None else checkpoint.base_model,
            LoraConfig(rank=checkpoint.lora_rank),
            resume_from_checkpoint_id=checkpoint.id,
            load_optimizer=load_optimizer,
        )

    async def create_lora_training_client_async(
        self,
        base_model: str,
        rank: int = 32,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        user_metadata: dict[str, str] | None = None,
        optimizer: types.OptimizerConfig | None = None,
    ) -> TrainingClient:
        """Async twin of :meth:`create_lora_training_client`."""
        del user_metadata
        self._check_open()
        _check_optimizer(optimizer)
        _warn_ignored_train_options(train_mlp, train_attn)
        _exit_on_sigterm()
        return await self._provision_async(base_model, _build_lora_config(rank, seed, train_unembed))

    async def _provision_async(
        self,
        base_model: str,
        lora_config: LoraConfig,
        *,
        resume_from_checkpoint_id: str | None = None,
        load_optimizer: bool = True,
    ) -> TrainingClient:
        self._check_open()
        model_resources_id = self._model_resources_id
        owns_model_resources = model_resources_id is None
        if model_resources_id is None:
            model_resources = await ModelResourcesClient.create_async(
                base_model=base_model,
                api_key=self._api_key,
                base_url=self._base_url,
            )
        else:
            model_resources = await ModelResourcesClient.attach_async(
                model_resources_id=model_resources_id,
                api_key=self._api_key,
                base_url=self._base_url,
            )

        session_kwargs: dict[str, Any] = {"lora_config": lora_config}
        if self._display_name is not None:
            session_kwargs["display_name"] = self._display_name
        if resume_from_checkpoint_id is not None:
            session_kwargs["resume_from_checkpoint_id"] = resume_from_checkpoint_id
            session_kwargs["load_optimizer"] = load_optimizer
        # One release path: everything from here on holds resources that must be given back.
        try:
            if not owns_model_resources:
                _check_attached(await model_resources.retrieve_async(), base_model)
            session = await model_resources.create_session_async(**session_kwargs)
        except BaseException:
            await _Lifecycle(None, model_resources, owns_model_resources=owns_model_resources).aclose(automatic=True)
            raise

        training = _start_training_client(session, model_resources, owns_model_resources=owns_model_resources)
        with self._lock:
            if not self._closed:
                self._training_clients.append(training)
                return training
        # close() ran while this client was being created; release it rather than strand its GPUs.
        try:
            await training.close_async()
        except Exception as exc:  # any stop failure: keep the reason the create was refused
            raise RuntimeError("ServiceClient is closed; releasing the client it was creating failed") from exc
        raise RuntimeError("ServiceClient is closed")


async def _close_training_clients(clients: list[TrainingClient]) -> None:
    """Close each client in turn, so one failure does not strand the rest.

    Raises the first failure, with the other failures attached as notes.
    """
    failures: list[BaseException] = []
    for client in clients:
        try:
            await client.close_async()
        # BaseException: a cancel during one close must not skip releasing the remaining
        # clients' GPUs. The first failure is raised once every client has been tried.
        except BaseException as exc:
            failures.append(exc)
    if failures:
        first = failures[0]
        for other in failures[1:]:
            first.add_note(f"Closing another training client also failed: {other!r}")
        raise first


def _describe_training_checkpoint(
    checkpoint_id: str,
    *,
    api_key: str | None,
    base_url: str | None,
) -> Checkpoint:
    with Together(api_key=api_key, base_url=base_url) as client:
        checkpoint = client.post_training.checkpoints.retrieve(checkpoint_id)
    return _require_training_checkpoint(checkpoint, checkpoint_id)


async def _describe_training_checkpoint_async(
    checkpoint_id: str,
    *,
    api_key: str | None,
    base_url: str | None,
) -> Checkpoint:
    async with AsyncTogether(api_key=api_key, base_url=base_url) as client:
        checkpoint = await client.post_training.checkpoints.retrieve(checkpoint_id)
    return _require_training_checkpoint(checkpoint, checkpoint_id)


def _require_training_checkpoint(checkpoint: Checkpoint, checkpoint_id: str) -> Checkpoint:
    if checkpoint.type != "CHECKPOINT_TYPE_TRAINING":
        raise ValueError(
            f"Checkpoint {checkpoint_id!r} has type {checkpoint.type!r}; "
            "create_training_client_from_state requires CHECKPOINT_TYPE_TRAINING"
        )
    return checkpoint
