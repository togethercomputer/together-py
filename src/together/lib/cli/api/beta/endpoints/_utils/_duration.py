from __future__ import annotations

import re
from typing import NoReturn
from decimal import ROUND_HALF_EVEN, Decimal

from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils._console import console

# protobuf JSON Duration: optional minus, seconds, optional fractional nanos, suffix "s".
_PROTO_DURATION_RE = re.compile(r"^-?(?:0|[1-9]\d{0,11})(?:\.\d{1,9})?s$")
_BARE_SECONDS_RE = re.compile(r"^-?(?:0|[1-9]\d{0,11})(?:\.\d{1,9})?$")
# Go-style number+unit tokens. Longer units first so "ms" is not parsed as "m" + "s".
_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)(ns|us|µs|μs|ms|h|m|s)")

_NS_PER_UNIT = {
    "ns": Decimal(1),
    "us": Decimal(1_000),
    "µs": Decimal(1_000),
    "μs": Decimal(1_000),
    "ms": Decimal(1_000_000),
    "s": Decimal(1_000_000_000),
    "m": Decimal(60_000_000_000),
    "h": Decimal(3_600_000_000_000),
}
_NS_PER_SECOND = 1_000_000_000


def normalize_duration(value: str | None, *, option_name: str) -> str | None:
    """Normalize a CLI duration to protobuf JSON Duration (seconds, suffix `s`).

    Accepts proto JSON (`30s`, `1.5s`), bare seconds (`30`), and Go-style units
    (`10m`, `1h`, `10m30s`, `1ms`). Other spellings are rejected locally so the
    server codec never has to.
    """
    if value is None:
        return None
    value = value.strip()
    if not value:
        _reject(option_name, value)
    if _PROTO_DURATION_RE.fullmatch(value):
        return value
    if _BARE_SECONDS_RE.fullmatch(value):
        return f"{value}s"
    converted = _from_human_units(value)
    if converted is not None:
        return converted
    _reject(option_name, value)


def _reject(option_name: str, value: str) -> NoReturn:
    console.print(f"Error: {option_name} must be a duration, e.g. 30, 30s, or 10m (got {value!r}).")
    raise CliDiagnosticExit(f"Invalid duration for {option_name}")


def _from_human_units(value: str) -> str | None:
    sign = 1
    rest = value
    if rest.startswith("-"):
        sign = -1
        rest = rest[1:]
    if not rest:
        return None
    total_ns = Decimal(0)
    pos = 0
    for match in _TOKEN_RE.finditer(rest):
        if match.start() != pos:
            return None
        amount = Decimal(match.group(1))
        total_ns += amount * _NS_PER_UNIT[match.group(2)]
        pos = match.end()
    if pos != len(rest) or pos == 0:
        return None
    nanos = int(total_ns.to_integral_value(rounding=ROUND_HALF_EVEN))
    return _format_proto_duration(sign * nanos)


def _format_proto_duration(signed_ns: int) -> str:
    sign = "-" if signed_ns < 0 else ""
    ns = abs(signed_ns)
    seconds, nanos = divmod(ns, _NS_PER_SECOND)
    if nanos == 0:
        return f"{sign}{seconds}s"
    frac = f"{nanos:09d}".rstrip("0")
    return f"{sign}{seconds}.{frac}s"
