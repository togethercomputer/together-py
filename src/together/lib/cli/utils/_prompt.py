from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console

if TYPE_CHECKING:
    pass

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


async def confirm(message: str) -> bool:
    try:
        import questionary

        style = questionary.Style(custom_style_fancy)

        result = await questionary.confirm(message, style=style).unsafe_ask_async()
        return bool(result)
    except Exception:
        return False


class PromptParameter:
    message: str | None = None
    instructions: str | None = None
    choices: list[str | tuple[str, str]] | None = None
    type: Literal["text", "select", "checkbox", "confirm"] = "text"

    def __init__(
        self,
        message: str | None = None,
        instructions: str | None = None,
        choices: list[str | tuple[str, str]] | None = None,
    ):
        self.message = message or self.message
        self.instructions = instructions or self.instructions
        self.choices = choices or self.choices

    async def preprompt(self, _config: CLIConfig) -> None:
        pass

    async def prompt(self, field: str) -> str | bool:
        import questionary

        style = questionary.Style(custom_style_fancy)

        if self.instructions is not None:
            console.print(f"[dim]{self.instructions}[/dim]")

        if self.choices is not None:
            choices: list[questionary.Choice] = []
            for choice in self.choices:
                if isinstance(choice, tuple):
                    choices.append(questionary.Choice(title=choice[0], value=choice[1]))
                else:
                    choices.append(questionary.Choice(title=choice, value=choice))
            return cast(
                str | bool,
                await questionary.select(
                    self.message or field, choices=choices, style=style, show_selected=True
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
