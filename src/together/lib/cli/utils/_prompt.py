from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console

if TYPE_CHECKING:
    import questionary

custom_style_fancy = [
    ("qmark", "fg:#caaef5 bold"),  # token in front of the question
    ("question", "bold #caaef5"),  # question text
    ("answer", "fg:#98a0b3 bold"),  # submitted answer text behind the question
    ("pointer", "fg:#caaef5 bold"),  # pointer used in select and checkbox prompts
    ("highlighted", "fg:#caaef5 bold"),  # pointed-at choice in select and checkbox prompts
    ("selected", "fg:#caaef5"),  # style for a selected item of a checkbox
    ("separator", "fg:#caaef5"),  # separator in lists
    ("instruction", ""),  # user instructions for select, rawselect, checkbox
    ("text", "#98a0b3"),  # plain text
    ("disabled", "fg:#858585 italic"),  # disabled choices for select and checkbox prompts
]


# class NameValidator(questionary.Validator):
#     def validate(self, document):
#         if document.text.count(" ") > 0:
#             raise questionary.ValidationError(
#                 message="Model name cannot contain spaces",
#                 cursor_position=len(document.text),
#             )


class PromptParameter:
    message: str | None = None
    instructions: str | None = None
    choices: list[str | questionary.Choice] | None = None
    type: Literal["text", "select", "checkbox", "confirm"] = "text"

    def __init__(
        self,
        message: str | None = None,
        instructions: str | None = None,
        choices: list[str | questionary.Choice] | None = None,
    ):
        self.message = message
        self.instructions = instructions
        self.choices = choices

    async def preprompt(self, _config: CLIConfig) -> None:
        pass

    async def prompt(self, field: str) -> str | bool:
        import questionary

        style = questionary.Style(custom_style_fancy)

        if self.instructions is not None:
            console.print(f"[dim]{self.instructions}[/dim]")

        if self.choices is not None:
            return cast(
                str | bool,
                await questionary.select(
                    self.message or field, choices=self.choices, style=style, show_selected=True
                ).unsafe_ask_async(),
            )

        if self.type == "confirm":
            return cast(
                str | bool,
                await questionary.confirm(self.message or field, style=style).unsafe_ask_async(),
            )

        return cast(
            str | bool,
            await questionary.text(
                self.message or field,
                instruction="\n→",
                style=style,  # , validate=NameValidator
            ).unsafe_ask_async(),
        )
