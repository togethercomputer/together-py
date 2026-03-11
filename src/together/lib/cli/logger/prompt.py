from __future__ import annotations
from rich import print

import questionary

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
    choices: list[str] | None = None

    def __init__(self, message: str | None = None, instructions: str | None = None, choices: list[str] | None = None):
        self.message = message
        self.instructions = instructions
        self.choices = choices

    async def prompt(self, field: str) -> str:
        if self.instructions is not None:
            print(f"[dim]{self.instructions}[/dim]")
        
        if self.choices is not None:
            return await questionary.select(self.message or field, choices=self.choices, style=custom_style_fancy).unsafe_ask_async()

        return await questionary.text(self.message or field, instruction="\n→", style=custom_style_fancy, validate=NameValidator).unsafe_ask_async()