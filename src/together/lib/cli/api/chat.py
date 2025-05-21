from __future__ import annotations

import cmd
import json
from typing import List, Tuple, Literal, cast
from typing_extensions import override

import click

from together import Together

from ...._types import NOT_GIVEN, NotGiven
from ...._streaming import Stream
from ....types.chat import completion_create_params


class ChatShell(cmd.Cmd):
    intro = "Type /exit to exit, /help, or /? to list commands.\n"
    prompt = ">>> "

    def __init__(
        self,
        client: Together,
        model: str,
        max_tokens: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        system_message: str | NotGiven = NOT_GIVEN,
    ) -> None:
        super().__init__()
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.stop = stop
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repetition_penalty = repetition_penalty
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.min_p = min_p
        self.safety_model = safety_model
        self.system_message = system_message

        self.messages: List[completion_create_params.Message] = (
            [{"role": "system", "content": self.system_message}] if self.system_message else []
        )

    @override
    def precmd(self, line: str) -> str:
        if line.startswith("/"):
            return line[1:]
        else:
            return "say " + line

    def do_say(self, arg: str) -> None:
        self.messages.append({"role": "user", "content": arg})

        output = ""

        for chunk in self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            max_tokens=self.max_tokens,
            stop=self.stop,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            min_p=self.min_p,
            safety_model=self.safety_model,
            stream=True,
        ):
            token = chunk.choices[0].delta.content

            click.echo(token, nl=False)

            output += token or ""

        click.echo("\n")

        self.messages.append({"role": "assistant", "content": output})

    def do_reset(self, _arg: str) -> None:
        self.messages = [{"role": "system", "content": self.system_message}] if self.system_message else []

    def do_exit(self, _arg: str) -> bool:
        return True


@click.command(name="chat.interactive")
@click.pass_context
@click.option("--model", type=str, required=True, help="Model name")
@click.option("--max-tokens", type=int, help="Max tokens to generate")
@click.option("--stop", type=str, multiple=True, help="List of strings to stop generation")
@click.option("--temperature", type=float, help="Sampling temperature")
@click.option("--top-p", type=int, help="Top p sampling")
@click.option("--top-k", type=float, help="Top k sampling")
@click.option("--repetition-penalty", type=float, help="Repetition penalty")
@click.option("--presence-penalty", type=float, help="Presence penalty")
@click.option("--frequency-penalty", type=float, help="Frequency penalty")
@click.option("--min-p", type=float, help="Minimum p")
@click.option("--safety-model", type=str, help="Moderation model")
@click.option("--system-message", type=str, help="System message to use for the chat")
def interactive(
    ctx: click.Context,
    model: str,
    max_tokens: int | NotGiven = NOT_GIVEN,
    stop: List[str] | NotGiven = NOT_GIVEN,
    temperature: float | NotGiven = NOT_GIVEN,
    top_p: float | NotGiven = NOT_GIVEN,
    top_k: int | NotGiven = NOT_GIVEN,
    repetition_penalty: float | NotGiven = NOT_GIVEN,
    presence_penalty: float | NotGiven = NOT_GIVEN,
    frequency_penalty: float | NotGiven = NOT_GIVEN,
    min_p: float | NotGiven = NOT_GIVEN,
    safety_model: str | NotGiven = NOT_GIVEN,
    system_message: str | NotGiven = NOT_GIVEN,
) -> None:
    """Interactive chat shell"""
    client: Together = ctx.obj

    ChatShell(
        client=client,
        model=model,
        max_tokens=max_tokens,
        stop=stop,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        min_p=min_p,
        safety_model=safety_model,
        system_message=system_message,
    ).cmdloop()


@click.command(name="chat.completions")
@click.pass_context
@click.option(
    "--message",
    type=(str, str),
    multiple=True,
    required=True,
    help="Message to generate chat completions from",
)
@click.option("--model", type=str, required=True, help="Model name")
@click.option("--max-tokens", type=int, help="Max tokens to generate")
@click.option("--stop", type=str, multiple=True, help="List of strings to stop generation")
@click.option("--temperature", type=float, help="Sampling temperature")
@click.option("--top-p", type=int, help="Top p sampling")
@click.option("--top-k", type=float, help="Top k sampling")
@click.option("--repetition-penalty", type=float, help="Repetition penalty")
@click.option("--presence-penalty", type=float, help="Presence penalty sampling method")
@click.option("--frequency-penalty", type=float, help="Frequency penalty sampling method")
@click.option("--min-p", type=float, help="Min p sampling")
@click.option("--no-stream", is_flag=True, help="Disable streaming")
@click.option("--logprobs", type=int, help="Return logprobs. Only works with --raw.")
@click.option("--echo", is_flag=True, help="Echo prompt. Only works with --raw.")
@click.option("--n", type=int, help="Number of output generations")
@click.option("--safety-model", type=str, help="Moderation model")
@click.option("--raw", is_flag=True, help="Output raw JSON")
def chat(
    ctx: click.Context,
    message: List[Tuple[str, str]],
    model: str,
    max_tokens: int | NotGiven = NOT_GIVEN,
    stop: List[str] | NotGiven = NOT_GIVEN,
    temperature: float | NotGiven = NOT_GIVEN,
    top_p: float | NotGiven = NOT_GIVEN,
    top_k: int | NotGiven = NOT_GIVEN,
    repetition_penalty: float | NotGiven = NOT_GIVEN,
    presence_penalty: float | NotGiven = NOT_GIVEN,
    frequency_penalty: float | NotGiven = NOT_GIVEN,
    min_p: float | NotGiven = NOT_GIVEN,
    no_stream: bool = False,
    logprobs: int | NotGiven = NOT_GIVEN,
    echo: bool | NotGiven = NOT_GIVEN,
    n: int | NotGiven = NOT_GIVEN,
    safety_model: str | NotGiven = NOT_GIVEN,
    raw: bool = False,
) -> None:
    """Generate chat completions from messages"""
    client: Together = ctx.obj

    messages: List[completion_create_params.Message] = []

    for msg in message:
        messages.append({"role": cast(Literal["system", "user", "assistant"], msg[0]), "content": msg[1]}) # type: ignore

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        top_p=top_p,
        top_k=top_k,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
        repetition_penalty=repetition_penalty,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        min_p=min_p,
        stream=not no_stream,
        logprobs=logprobs,
        echo=echo,
        n=n,
        safety_model=safety_model,
    )

    if isinstance(response, Stream):
        for chunk in response:
            if raw:
                click.echo(f"{json.dumps(chunk.model_dump())}")
                continue

            should_print_header = len(chunk.choices) > 1
            for stream_choice in sorted(chunk.choices, key=lambda c: c.index):  # type: ignore
                if should_print_header:
                    click.echo(f"\n===== Completion {stream_choice.index} =====\n")
                click.echo(f"{stream_choice.delta.content}", nl=False)

                if should_print_header:
                    click.echo("\n")

        # new line after stream ends
        click.echo("\n")
    else:
        if raw:
            click.echo(f"{json.dumps(response.model_dump(), indent=4)}")
            return

        should_print_header = len(response.choices) > 1
        for i, choice in enumerate(response.choices):
            if should_print_header:
                click.echo(f"===== Completion {i} =====")
            click.echo(choice.message.content)  # type: ignore

            if should_print_header:
                click.echo("\n")
