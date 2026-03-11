from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path
from typing import Annotated, Optional, get_args, get_origin

import httpx
from cyclopts import App, MissingArgumentError, Parameter

from together import AsyncTogether
from together._exceptions import APIError
from together._version import __version__
from together._utils._logs import setup_logging
from together.lib.cli.logger.prompt import PromptParameter

app = App(
    name="together",
    help="Together AI CLI",
    version=__version__,
    default_parameter=Parameter(negative=())
)

app['--version'].group = "Parameters"
app['--help'].group = "Parameters"

class Config:
    client: AsyncTogether
    non_interactive: bool
    json: bool

    def __init__(self, client: AsyncTogether, non_interactive: bool, json: bool):
        self.client = client
        self.non_interactive = non_interactive
        self.json = json

def _create_client(
    api_key: Optional[str],
    base_url: Optional[str],
    timeout: Optional[int],
    max_retries: Optional[int],
) -> AsyncTogether:
    try:
        return AsyncTogether(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 0,
        )
    except Exception as e:
        if "api_key" in str(e):
            client = AsyncTogether(
                api_key="0000000000000000000000000000000000000000",
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries if max_retries is not None else 0,
            )

            def block_requests_for_api_key(_: httpx.Request) -> None:
                print("Error: api key missing.", file=sys.stderr)
                print(
                    "The api_key must be set either by passing --api-key or by setting TOGETHER_API_KEY.",
                    file=sys.stderr,
                )
                print("You can find your api key at https://api.together.xyz/settings/api-keys", file=sys.stderr)
                sys.exit(1)

            client._client.event_hooks["request"].append(block_requests_for_api_key)
            return client
        raise e


@app.meta.default
async def _launcher(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    api_key: Annotated[Optional[str], Parameter(show=False)] = None,
    base_url: Annotated[Optional[str], Parameter(show=False)] = None,
    timeout: Annotated[Optional[int], Parameter(show=False)] = None,
    max_retries: Annotated[Optional[int], Parameter(show=False)] = None,
    debug: Annotated[Optional[bool], Parameter(show=False)] = False,
    non_interactive: Annotated[Optional[bool], Parameter()] = False,
    json: Annotated[Optional[bool], Parameter()] = False,
) -> None:
    if debug:
        os.environ.setdefault("TOGETHER_LOG", "debug")
        setup_logging()
    client = _create_client(api_key, base_url, timeout, max_retries)
    config = Config(
        client=client,
        non_interactive=non_interactive or False,
        json=json or False,
    )

    remaining = list(tokens)

    async def run_command():
        try:
            command, bound, _ignored, extra = app.parse_known_args(remaining)
            for arg_name, arg_type in command.__annotations__.items():
                if isinstance(arg_type, PromptParameter) and not config.non_interactive:
                    value = await prompt(arg_name)
                    remaining.append(arg_name)
                    remaining.append(value)

            kwargs = dict(bound.kwargs)
            kwargs["config"] = config
            if "config" in extra:
                kwargs["config"] = config
            result = command(*bound.args, **kwargs)
            if inspect.iscoroutine(result):
                await result

        except MissingArgumentError as e:
            if config.non_interactive:
                raise e
            # auto prompt for missing arguments
            if e.argument is None:
                raise e

            annotation = (e.argument.field_info.annotation)
            prompt: PromptParameter | None = None

            if get_origin(annotation) is Annotated:
                args = get_args(annotation)
                metadata = args[1:]
                for metadata in metadata:
                    if isinstance(metadata, PromptParameter):
                        prompt = metadata

            value: str | None = None
            if prompt is not None:
                value = await prompt.prompt(e.argument.name)
                print("") # Push a blank line for nicer output
                remaining.append(e.argument.name)
                remaining.append(value)
                await run_command()
        except (KeyboardInterrupt, SystemExit):
            pass
        except APIError as e:
            error_msg = ""
            if e.body is not None:
                error_msg = getattr(e.body, "message", str(e.body))
            else:
                error_msg = str(e)
            print(f"Failed", file=sys.stderr)
            print(f"{error_msg}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Failed", file=sys.stderr)
            print(f"An unexpected error occurred - {e!s}", file=sys.stderr)
            sys.exit(1)
    try:
        await run_command()
    finally:
        await client.close()


# Register commands
_CLI = "together.lib.cli.api"

