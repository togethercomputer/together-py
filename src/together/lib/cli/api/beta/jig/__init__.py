"""Jig CLI - deployment tool for Together AI."""

from __future__ import annotations

import os
import sys
from typing import Annotated

from cyclopts import App, Parameter

import together


def register_jig(parent: App) -> None:
    """Register the jig sub-app. Forwards to the legacy Click-based Jig when a subcommand is used."""
    jig_app = parent.command(App(name="jig", help="Jig commands - deploy and manage containers"))

    @jig_app.default
    def run_jig(
        *tokens: Annotated[list[str], Parameter(show=False, allow_leading_hyphen=True)],
    ) -> None:
        from together.lib.cli.api.beta.jig.jig_click import main as jig_main

        sys.argv = ["together", "beta", "jig"] + list(tokens)
        # Jig runs as a nested app so it doesn't receive the root-injected client; create from env.
        client = together.Together(api_key=os.getenv("TOGETHER_API_KEY"))
        jig_main(obj=client)
