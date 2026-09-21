from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from together.lib.cli.utils import _cli_extras


def test_has_cli_extras_requires_questionary_and_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    specs: dict[str, object] = {"questionary": object(), "yaml": object()}

    def find_spec(name: str) -> object | None:
        return specs.get(name)

    monkeypatch.setattr(_cli_extras.importlib.util, "find_spec", find_spec)

    assert _cli_extras.has_cli_extras() is True

    del specs["questionary"]
    assert _cli_extras.has_cli_extras() is False

    specs["questionary"] = object()
    del specs["yaml"]
    assert _cli_extras.has_cli_extras() is False


def test_inform_skips_when_extras_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    monkeypatch.setattr(_cli_extras, "has_cli_extras", lambda: True)
    monkeypatch.setattr(_cli_extras, "error_console", output)

    _cli_extras.inform_cli_extras_tip(non_interactive=False)

    output.print.assert_not_called()


def test_inform_skips_when_non_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    monkeypatch.setattr(_cli_extras, "has_cli_extras", lambda: False)
    monkeypatch.setattr(_cli_extras, "error_console", output)

    _cli_extras.inform_cli_extras_tip(non_interactive=True)

    output.print.assert_not_called()


def test_inform_prints_copy_paste_install_command(monkeypatch: pytest.MonkeyPatch) -> None:
    output = MagicMock()
    monkeypatch.setattr(_cli_extras, "has_cli_extras", lambda: False)
    monkeypatch.setattr(_cli_extras, "error_console", output)

    _cli_extras.inform_cli_extras_tip(non_interactive=False)

    rendered = "\n".join(call.args[0] for call in output.print.call_args_list)
    assert "Install the CLI extras for a better experience" in rendered
    assert "together\\[cli]" in rendered
    assert _cli_extras.CLI_EXTRAS_INSTALL_COMMAND == 'uv tool install "together[cli]" --upgrade'
