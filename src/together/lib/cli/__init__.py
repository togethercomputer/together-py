from __future__ import annotations

import os
import sys
import inspect
from typing import Optional, Annotated, get_args, get_origin

import httpx
from cyclopts import App, Group, Parameter, CycloptsError, MissingArgumentError
from rich.markup import escape as escape_rich_markup

from together import AsyncTogether
from together._version import __version__
from together.lib.utils import log_debug
from together._exceptions import APIError
from together._utils._json import openapi_dumps
from together._utils._logs import setup_logging
from together.lib.cli._track_cli import (
    CliTrackingEvents,
    track_cli,
    flush_pending_events,
    parse_command_and_flags,
    sanitize_cli_error_message,
)
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.utils._api_error import try_handle_server_error_message
from together.lib.cli.utils._completion import install_completion
from together.lib.cli.utils._help_formatter import help_formatter

app = App(
    version=__version__,
    name="tg",
    help_format="rich",
    help=f"[dim]Together CLI (v{__version__})[/dim]",
    console=console,
    usage="",
    help_formatter=help_formatter,
)

app["--version"].group = "Parameters"
app["--help"].group = "Parameters"


def _create_client(
    api_key: Optional[str],
    base_url: Optional[str],
    timeout: Optional[int],
    max_retries: Optional[int],
) -> AsyncTogether:
    try:
        client = AsyncTogether(
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
                console.print(
                    "[red]x[/red] api key missing.\n\nThe api key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
                )
                console.print("You can find your api key at https://api.together.xyz/settings/api-keys")
                sys.exit(1)

            client._client.event_hooks["request"].append(block_requests_for_api_key)
        else:
            raise e

    # Wrap the client's httpx requests to track the parameters sent on api requests
    async def track_request(request: httpx.Request) -> None:
        try:
            track_cli(
                CliTrackingEvents.ApiRequest,
                {"path": request.url.path, "method": request.method},
            )
        except Exception as e:
            log_debug("Error tracking api request", error=e)

    client._client.event_hooks["request"].append(track_request)

    if client.api_key == "":
        console.print(
            "[red]Error:[/red] Together API Key missing.\n\nThe api key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
        )
        console.print("You can find your api key at https://api.together.ai/settings/api-keys")
        sys.exit(1)

    return client


common_parameters = Group(
    "Common Parameters",
)


@app.meta.default
async def launcher(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    api_key: Annotated[Optional[str], Parameter(show=False)] = None,
    base_url: Annotated[Optional[str], Parameter(show=False)] = None,
    timeout: Annotated[Optional[int], Parameter(show=False)] = None,
    max_retries: Annotated[Optional[int], Parameter(show=False)] = None,
    debug: Annotated[Optional[bool], Parameter(show=False)] = False,
    non_interactive: Annotated[
        Optional[bool], Parameter(group=common_parameters, negative=(), help="Disable interactive prompts")
    ] = False,
    output_json: Annotated[
        Optional[bool],
        Parameter(name="json", group=common_parameters, negative=(), help="Output the response in JSON format"),
    ] = False,
) -> None:
    if debug:
        os.environ.setdefault("TOGETHER_LOG", "debug")
        setup_logging()
    client = _create_client(api_key, base_url, timeout, max_retries)
    config = CLIConfig(
        client=client,
        # TODO: Turn on non-interactive mode for agents
        # TODO: Detect isTTY or CI
        non_interactive=non_interactive or False,
        json=output_json or False,
    )

    remaining = list(tokens)
    (parsed_command, explicit_args, is_beta_command) = parse_command_and_flags(app, [*remaining])

    if output_json:
        explicit_args.append("json")
    if non_interactive:
        explicit_args.append("non_interactive")
    if debug:
        explicit_args.append("debug")

    async def run_command() -> None:
        try:
            command, bound, _ignored, extra = app.parse_known_args(remaining)
            # for arg_name, arg_type in command.__annotations__.items():
            #     if isinstance(arg_type, PromptParameter) and not config.non_interactive:
            #         value = await prompt(arg_name)
            #         remaining.append(arg_name)
            #         remaining.append(value)

            kwargs = dict(bound.kwargs)
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

            annotation = e.argument.field_info.annotation
            prompt: PromptParameter | None = None

            if get_origin(annotation) is Annotated:
                args = get_args(annotation)
                metadata = args[1:]
                for m in metadata:
                    if isinstance(m, PromptParameter):
                        prompt = m

            value: str | bool | None = None
            if prompt is not None:
                try:
                    await prompt.preprompt(config)
                    value = await prompt.prompt(e.argument.name)
                except Exception:
                    # If the users does not install the cli extra target, they will not get questionary installed
                    # In this case we want to re-raise the MissingArgumentError
                    raise e from e

                console.print("")  # Push a blank line for nicer output
                if value is True or value is False:
                    remaining.append(e.argument.name)
                else:
                    remaining.append(e.argument.name)
                    remaining.append(value)
                await run_command()
            else:
                # TODO: Better design this
                console.print("Missing required argument", e.argument.name)
                sys.exit(1)
        except APIError as e:
            try:
                try_handle_server_error_message(e, config.json)
            except Exception:
                error_msg = ""
                if e.body is not None:
                    error_msg = getattr(e.body, "message", str(e.body))
                else:
                    error_msg = str(e)
                if config.json:
                    console.print_json(openapi_dumps({"error": error_msg}).decode("utf-8"))
                else:
                    console.print(f"Failed")
                    console.print(escape_rich_markup(str(error_msg)))
            raise e

    track_cli(
        CliTrackingEvents.CommandStarted,
        {"command": parsed_command, "arguments": explicit_args, "is_beta_command": is_beta_command},
    )
    try:
        await run_command()
        track_cli(
            CliTrackingEvents.CommandCompleted,
            {"command": parsed_command, "arguments": explicit_args, "is_beta_command": is_beta_command},
        )
    except KeyboardInterrupt:
        track_cli(
            CliTrackingEvents.CommandUserAborted,
            {"command": parsed_command, "arguments": explicit_args, "is_beta_command": is_beta_command},
        )
        sys.exit(0)
    # Some commands use sys.exit(1) to exit the program.
    # We need to track these so we can see if they are failing.
    except SystemExit as e:
        if e.code == 0:
            track_cli(
                CliTrackingEvents.CommandCompleted,
                {"command": parsed_command, "arguments": explicit_args, "is_beta_command": is_beta_command},
            )
            sys.exit(0)

        track_cli(
            CliTrackingEvents.CommandFailed,
            {
                "command": parsed_command,
                "arguments": explicit_args,
                "is_beta_command": is_beta_command,
                "error": sanitize_cli_error_message(str(e)),
            },
        )
        sys.exit(e.code)
    except Exception as e:
        track_cli(
            CliTrackingEvents.CommandFailed,
            {
                "command": parsed_command,
                "arguments": explicit_args,
                "is_beta_command": is_beta_command,
                "error": sanitize_cli_error_message(str(e)),
            },
        )

        if debug:
            raise e
        elif isinstance(e, CycloptsError):
            e.verbose = True if debug else False
            console.print(f"[red]Error:[/red] {escape_rich_markup(str(e))}")
        elif not isinstance(e, APIError):
            # API Errors are handled better inside the run_command() function
            # We don't want to raise them here as that will print a stack trace which we do not want.
            console.print(f"[red]Error:[/red] {escape_rich_markup(str(e))}")

        sys.exit(1)
    finally:
        flush_pending_events()
        await client.close()


# Register commands
_CLI = "together.lib.cli.api"

## Files API commands
files_app = app.command(App(name="files", help="File API commands"))
files_app.command(f"{_CLI}.files.upload:upload", help="Upload files for fine-tuning, evals, etc.")
files_app.command(f"{_CLI}.files.list:list", alias="ls", help="List files on the Together platform")
files_app.command(f"{_CLI}.files.retrieve:retrieve", help="Retrieve metadata for a file from the Together platform")
files_app.command(
    f"{_CLI}.files.retrieve_content:retrieve_content", help="Download the contents of a file from the Together platform"
)
files_app.command(f"{_CLI}.files.delete:delete", help="Delete a file from the Together platform", alias="-d")
files_app.command(f"{_CLI}.files.check:check", help="Check a local file for issues")

# Fine-tuning API commands
fine_tuning_app = app.command(App(name="fine-tuning", help="Fine-tuning API commands", alias="ft"))
fine_tuning_app.command((f"{_CLI}.fine_tuning.create:create"), alias="-c", help="Start a new fine-tuning job")
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.list:list"), alias="ls", help="List fine-tuning jobs on the Together platform"
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.retrieve:retrieve"), help="Retrieve metadata for a fine-tuning job from the Together platform"
)
fine_tuning_app.command((f"{_CLI}.fine_tuning.cancel:cancel"), help="Cancel a fine-tuning job")
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.list_events:list_events"), help="List events for a fine-tuning job from the Together platform"
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.list_checkpoints:list_checkpoints"),
    help="List checkpoints for a fine-tuning job from the Together platform",
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.download:download"),
    help="Download the weights of a fine-tuned model from the Together platform",
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.delete:delete"),
    help="Delete a fine-tuning job from the Together platform",
    alias="-d",
)

