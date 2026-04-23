from __future__ import annotations

import io
import os
from typing import cast
from unittest.mock import patch

import pytest
from attr import dataclass


@dataclass
class Result:
    exit_code: int
    output: str
    err_out: str
    out_out: str


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"


class CliRunner:
    def __init__(self, capsys: pytest.CaptureFixture[str]):
        self.env = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}
        self.capsys = capsys

    def invoke(self, iargs: list[str], *, input: str | None = None) -> Result:
        from together.lib.cli import app

        try:
            # TODO: handle input
            # Sync App.__call__ uses asyncio.run for async commands; must not run under
            # pytest-asyncio's loop (RuntimeError: asyncio.run() cannot be called from a running event loop).
            with patch("sys.stdin", io.StringIO(input)):
                with patch.dict(os.environ, self.env, clear=False):
                    app.meta(iargs)

            output = self.capsys.readouterr()
            err_out = output.err
            out_out = output.out

            return Result(
                exit_code=0,
                err_out=err_out,
                out_out=out_out,
                output=out_out + err_out,
            )
        except SystemExit as e:
            # Cyclopts ends successful runs with sys.exit(0). readouterr() clears the
            # buffer; only call it once (meta + table print go to stdout).
            captured = self.capsys.readouterr()
            return Result(
                exit_code=cast(int, e.code),
                err_out=captured.err,
                out_out=captured.out,
                output=captured.out + captured.err,
            )
