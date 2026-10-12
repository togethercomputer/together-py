"""When an API rejects the base `tg login` JWT, prompt for a project-scoped token."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from rich.markup import escape as escape_rich_markup

from together import TogetherError, APIStatusError, PermissionDeniedError, omit
from together.lib.cli.auth import TogetherAuth, StoredCredentials
from together.types.project import Project
from together.lib.cli.utils._prompt import confirm, custom_style_fancy
from together.lib.cli.utils._console import console
from together.lib.cli.utils._json_mode import is_json_mode, exit_with_message

# These succeed with a user token, so a rejection here is not "switch projects first".
_SCOPE_FREE_COMMANDS = frozenset(
    {
        "whoami",
        "projects list",
        "telemetry status",
        "telemetry enable",
        "telemetry disable",
    }
)
# 401/403 from a user JWT that has no project means the call needs a project token.
# A 401 whose refresh was rejected is a dead session instead — see explain_project_scope.
# A project JWT's 401/403 is that command's own error. A 400/404 is too.
_USER_JWT_REJECTION = frozenset({401, 403})
_SELECT_PROJECT_SCOPE = "Select a project scope"


class ProjectScopeSwitched(Exception):
    """The user picked a project. The caller reruns the command with this token."""

    def __init__(self, project_id: str, access_token: str) -> None:
        super().__init__(project_id)
        self.project_id = project_id
        self.access_token = access_token


def project_switch_message(
    error: BaseException,
    *,
    command: str,
    token_project: str | None,
    client_project: str | None,
) -> str | None:
    """Message when `error` means the login token cannot act in the target project.

    Returns None when the failure is unrelated, or the token is already scoped to that project.
    """
    if command in _SCOPE_FREE_COMMANDS:
        return None
    # Base user JWT: the API (or a missing project id) refused the unscoped login.
    if token_project is None:
        if not _user_jwt_rejected(error):
            return None
    elif not isinstance(error, PermissionDeniedError) or token_project == client_project or not client_project:
        # A project-scoped token that 403s on its own project is a real permission error.
        return None

    target = client_project if client_project and client_project != token_project else None
    if target and token_project:
        return (
            f"Your login is scoped to project {token_project}, not {target}. "
            f"Run `tg switch {target}` before this command."
        )
    if target:
        return f"Your login is not scoped to project {target}. Run `tg switch {target}` before this command."
    return (
        "Your login is not scoped to a project. "
        "Run `tg projects list`, then `tg switch <project-id>`, before this command."
    )


def _login_refresh_failure(client: Any) -> TogetherError | None:
    """`TogetherError` from the 401 retry's refresh, if that refresh was rejected."""
    http = getattr(client, "_client", None)
    auth = getattr(http, "auth", None)
    failure = getattr(auth, "refresh_failure", None)
    if isinstance(failure, TogetherError):
        return failure
    return None


def _user_jwt_rejected(error: BaseException) -> bool:
    if isinstance(error, ValueError) and (
        "Missing project_id" in str(error) or "non-empty value for `project_id`" in str(error)
    ):
        return True
    return isinstance(error, APIStatusError) and error.status_code in _USER_JWT_REJECTION


async def explain_project_scope(
    error: BaseException,
    *,
    command: str,
    using_stored_token: bool,
    token_project: str | None,
    client_project: str | None,
    non_interactive: bool,
    client: Any = None,
) -> None:
    """Prompt for a project-scoped token and signal a rerun, or print `tg switch`. No-op otherwise."""
    if not using_stored_token:
        return
    # An unscoped token's 401 is a scope miss only when the session is still alive.
    # A rejected refresh means the login itself is gone; listing projects 401s too.
    if token_project is None and isinstance(error, APIStatusError) and error.status_code == 401:
        failure = _login_refresh_failure(client)
        if failure is not None:
            text = str(failure)
            exit_with_message(f"[red]Error:[/red] {escape_rich_markup(text)}", error=text)
    message = project_switch_message(
        error,
        command=command,
        token_project=token_project,
        client_project=client_project,
    )
    if message is None:
        return

    target = client_project if client_project and client_project != token_project else None
    if not non_interactive and not is_json_mode():
        console.print("[red]×[/red] [bold]Error[/bold]")
        console.print("  The API rejected this request. You must select a project scope to work in.")
        chosen = await _choose_project(client, token_project=token_project, target=target)
        if chosen:
            credentials = _exchange(chosen)
            console.print(f"[green]Switched to project[/green] [bold]{escape_rich_markup(chosen)}[/bold]")
            raise ProjectScopeSwitched(chosen, credentials.access_token)

    exit_with_message(f"[red]Error:[/red] {escape_rich_markup(message)}", error=message)


