from __future__ import annotations

import os
import re
import sys
import logging
from typing import Any, Set, Dict

logger: logging.Logger = logging.getLogger("together")

TOGETHER_LOG = os.environ.get("TOGETHER_LOG")

WARNING_MESSAGES_ONCE: Set[str] = set()


def _console_log_level() -> str | None:
    if TOGETHER_LOG in ["debug", "info"]:
        return TOGETHER_LOG
    else:
        return None


def logfmt(props: Dict[str, Any]) -> str:
    def fmt(key: str, val: Any) -> str:
        # Handle case where val is a bytes or bytesarray
        if hasattr(val, "decode"):
            val = val.decode("utf-8")
        # Check if val is already a string to avoid re-encoding into ascii.
        if not isinstance(val, str):
            val = str(val)
        if re.search(r"\s", val):
            val = repr(val)
        # key should already be a string
        if re.search(r"\s", key):
            key = repr(key)
        return "{key}={val}".format(key=key, val=val)

    return " ".join([fmt(key, val) for key, val in sorted(props.items())])


def log_debug(message: str | Any, **params: Any) -> None:
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)  # noqa
    logger.debug(msg)


def log_info(message: str | Any, **params: Any) -> None:
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)  # noqa
    logger.info(msg)


def log_warn(message: str | Any, **params: Any) -> None:
    msg = logfmt(dict(message=message, **params))
    print(msg, file=sys.stderr)  # noqa
    logger.warning(msg)


def log_warn_once(message: str | Any, **params: Any) -> None:
    msg = logfmt(dict(message=message, **params))
    if msg not in WARNING_MESSAGES_ONCE:
        print(msg, file=sys.stderr)  # noqa
        logger.warning(msg)
        WARNING_MESSAGES_ONCE.add(msg)
