"""Resource provisioning for Together-backed Tinker training clients."""

from __future__ import annotations

import logging
import warnings
from typing import Any

from .. import ModelResourcesClient
from ._teardown import _Lifecycle, _stop_on_exit, _exit_on_sigterm, _log_release_hint
from ._training import TrainingClient
from .....types.beta.rl.lora_config_param import LoraConfigParam

logger = logging.getLogger("together")

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
                f"Together ignores {ignored}: the resource client owns its transport "
                "policy, so these Tinker HTTP options have no effect",
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

        Per-session ``user_metadata`` is accepted and ignored. Together cannot select
        trainable LoRA modules independently, so non-default ``train_*`` values warn.
        """
        del user_metadata
        unsupported = [
            name
            for name, enabled in (
                ("train_mlp", train_mlp),
                ("train_attn", train_attn),
                ("train_unembed", train_unembed),
            )
            if enabled is not True
        ]
        if unsupported:
            warnings.warn(
                f"Together ignores {unsupported}: per-module training selection is not "
                "configurable, so runs will not reproduce Tinker behavior exactly",
                stacklevel=2,
            )

        _exit_on_sigterm()
        owns_model_resources = self._model_resources_id is None
        if owns_model_resources:
            model_resources = ModelResourcesClient.create(
                base_model=base_model,
                api_key=self._api_key,
                base_url=self._base_url,
            )
        else:
            assert self._model_resources_id is not None
            model_resources = ModelResourcesClient.attach(
                model_resources_id=self._model_resources_id,
                api_key=self._api_key,
                base_url=self._base_url,
            )
            attached = model_resources.retrieve()
            if attached.base_model != base_model:
                model_resources.detach()
                raise ValueError(
                    f"Attached model resources use base model {attached.base_model!r}, not requested {base_model!r}"
                )
            if not attached.lora_enabled:
                model_resources.detach()
                raise ValueError("Attached model resources do not support LoRA training sessions")

        lora_config = LoraConfigParam(rank=rank)
        if seed is not None:
            lora_config["seed"] = seed
        try:
            session = model_resources.create_session(lora_config=lora_config)
        except BaseException:
            try:
                if owns_model_resources:
                    model_resources.stop()
                else:
                    model_resources.detach()
            except BaseException as exc:
                if owns_model_resources:
                    _log_release_hint(model_resources)
                else:
                    logger.error(
                        "[model-resources:%s] failed to detach after session creation failed: %r",
                        model_resources.model_resources_id,
                        exc,
                    )
            raise

        lifecycle = _Lifecycle(
            session,
            model_resources,
            owns_model_resources=owns_model_resources,
        )
        _stop_on_exit(lifecycle)
        return TrainingClient(session, lifecycle)