async def _choose_project(client: Any, *, token_project: str | None, target: str | None) -> str | None:
    """Project id to exchange the login for, or None when the user declines."""
    if token_project is None:
        # Base user JWT was rejected. Ask which project-scoped token to switch to.
        return await _prompt_user_jwt_project(client, preferred=target)
    if target and await confirm(f"Switch to project {target} now?"):
        return target
    return None


async def _prompt_user_jwt_project(client: Any, *, preferred: str | None) -> str | None:
    projects = await _load_projects(client)
    if projects:
        return await select_project(projects, preferred=preferred, message=_SELECT_PROJECT_SCOPE)
    if preferred and await confirm(f"Switch to project {preferred} now?"):
        return preferred
    return None


async def load_projects(client: Any, *, headers: Mapping[str, str] | None = None) -> list[Project]:
    """Every project `client` can list, following `next_cursor`."""
    if client is None:
        return []
    projects: list[Project] = []
    after: str | None = None
    seen: set[str] = set()
    while True:
        page = await client.projects.list(
            limit=100,
            after=after if after else omit,
            extra_headers=headers,
        )
        raw_items = cast(list[object], getattr(page, "data", None) or [])
        for item in raw_items:
            if isinstance(item, Project):
                projects.append(item)
        next_cursor = cast(object, getattr(page, "next_cursor", None))
        cursor = next_cursor if isinstance(next_cursor, str) and next_cursor else None
        if not cursor or cursor in seen:
            return projects
        seen.add(cursor)
        after = cursor


async def _load_projects(client: Any) -> list[Project]:
    try:
        return await load_projects(client)
    except Exception:
        return []


async def select_project(
    projects: Sequence[Project], *, preferred: str | None, message: str = "Which project should this login use?"
) -> str | None:
    """Ask which project-scoped token to use. None when the prompt cannot be shown."""
    try:
        import questionary

        choices = [
            questionary.Choice(title=f"{project.name} ({project.slug})", value=project.id) for project in projects
        ]
        default = preferred if any(project.id == preferred for project in projects) else None
        selected = await questionary.select(
            message,
            choices=choices,
            default=default,
            style=questionary.Style(custom_style_fancy),
            show_selected=True,
        ).unsafe_ask_async()
    except Exception:
        return None
    return str(selected) if selected else None


CHOOSE_PROJECT_MESSAGE = "Choose a project to work in:\n  [dim]-[/dim] [white]tg projects list[/white]\n  [dim]-[/dim] [white]tg switch <project-id>[/white]"


async def offer_project_after_login(client: Any, *, interactive: bool) -> str | None:
    """Exchange the new login for a project token. None when the user was not switched.

    A single project is selected without a prompt, including when the terminal cannot ask.
    """
    projects = await _load_projects(client)
    if len(projects) == 1:
        chosen: str | None = projects[0].id
    elif interactive and projects:
        chosen = await select_project(projects, preferred=None)
    else:
        chosen = None
    if not chosen:
        return None
    with TogetherAuth() as auth:
        auth.switch(chosen)
    return chosen


def _exchange(project_id: str) -> StoredCredentials:
    try:
        with TogetherAuth() as auth:
            return auth.switch(project_id)
    except TogetherError as exc:
        exit_with_message(f"[red]Error:[/red] {escape_rich_markup(str(exc))}", error=str(exc))
