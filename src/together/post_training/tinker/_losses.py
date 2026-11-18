"""Tinker loss names mapped onto the shared Together wire contracts."""

from __future__ import annotations

from types import MappingProxyType
from typing import get_args
from collections.abc import Mapping

from ._compat import types
from .._losses import LOSS_SPECS as _WIRE_LOSS_SPECS, LossSpec

LOSS_SPECS: Mapping[types.LossFnType, LossSpec] = MappingProxyType(
    {
        "cross_entropy": _WIRE_LOSS_SPECS["LOSS_TYPE_CROSS_ENTROPY"],
        "importance_sampling": _WIRE_LOSS_SPECS["LOSS_TYPE_IMPORTANCE_SAMPLING"],
        "ppo": _WIRE_LOSS_SPECS["LOSS_TYPE_PPO"],
        "cispo": _WIRE_LOSS_SPECS["LOSS_TYPE_CISPO"],
        "dro": _WIRE_LOSS_SPECS["LOSS_TYPE_DRO"],
    }
)


def loss_spec(loss_fn: types.LossFnType) -> LossSpec:
    """Look up the wire contract for ``loss_fn``.

    Args:
        loss_fn: The tinker loss to look up.

    Returns:
        The spec describing how that loss maps onto the wire.

    Raises:
        NotImplementedError: If ``loss_fn`` is a Tinker loss Together does not support.
        ValueError: If ``loss_fn`` is not a Tinker loss at all.
    """
    if loss_fn in LOSS_SPECS:
        return LOSS_SPECS[loss_fn]
    if loss_fn in get_args(types.LossFnType):
        raise NotImplementedError(
            f"loss_fn {loss_fn!r} is not supported on Together yet; use one of {sorted(LOSS_SPECS)}"
        )
    raise ValueError(f"Unknown loss_fn {loss_fn!r}; expected one of {sorted(LOSS_SPECS)}")