## Models API commands
models_app = app.command(App(name="models", help="Models API commands"))
models_app.command((f"{_CLI}.models.list:list"), alias="ls", help="List models on the Together platform")
models_app.command((f"{_CLI}.models.upload:upload"), help="Upload a model to the Together platform")

## Endpoints API commands
endpoints_app = app.command(App(name="endpoints", help="Endpoints API commands"))
endpoints_app.command(
    (f"{_CLI}.endpoints.hardware:hardware"), help="List available hardware configurations for deploying models"
)
endpoints_app.command((f"{_CLI}.endpoints.create:create"), alias="-c", help="Create a new endpoint")
endpoints_app.command(
    (f"{_CLI}.endpoints.retrieve:retrieve"), help="Retrieve metadata for an endpoint from the Together platform"
)
endpoints_app.command((f"{_CLI}.endpoints.stop:stop"), help="Stop an endpoint")
endpoints_app.command((f"{_CLI}.endpoints.start:start"), help="Start an endpoint")
endpoints_app.command(
    (f"{_CLI}.endpoints.delete:delete"),
    help="Delete an endpoint from the Together platform",
    alias="-d",
)
endpoints_app.command((f"{_CLI}.endpoints.list:list"), alias="ls", help="List endpoints on the Together platform")
endpoints_app.command((f"{_CLI}.endpoints.update:update"), help="Update an endpoint on the Together platform")
endpoints_app.command(
    (f"{_CLI}.endpoints.availability_zones:availability_zones"), help="List availability zones for deploying models"
)

