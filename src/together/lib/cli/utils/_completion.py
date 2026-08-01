import os
from typing import Literal

from cyclopts import App
from detect_agent import determine_agent

from together.lib.utils import log_debug


def install_completion(app: App) -> None:
    """Install shell completion script to appropriate location for both "together" and "tg" commands.

    Args:
        app: The app to install completion for.

    Does not raise any errors. Silently fails is better here.
    """
    # Skip completion installation for agents and CI environments.
    if _is_agent_or_ci():
        return

    try:
        from cyclopts.completion.detect import detect_shell

        shell = detect_shell()

        _install_named_completion(app, shell, "together")
        _install_named_completion(app, shell, "tg")
    except Exception as e:
        log_debug(f"Error installing completion: {e}")


def _install_named_completion(app: App, shell: Literal["zsh", "bash", "fish"], name: str) -> None:
    from cyclopts.completion.install import add_to_rc_file, get_default_completion_path

    copy_app = App(name=name)

    copy_app.update(app)
    output = get_default_completion_path(shell, name)

    if output.exists():
        log_debug(f"Completion script already exists at {output}")
        return

    log_debug(f"Installing completion for {name} to {output}")
    script_content = copy_app.generate_completion(shell=shell)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(script_content)
    # Fish does not need any startup script changes.
    if shell in ("bash", "zsh"):
        add_to_rc_file(output, name, shell)  # type: ignore


def _is_agent_or_ci() -> bool:
    is_agent = determine_agent()["is_agent"]
    is_ci = os.getenv("CI") is not None
    return is_agent or is_ci
