from __future__ import annotations

import json
from typing import List, Literal

import click

from together import Together

from ...._types import NOT_GIVEN, NotGiven
from ...._streaming import Stream


@click.command()
@click.pass_context
@click.argument("prompt", type=str, required=True)
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
@click.option("--no-stream", is_flag=True, help="Disable streaming")
@click.option("--logprobs", type=int, help="Return logprobs. Only works with --raw.")
@click.option("--echo", is_flag=True, help="Echo prompt. Only works with --raw.")
@click.option("--n", type=int, help="Number of output generations")
@click.option("--safety-model", type=str, help="Moderation model")
@click.option("--raw", is_flag=True, help="Return raw JSON response")
def completions(
    ctx: click.Context,
    prompt: str,
    model: str,
    max_tokens: int | NotGiven = 512,
    stop: List[str] | NotGiven = NOT_GIVEN,
    temperature: float | NotGiven = NOT_GIVEN,
    top_p: float | NotGiven = NOT_GIVEN,
    top_k: int | NotGiven = NOT_GIVEN,
    repetition_penalty: float | NotGiven = NOT_GIVEN,
    presence_penalty: float | NotGiven = NOT_GIVEN,
    frequency_penalty: float | NotGiven = NOT_GIVEN,
    min_p: float | NotGiven = NOT_GIVEN,
    no_stream: Literal[True, False] = False,
    logprobs: int | NotGiven = NOT_GIVEN,
    echo: bool | NotGiven = NOT_GIVEN,
    n: int | NotGiven = NOT_GIVEN,
    safety_model: str | NotGiven = NOT_GIVEN,
    raw: bool = False,
) -> None:
    """Generate text completions"""
    client: Together = ctx.obj

    response = client.completions.create(
        model=model,
        prompt=prompt,
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
            click.echo(choice.text)

            if should_print_header or not (choice.text is not None and choice.text.endswith("\n")):
                click.echo("\n")