## Evals API commands
evals_app = app.command(App(name="evals", help="Evals API commands"))
evals_app.command((f"{_CLI}.evals.create:create"), alias="-c", help="Create a new eval job")
evals_app.command((f"{_CLI}.evals.list:list"), alias="ls", help="List eval jobs on the Together platform")
evals_app.command(
    (f"{_CLI}.evals.retrieve:retrieve"), help="Retrieve metadata for an eval job from the Together platform"
)
evals_app.command((f"{_CLI}.evals.status:status"), help="Get the status of an eval job")

## Telemetry API commands
telemetry_app = app.command(App(name="telemetry", help="Telemetry API commands"))
telemetry_app.command((f"{_CLI}.telemetry.status:status"), help="Check to see if telemetry is enabled or disabled")
telemetry_app.command((f"{_CLI}.telemetry.enable:enable"), help="Enable telemetry")
telemetry_app.command((f"{_CLI}.telemetry.disable:disable"), help="Disable telemetry")


# Hidden from the help page, but the actual namespace for command resolution
# Visible initially to install tab completion properly, but set to be hidden after installation
beta_root_app = App(name="beta", help="Beta API commands")
beta_app = app.command(beta_root_app)

### Clusters API commands
clusters_app = beta_app.command(App(name="clusters", help="Clusters API commands"))
clusters_app.command((f"{_CLI}.beta.clusters.list:list"), alias="ls", help="List clusters on the Together platform")
clusters_app.command((f"{_CLI}.beta.clusters.create:create"), alias="-c", help="Create a new cluster")
clusters_app.command(
    (f"{_CLI}.beta.clusters.retrieve:retrieve"), help="Retrieve metadata for a cluster from the Together platform"
)
clusters_app.command((f"{_CLI}.beta.clusters.update:update"), help="Update a cluster on the Together platform")
clusters_app.command(
    (f"{_CLI}.beta.clusters.delete:delete"),
    help="Delete a cluster from the Together platform",
    alias="-d",
)
clusters_app.command((f"{_CLI}.beta.clusters.list_regions:list_regions"), help="List regions for deploying clusters")
clusters_app.command((f"{_CLI}.beta.clusters.get_credentials:get_credentials"), help="Get credentials for a cluster")

