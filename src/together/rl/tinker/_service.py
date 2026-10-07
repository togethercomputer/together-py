"""Resource provisioning for Together-backed Tinker training clients."""

from __future__ import annotations

import warnings
from typing import Any, NoReturn

from .. import LoraConfig, ModelResources, ModelResourcesClient
from .._loop import run_untracked
from ._compat import tinker
from ._teardown import _Lifecycle, _stop_on_exit, _exit_on_sigterm
from ._training import TrainingClient
from ....._client import Together
from ..clients.session import SessionClient
from .....types.beta.rl.checkpoint import Checkpoint

# Tinker HTTP-client options that Together's resource client does not honor.
_KNOWN_IGNORED_KWARGS = frozenset(
    {
        "default_headers",
        "default_query",
        "http_client",
        "max_retries",
        "timeout",
    }
)
# Ops/transport knobs a migrator likely tuned on purpose; warn so "work or warn" holds.
# Headers/query stay silent — boilerplate plumbing nobody verifies after the import swap.
_WARNED_IGNORED_KWARGS = frozenset({"http_client", "max_retries", "timeout"})


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

    ``user_metadata`` and ``project_id`` are accepted for Tinker compatibility but
    Together does not use them. Known Tinker HTTP options (``default_headers``,
    ``timeout``, …) are accepted and ignored because Together's resource client owns
    its transport policy; ``http_client`` / ``max_retries`` / ``timeout`` warn when
    passed, while ``default_headers`` / ``default_query`` stay silent. Any other
    kwargs raise ``TypeError``. Resources supplied with ``model_resources_id`` are
    borrowed and left running; resources provisioned by this client are owned and
    stopped by :meth:`TrainingClient.close` or the interpreter-exit fallback.
    Sessions created by this client are always stopped.
    """

    def __init__(
        self,
        user_metadata: dict[str, str] | None = None,
        project_id: str | None = None,
        *,
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
        self._base_url = base_url
        self._api_key = api_key
        self._model_resources_id = model_resources_id

    def create_lora_training_client(
        self,
        base_model: str,
        rank: int = 32,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        user_metadata: dict[str, str] | None = None,
    ) -> TrainingClient:
        """Create a LoRA session.

        Per-session ``user_metadata`` is accepted and ignored. ``train_unembed`` is
        forwarded into the session LoRA config. ``train_mlp`` / ``train_attn`` cannot
        be selected independently, so non-default values warn and are ignored.
        """
        del user_metadata
        _warn_ignored_train_options(train_mlp, train_attn)
        # Before handing the work off: signals can only be installed from the main thread,
        # and _provision_async runs on the process loop.
        _exit_on_sigterm()
        return run_untracked(self._provision_async(base_model, _build_lora_config(rank, seed, train_unembed)))

    def create_training_client_from_state(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> TrainingClient:
        """Resume a LoRA session from a training checkpoint (weights only)."""
        return self._resume_from_checkpoint(path, user_metadata, weights_access_token, load_optimizer=False)

    def create_training_client_from_state_with_optimizer(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> TrainingClient:
        """Resume a LoRA session from a training checkpoint, including optimizer state."""
        return self._resume_from_checkpoint(path, user_metadata, weights_access_token, load_optimizer=True)

    def create_rest_client(self) -> NoReturn:
        raise tinker.TinkerError("Together's Tinker-compatible client does not support RestClient")

    def _resume_from_checkpoint(
        self,
        path: str,
        user_metadata: dict[str, str] | None,
        weights_access_token: str | None,
        *,
        load_optimizer: bool,
    ) -> TrainingClient:
        del user_metadata
        if weights_access_token is not None:
            raise NotImplementedError("Together's Tinker-compatible client does not support weights_access_token")
        checkpoint = _describe_training_checkpoint(path, api_key=self._api_key, base_url=self._base_url)
        rank = checkpoint.lora_rank
        return self._open_lora_training_client(
            checkpoint.base_model,
            LoraConfig(rank=rank),
            resume_from_checkpoint_id=checkpoint.id,
            load_optimizer=load_optimizer,
        )

    def _open_lora_training_client(
        self,
        base_model: str,
        lora_config: LoraConfig,
        *,
        resume_from_checkpoint_id: str | None = None,
        load_optimizer: bool = True,
    ) -> TrainingClient:
        _exit_on_sigterm()
        return run_untracked(
            self._provision_async(
                base_model,
                lora_config,
                resume_from_checkpoint_id=resume_from_checkpoint_id,
                load_optimizer=load_optimizer,
            )
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
    ) -> TrainingClient:
        """Async twin of :meth:`create_lora_training_client`."""
        del user_metadata
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

        return _start_training_client(session, model_resources, owns_model_resources=owns_model_resources)


def _describe_training_checkpoint(
    checkpoint_id: str,
    *,
    api_key: str | None,
    base_url: str | None,
) -> Checkpoint:
    with Together(api_key=api_key, base_url=base_url) as client:
        checkpoint = client.beta.rl.checkpoints.retrieve(checkpoint_id)
    if checkpoint.type != "CHECKPOINT_TYPE_TRAINING":
        raise ValueError(
            f"Checkpoint {checkpoint_id!r} has type {checkpoint.type!r}; "
            "create_training_client_from_state requires CHECKPOINT_TYPE_TRAINING"
        )
    return checkpoint
