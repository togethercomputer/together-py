"""Tinker loss names mapped onto the shared Together wire contracts."""

from __future__ import annotations

from types import MappingProxyType
from collections.abc import Mapping

from together.lib.beta.rl._losses import LOSS_SPECS as _WIRE_LOSS_SPECS, LossSpec

from ._compat import types

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
        ValueError: If ``loss_fn`` is not a loss name the wrapper maps.
    """
    if loss_fn not in LOSS_SPECS:
        raise ValueError(f"Unknown loss_fn {loss_fn!r}; expected one of {sorted(LOSS_SPECS)}")
    return LOSS_SPECS[loss_fn]
