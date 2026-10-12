"""`tg switch` — RFC 8693 token exchange for a project-scoped access token. See `together.lib.cli.auth`."""

from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.auth import TogetherAuth, CredentialStore, StoredCredentials, note_credentials_path
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.api.projects.list import print_project_list
from together.lib.cli.utils._project_scope import load_projects, select_project


async def switch(
    project_id: Annotated[
        str | None,
        Parameter(help="Together project ID to switch to. Omit to choose from your projects."),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Exchange the login token for a project-scoped access token.

    The issuer and client id come from the stored `tg login` credentials.
    Omit the project ID to pick one, or to print the projects you can switch to.
    """
    target = (project_id or "").strip()
    if not target:
        target = await _choose_project(config) or ""
    if not target:
        return

    with TogetherAuth() as auth:
        project = auth.switch(target)
    note_credentials_path()
    if config.json:
        console.print_json(openapi_dumps({"status": "ok", "project_id": project.project_id}).decode("utf-8"))
        return
    console.print(f"[green]Switched to project[/green] [bold]{project.project_id}[/bold]")


async def _choose_project(config: CLIConfig) -> str | None:
    """Project id from a prompt, or None after printing the projects to choose from.

    The list uses the `tg login` token. The current entry may be a project token from an
    earlier switch, and that token cannot list every project the login can switch to.
    """
    login = _login_for_listing()
    projects = await load_projects(
        config.client,
        headers={"Authorization": f"Bearer {login.access_token}"},
    )
    if not config.non_interactive and projects:
        chosen = await select_project(projects, preferred=config.project_id, message="Select a project")
        if chosen:
            return chosen
    if config.json:
        console.print_json(openapi_dumps({"object": "list", "data": projects, "next_cursor": None}).decode("utf-8"))
        return None
    print_project_list(projects, current_id=config.project_id)
    return None


def _login_for_listing() -> StoredCredentials:
    login = CredentialStore.load().login_credentials()
    if login is None:
        raise TogetherError("Not logged in. Run `tg login` first.")
    with TogetherAuth() as auth:
        return auth.refresh(name=login.entry_name) or login