### Clusters > Storage API commands
storage_app = clusters_app.command(App(name="storage", help="Clusters Storage API commands", group="Subcommands"))
storage_app.command((f"{_CLI}.beta.clusters.storage.list:list"), alias="ls", help="List storage volumes for a cluster")
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.create:create"), alias="-c", help="Create a new storage volume for a cluster"
)
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.retrieve:retrieve"),
    help="Retrieve metadata for a storage volume from the Together platform",
)
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.delete:delete"),
    help="Delete a storage volume from the Together platform",
    alias="-d",
)

### JIG API commands
jig_app = beta_app.command(App(name="jig", help="JIG API commands"))
jig_app.command((f"{_CLI}.beta.jig.jig:init"), help="Initialize configuration for JIG deployment")
jig_app.command(
    (f"{_CLI}.beta.jig.jig:dockerfile_cli"), name="dockerfile", help="Generate Dockerfile from jig configuration"
)
jig_app.command((f"{_CLI}.beta.jig.jig:build_cli"), name="build", help="Build container image")
jig_app.command((f"{_CLI}.beta.jig.jig:push_cli"), name="push", help="Push image to registry")
jig_app.command((f"{_CLI}.beta.jig.jig:deploy_cli"), name="deploy", help="Deploy model to Together")
jig_app.command((f"{_CLI}.beta.jig.jig:status_cli"), name="status", help="Get deployment status")
jig_app.command((f"{_CLI}.beta.jig.jig:endpoint_cli"), name="endpoint", help="Get deployment endpoint URL")
jig_app.command((f"{_CLI}.beta.jig.jig:logs_cli"), name="logs", help="Get deployment logs")
jig_app.command((f"{_CLI}.beta.jig.jig:destroy_cli"), name="destroy", help="Destroy deployment")
jig_app.command((f"{_CLI}.beta.jig.jig:submit_cli"), name="submit", help="Submit a job to the deployment")
jig_app.command((f"{_CLI}.beta.jig.jig:job_status_cli"), name="job-status", help="Get status of a specific job")
jig_app.command(
    (f"{_CLI}.beta.jig.jig:queue_status_cli"), name="queue-status", help="Get queue metrics for the deployment"
)
jig_app.command((f"{_CLI}.beta.jig.jig:list_deployments_cli"), name="list", alias="ls", help="List all deployments")

secrets_app = jig_app.command(App(name="secrets", help="Manage deployment secrets", group="Subcommands"))
secrets_app.command((f"{_CLI}.beta.jig.jig:secrets_set_cli"), name="set", help="Set a secret (create or update)")
secrets_app.command((f"{_CLI}.beta.jig.jig:secrets_unset_cli"), name="unset", help="Remove a secret from local state")
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_delete_cli"),
    name="delete",
    help="Delete a secret and unset it locally",
    alias="-d",
)
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_list_cli"), name="list", alias="ls", help="List all secrets with sync status"
)

### Jig > volumes
storage_app = jig_app.command(App(name="volumes", help="Jig Volumes API commands", group="Subcommands"))
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_create_cli"), name="create", help="Create a new volume for a JIG deployment"
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_update_cli"), name="update", help="Update a volume and re-upload files"
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_delete_cli"),
    name="delete",
    help="Delete a volume from the Together platform",
    alias="-d",
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_describe"),
    name="describe",
    help="Retrieve metadata for a volume from the Together platform",
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_list"), name="list", alias="ls", help="List volumes for a JIG deployment"
)


def main() -> None:
    install_completion(app)

    # Shown in the root help page, but not a functional command
    BETA_GROUP_TITLE = "Beta Commands"
    app.command(App(name="beta clusters", help="Create and manage GPU clusters", group=BETA_GROUP_TITLE))
    app.command(App(name="beta jig", help="Container deployment", group=BETA_GROUP_TITLE))
    beta_root_app.show = False

    app.meta()