## Files API commands
files_app = app.command(App(name="files", help="File API commands"))
files_app.command(f"{_CLI}.files.upload:upload")
files_app.command(f"{_CLI}.files.list:list_", name="list")
files_app.command((f"{_CLI}.files.retrieve:retrieve"))
files_app.command((f"{_CLI}.files.retrieve_content:retrieve_content"))
files_app.command((f"{_CLI}.files.delete:delete"))
files_app.command((f"{_CLI}.files.check:check"))

# Fine-tuning API commands
fine_tuning_app = app.command(App(name="fine-tuning", help="Fine-tuning API commands"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.create:create"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.list:list_"), name="list")
fine_tuning_app.command((f"{_CLI}.fine_tuning.retrieve:retrieve"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.cancel:cancel"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.list_events:list_events"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.list_checkpoints:list_checkpoints"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.download:download"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.delete:delete"))

## Models API commands
models_app = app.command(App(name="models", help="Models API commands"))
models_app.command((f"{_CLI}.models.list:list_"), name="list")
models_app.command((f"{_CLI}.models.upload:upload"))

## Endpoints API commands
endpoints_app = app.command(App(name="endpoints", help="Endpoints API commands"))
endpoints_app.command((f"{_CLI}.endpoints.hardware:hardware"))
endpoints_app.command((f"{_CLI}.endpoints.create:create"))
endpoints_app.command((f"{_CLI}.endpoints.retrieve:retrieve"))
endpoints_app.command((f"{_CLI}.endpoints.stop:stop"))
endpoints_app.command((f"{_CLI}.endpoints.start:start"))
endpoints_app.command((f"{_CLI}.endpoints.delete:delete"))
endpoints_app.command((f"{_CLI}.endpoints.list:list_"), name="list")
endpoints_app.command((f"{_CLI}.endpoints.update:update"))
endpoints_app.command((f"{_CLI}.endpoints.availability_zones:availability_zones"))

## Evals API commands
evals_app = app.command(App(name="evals", help="Evals API commands"))
evals_app.command((f"{_CLI}.evals.create:create"))
evals_app.command((f"{_CLI}.evals.list:list_"), name="list")
evals_app.command((f"{_CLI}.evals.retrieve:retrieve"))
evals_app.command((f"{_CLI}.evals.status:status"))

## Beta API commands
beta_app = app.command(App(name="beta", help="Beta API commands"))

### Clusters API commands
clusters_app = beta_app.command(App(name="clusters", help="Clusters API commands"))
clusters_app.command((f"{_CLI}.beta.clusters.list:list_"), name="list")
clusters_app.command((f"{_CLI}.beta.clusters.create:create"))
clusters_app.command((f"{_CLI}.beta.clusters.retrieve:retrieve"))
clusters_app.command((f"{_CLI}.beta.clusters.update:update"))
clusters_app.command((f"{_CLI}.beta.clusters.delete:delete"))
clusters_app.command((f"{_CLI}.beta.clusters.list_regions:list_regions"))
clusters_app.command((f"{_CLI}.beta.clusters.get_credentials:get_credentials"))

### Clusters > Storage API commands
storage_app = clusters_app.command(App(name="storage", help="Clusters Storage API commands"))
storage_app.command((f"{_CLI}.beta.clusters.storage.list:list_"), name="list")
storage_app.command((f"{_CLI}.beta.clusters.storage.create:create"))
storage_app.command((f"{_CLI}.beta.clusters.storage.retrieve:retrieve"))
storage_app.command((f"{_CLI}.beta.clusters.storage.delete:delete"))

### JIG API COMMANDS - TODO


def _maybe_auto_install_completion() -> None:
    if os.environ.get("TOGETHER_NO_AUTO_COMPLETION"):
        return
    sentinel = Path.home() / ".config" / "together" / "completion_installed"
    if sentinel.exists():
        return
    try:
        shell = os.environ.get("SHELL", "")
        zsh = shell.endswith("zsh")
        bash = shell.endswith("bash")
        fish = shell.endswith("fish")
        if not any((zsh, bash, fish)):
            return
        if zsh:
            shell = "zsh"
        elif bash:
            shell = "bash"
        elif fish:
            shell = "fish"
        print(f"Installing tab completion for {shell}...", file=sys.stderr)
        app.install_completion(shell=shell, add_to_startup=True)
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.touch()
        print("Together shell command completion installed. Restart your shell or source your rc file to start using it.", file=sys.stderr)
    except Exception:
        pass


def main() -> None:
    _maybe_auto_install_completion()
    app.meta()

