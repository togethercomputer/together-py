from __future__ import annotations
from rich import print

import questionary
from together.lib.cli.logger.config import CLIConfig
from rich.theme import Theme
from rich.console import Console

custom_style_fancy = questionary.Style([
    ('qmark', 'fg:#caaef5 bold'),       # token in front of the question
    ('question', 'bold #caaef5'),               # question text
    ('answer', 'fg:#98a0b3 bold'),      # submitted answer text behind the question
    ('pointer', 'fg:#caaef5 bold'),     # pointer used in select and checkbox prompts
    ('highlighted', 'fg:#caaef5 bold'), # pointed-at choice in select and checkbox prompts
    ('selected', 'fg:#caaef5'),         # style for a selected item of a checkbox
    ('separator', 'fg:#caaef5'),        # separator in lists
    ('instruction', ''),                # user instructions for select, rawselect, checkbox
    ('text', '#98a0b3'),                       # plain text
    ('disabled', 'fg:#858585 italic')   # disabled choices for select and checkbox prompts
])

custom_theme = Theme({
    # Text styles
    "primary": "#caaef5",       # Purple 300 ⭐ (lighter when bold)
    "secondary": "dim #caaef5",          # Purple 500 ⭐ (mid-tone without bold)
    "accent": "#ff68d4",             # Pink 500 ⭐
    "muted": "#98a0b3",              # Grey 400 ⭐
    "dim": "dim #626b84",            # Grey 600 ⭐

    # Semantic styles
    "success": "bold #0dce74",       # Green 400 ⭐
    "info": "#64afff",               # Blue 500 ⭐
    "warning": "bold #ff815d",       # Red 500 ⭐
    "error": "bold #c63800",         # Red 700 ⭐

    # UI elements
    "prompt": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "prompt.choices": "#caaef5",     # Purple 300 ⭐
    "prompt.default": "dim #98a0b3", # Grey 400 ⭐

    # Table styles
    "table.header": "#414858",  # Purple 300 ⭐ (lighter when bold)
    "table.border": "#626b84",       # Grey 600 ⭐
    "table.row": "#c4c9d4",          # Grey 300 ⭐

    # Progress/Loading
    "progress.description": "#caaef5",     # Purple 300 ⭐
    "progress.percentage": "bold #caaef5", # Purple 300 ⭐ (lighter when bold)
    "bar.complete": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "bar.finished": "#0dce74",             # Green 400 ⭐
    "bar.pulse": "#ff68d4",                # Pink 500 ⭐
})

console = Console(theme=custom_theme)


class NameValidator(questionary.Validator):
    def validate(self, document):
        if document.text.count(" ") > 0:
            raise questionary.ValidationError(
                message="Model name cannot contain spaces",
                cursor_position=len(document.text),
            )

class PromptParameter:
    message: str | None = None
    instructions: str | None = None
    choices: list[str | questionary.Choice] | None = None

    def __init__(self, message: str | None = None, instructions: str | None = None, choices: list[str | questionary.Choice] | None = None):
        self.message = message
        self.instructions = instructions
        self.choices = choices

    async def preprompt(self, _config: CLIConfig):
        pass

    async def prompt(self, field: str) -> str:
        if self.instructions is not None:
            print(f"[dim]{self.instructions}[/dim]")

        if self.choices is not None:
            return await questionary.select(self.message or field, choices=self.choices, style=custom_style_fancy, show_selected=True).unsafe_ask_async()

        return await questionary.text(self.message or field, instruction="\n→", style=custom_style_fancy, validate=NameValidator).unsafe_ask_async()