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
    sanitize_cli_error_message,
)
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.utils._api_error import try_handle_server_error_message
from together.lib.cli.utils._completion import install_completion
from together.lib.cli.utils._help_examples import (
    JIG_HELP_EXAMPLES,
    EVALS_HELP_EXAMPLES,
    FILES_HELP_EXAMPLES,
    MODELS_HELP_EXAMPLES,
    JIG_LOGS_HELP_EXAMPLES,
    JIG_PUSH_HELP_EXAMPLES,
    ENDPOINTS_HELP_EXAMPLES,
    JIG_BUILD_HELP_EXAMPLES,
    TOP_LEVEL_HELP_EXAMPLES,
    JIG_DEPLOY_HELP_EXAMPLES,
    JIG_SUBMIT_HELP_EXAMPLES,
    BETA_MODELS_HELP_EXAMPLES,
    FINE_TUNING_HELP_EXAMPLES,
    JIG_DESTROY_HELP_EXAMPLES,
    JIG_SECRETS_HELP_EXAMPLES,
    JIG_VOLUMES_HELP_EXAMPLES,
    EVALS_CREATE_HELP_EXAMPLES,
    FILES_UPLOAD_HELP_EXAMPLES,
    BETA_CLUSTERS_HELP_EXAMPLES,
    MODELS_UPLOAD_HELP_EXAMPLES,
    BETA_ENDPOINTS_HELP_EXAMPLES,
    JIG_JOB_STATUS_HELP_EXAMPLES,
    JIG_SECRETS_SET_HELP_EXAMPLES,
    ENDPOINTS_CREATE_HELP_EXAMPLES,
    ENDPOINTS_UPDATE_HELP_EXAMPLES,
    BETA_ENDPOINTS_AB_HELP_EXAMPLES,
    BETA_ENDPOINTS_LS_HELP_EXAMPLES,
    BETA_ENDPOINTS_RM_HELP_EXAMPLES,
    JIG_SECRETS_UNSET_HELP_EXAMPLES,
    BETA_ENDPOINTS_GET_HELP_EXAMPLES,
    BETA_MODELS_CREATE_HELP_EXAMPLES,
    BETA_MODELS_PUBLIC_HELP_EXAMPLES,
    BETA_MODELS_UPDATE_HELP_EXAMPLES,
    BETA_MODELS_UPLOAD_HELP_EXAMPLES,
    ENDPOINTS_HARDWARE_HELP_EXAMPLES,
    FINE_TUNING_CREATE_HELP_EXAMPLES,
    JIG_SECRETS_DELETE_HELP_EXAMPLES,
    JIG_VOLUMES_CREATE_HELP_EXAMPLES,
    JIG_VOLUMES_UPDATE_HELP_EXAMPLES,
    BETA_MODELS_CONFIGS_HELP_EXAMPLES,
    BETA_CLUSTERS_CREATE_HELP_EXAMPLES,
    BETA_CLUSTERS_UPDATE_HELP_EXAMPLES,
    BETA_MODELS_DOWNLOAD_HELP_EXAMPLES,
    FINE_TUNING_DOWNLOAD_HELP_EXAMPLES,
    BETA_CLUSTERS_STORAGE_HELP_EXAMPLES,
    BETA_ENDPOINTS_DEPLOY_HELP_EXAMPLES,
    BETA_ENDPOINTS_SHADOW_HELP_EXAMPLES,
    BETA_ENDPOINTS_UPDATE_HELP_EXAMPLES,
    FILES_RETRIEVE_CONTENT_HELP_EXAMPLES,
    FINE_TUNING_LIST_METRICS_HELP_EXAMPLES,
    BETA_CLUSTERS_REMEDIATIONS_HELP_EXAMPLES,
    BETA_MODELS_REMOTE_UPLOADS_HELP_EXAMPLES,
    BETA_CLUSTERS_STORAGE_CREATE_HELP_EXAMPLES,
    BETA_CLUSTERS_STORAGE_UPDATE_HELP_EXAMPLES,
    BETA_CLUSTERS_GET_CREDENTIALS_HELP_EXAMPLES,
    BETA_CLUSTERS_REMEDIATIONS_CREATE_HELP_EXAMPLES,
    BETA_MODELS_REMOTE_UPLOADS_CREATE_HELP_EXAMPLES,
)
from together.lib.cli.utils._help_formatter import help_formatter
from together.lib.cli.utils._preparse_tokens import preparse_tokens

app = App(
    version=__version__,
    name="tg",
    help_format="rich",
    help=f"[dim]Together CLI (v{__version__})[/dim]",
    console=console,
    usage="",
    help_formatter=help_formatter,
)

_GLOBAL_PARAM_HELP = {
    "--help": "Display this message and exit",
    "--version": "Display application version",
}


async def _resolve_project_id(client: AsyncTogether) -> str:
    me = await client.whoami()
    return me.project_id


def _propagate_global_param_group(target_app: App) -> None:
    for flag, help_text in _GLOBAL_PARAM_HELP.items():
        try:
            target_app[flag].group = "Global Options"
            target_app[flag].show = True
            target_app[flag].help = help_text
            target_app.help_epilogue = target_app.help_epilogue or ""
        except KeyError:
            pass
    for sub in target_app.subapps:
        if sub.default_command in (target_app.help_print, target_app.version_print):
            continue
        _propagate_global_param_group(sub)


def _create_client(
    api_key: Optional[str],
    base_url: Optional[str],
    timeout: Optional[int],
    max_retries: Optional[int],
    project_id: Optional[str],
) -> AsyncTogether:
    try:
        client = AsyncTogether(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 0,
            project_id=project_id,
        )
    except Exception as e:
        if "api_key" in str(e):
            client = AsyncTogether(
                api_key="0000000000000000000000000000000000000000",
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries if max_retries is not None else 0,
                project_id=project_id,
            )

            def block_requests_for_api_key(_: httpx.Request) -> None:
                console.print(
                    "[red]x[/red] api key missing.\n\nThe api key must be set either by passing --api-key to the command or by setting the TOGETHER_API_KEY environment variable",
                )
                console.print("You can find your api key at https://api.together.ai/settings/api-keys")
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


global_options = Group(
    "Global Options",
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
        Optional[bool], Parameter(group=global_options, negative=(), help="Disable interactive prompts")
    ] = False,
    project_id: Annotated[
        Optional[str],
        Parameter(
            name="--project",
            group=global_options,
            help=(
                "Together project ID. Defaults to TOGETHER_PROJECT_ID. If omitted, read-only commands use the "
                "project associated with the API key; mutating commands may prompt for confirmation or require "
                "an explicit project in JSON or non-interactive mode."
            ),
            env_var="TOGETHER_PROJECT_ID",
        ),
    ] = None,
    output_json: Annotated[
        Optional[bool],
        Parameter(name="json", group=global_options, negative=(), help="Output the response in JSON format"),
    ] = False,
) -> None:
    if debug:
        os.environ.setdefault("TOGETHER_LOG", "debug")
        setup_logging()
    client = _create_client(api_key, base_url, timeout, max_retries, project_id)

    if client.project_id is None:
        client.project_id = await _resolve_project_id(client)

    config = CLIConfig(
        client=client,
        # TODO: Turn on non-interactive mode for agents
        # TODO: Detect isTTY or CI
        non_interactive=non_interactive or output_json or False,
        json=output_json or False,
        project_id=project_id,
    )

    (parsed_command, explicit_args, is_beta_command, remaining) = preparse_tokens(app, [*tokens])

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
files_app = app.command(App(name="files", help="Upload and manage files", help_epilogue=FILES_HELP_EXAMPLES))
files_app.command(
    f"{_CLI}.files.upload:upload",
    help="Upload a file for fine-tuning, evals, or inference",
    help_epilogue=FILES_UPLOAD_HELP_EXAMPLES,
)
files_app.command(f"{_CLI}.files.list:list", alias="ls", help="List your files")
files_app.command(f"{_CLI}.files.retrieve:retrieve", alias="get", help="Get file details")
files_app.command(f"{_CLI}.files.retrieve_content:retrieve_content", help="Download file contents", show=False)
files_app.command(
    f"{_CLI}.files.retrieve_content:retrieve_content",
    name="download",
    help="Download file contents",
    help_epilogue=FILES_RETRIEVE_CONTENT_HELP_EXAMPLES,
)
files_app.command(f"{_CLI}.files.delete:delete", alias="-d", help="Delete a file")
files_app.command(f"{_CLI}.files.check:check", help="Check a local file for issues")

# Fine-tuning API commands
fine_tuning_app = app.command(
    App(
        name="fine-tuning",
        alias="ft",
        help="Create and manage fine-tuning jobs",
        help_epilogue=FINE_TUNING_HELP_EXAMPLES,
    )
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.create:create"),
    alias="-c",
    help="Start a new fine-tuning job",
    help_epilogue=FINE_TUNING_CREATE_HELP_EXAMPLES,
)
fine_tuning_app.command((f"{_CLI}.fine_tuning.list:list"), alias="ls", help="List fine-tuning jobs")
fine_tuning_app.command((f"{_CLI}.fine_tuning.retrieve:retrieve"), alias="get", help="Get fine-tuning job details")
fine_tuning_app.command((f"{_CLI}.fine_tuning.cancel:cancel"), help="Cancel a fine-tuning job")
fine_tuning_app.command((f"{_CLI}.fine_tuning.list_events:list_events"), help="List events for a fine-tuning job")
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.list_checkpoints:list_checkpoints"),
    help="List checkpoints for a fine-tuning job",
)
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.download:download"),
    help="Download a fine-tuned model's weights",
    help_epilogue=FINE_TUNING_DOWNLOAD_HELP_EXAMPLES,
)
fine_tuning_app.command((f"{_CLI}.fine_tuning.delete:delete"), alias="-d", help="Delete a fine-tuning job")
fine_tuning_app.command(
    (f"{_CLI}.fine_tuning.list_metrics:list_metrics"),
    help="Retrieve training metrics for a fine-tuning job",
    help_epilogue=FINE_TUNING_LIST_METRICS_HELP_EXAMPLES,
)

## Models API commands
models_app = app.command(App(name="models", help="List and upload models", help_epilogue=MODELS_HELP_EXAMPLES))
models_app.command((f"{_CLI}.models.list:list"), alias="ls", help="List available models")
models_app.command((f"{_CLI}.models.upload:upload"), help="Upload a model", help_epilogue=MODELS_UPLOAD_HELP_EXAMPLES)

## Endpoints API commands
endpoints_app = app.command(App(name="endpoints", help="Deploy and manage dedicated endpoints"))
endpoints_app.command(
    (f"{_CLI}.endpoints.hardware:hardware"),
    help="List available hardware configurations for deploying models",
    help_epilogue=ENDPOINTS_HARDWARE_HELP_EXAMPLES,
)
endpoints_app.command(
    (f"{_CLI}.endpoints.create:create"),
    alias="-c",
    help="Create a new endpoint",
    help_epilogue=ENDPOINTS_CREATE_HELP_EXAMPLES,
)
endpoints_app.command((f"{_CLI}.endpoints.retrieve:retrieve"), alias="get", help="Get endpoint details")
endpoints_app.command((f"{_CLI}.endpoints.stop:stop"), help="Stop an endpoint")
endpoints_app.command((f"{_CLI}.endpoints.start:start"), help="Start an endpoint")
endpoints_app.command((f"{_CLI}.endpoints.delete:delete"), alias="-d", help="Delete an endpoint")
endpoints_app.command((f"{_CLI}.endpoints.list:list"), alias="ls", help="List your endpoints")
endpoints_app.command(
    (f"{_CLI}.endpoints.update:update"), help="Update an endpoint", help_epilogue=ENDPOINTS_UPDATE_HELP_EXAMPLES
)
endpoints_app.command(
    (f"{_CLI}.endpoints.availability_zones:availability_zones"),
    help="List availability zones for deploying models",
)
endpoint_adapters_app = endpoints_app.command(
    App(name="adapters", help="Manage LoRA adapters bound to dedicated endpoints", group="Subcommands")
)
endpoint_adapters_app.command(
    (f"{_CLI}.endpoints.adapters.list:list"), alias="ls", help="List adapters for an endpoint"
)
endpoint_adapters_app.command((f"{_CLI}.endpoints.adapters.add:add"), help="Bind an adapter to an endpoint")
endpoint_adapters_app.command(
    (f"{_CLI}.endpoints.adapters.remove:remove"),
    alias=("delete", "rm"),
    help="Remove an adapter binding from an endpoint",
)

## Evals API commands
evals_app = app.command(App(name="evals", help="Run and manage model evaluations", help_epilogue=EVALS_HELP_EXAMPLES))
evals_app.command(
    (f"{_CLI}.evals.create:create"), alias="-c", help="Create a new eval job", help_epilogue=EVALS_CREATE_HELP_EXAMPLES
)
evals_app.command((f"{_CLI}.evals.list:list"), alias="ls", help="List eval jobs")
evals_app.command((f"{_CLI}.evals.retrieve:retrieve"), alias="get", help="Get eval job details")
evals_app.command((f"{_CLI}.evals.status:status"), help="Get an eval job's status")

## Telemetry API commands
telemetry_app = app.command(App(name="telemetry", help="Configure CLI telemetry"))
telemetry_app.command((f"{_CLI}.telemetry.status:status"), help="Show telemetry status")
telemetry_app.command((f"{_CLI}.telemetry.enable:enable"), help="Enable telemetry")
telemetry_app.command((f"{_CLI}.telemetry.disable:disable"), help="Disable telemetry")


# Hidden from the help page, but the actual namespace for command resolution
# Visible initially to install tab completion properly, but set to be hidden after installation
beta_root_app = App(name="beta", help="Experimental and beta features")
beta_app = app.command(beta_root_app)

### Clusters API commands
clusters_app = beta_app.command(
    App(name="clusters", help="Create and manage GPU clusters", help_epilogue=BETA_CLUSTERS_HELP_EXAMPLES)
)
clusters_app.command((f"{_CLI}.beta.clusters.list:list"), alias="ls", help="List your clusters")
clusters_app.command(
    (f"{_CLI}.beta.clusters.create:create"),
    alias="-c",
    help="Create a new cluster",
    help_epilogue=BETA_CLUSTERS_CREATE_HELP_EXAMPLES,
)
clusters_app.command((f"{_CLI}.beta.clusters.retrieve:retrieve"), alias="get", help="Get cluster details")
clusters_app.command(
    (f"{_CLI}.beta.clusters.update:update"),
    help="Update a cluster",
    help_epilogue=BETA_CLUSTERS_UPDATE_HELP_EXAMPLES,
)
clusters_app.command((f"{_CLI}.beta.clusters.delete:delete"), alias="-d", help="Delete a cluster")
clusters_app.command((f"{_CLI}.beta.clusters.list_regions:list_regions"), help="List regions for deploying clusters")
clusters_app.command(
    (f"{_CLI}.beta.clusters.get_credentials:get_credentials"),
    help="Get credentials for a cluster",
    help_epilogue=BETA_CLUSTERS_GET_CREDENTIALS_HELP_EXAMPLES,
)
clusters_app.command(
    (f"{_CLI}.beta.clusters.ssh:ssh"),
    help="SSH into a cluster via an OIDC-signed certificate",
)

### Clusters > Storage API commands
storage_app = clusters_app.command(
    App(
        name="storage",
        help="Manage cluster storage volumes",
        group="Subcommands",
        help_epilogue=BETA_CLUSTERS_STORAGE_HELP_EXAMPLES,
    )
)
storage_app.command((f"{_CLI}.beta.clusters.storage.list:list"), alias="ls", help="List storage volumes for a cluster")
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.create:create"),
    alias="-c",
    help="Create a new storage volume for a cluster",
    help_epilogue=BETA_CLUSTERS_STORAGE_CREATE_HELP_EXAMPLES,
)
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.update:update"),
    help="Resize a storage volume",
    help_epilogue=BETA_CLUSTERS_STORAGE_UPDATE_HELP_EXAMPLES,
)
storage_app.command(
    (f"{_CLI}.beta.clusters.storage.retrieve:retrieve"),
    alias="get",
    help="Get storage volume details",
)
storage_app.command((f"{_CLI}.beta.clusters.storage.delete:delete"), help="Delete a storage volume", alias="-d")

### Clusters > Remediations API commands
remediations_app = clusters_app.command(
    App(
        name="remediations",
        help="Manage node remediations",
        group="Subcommands",
        help_epilogue=BETA_CLUSTERS_REMEDIATIONS_HELP_EXAMPLES,
    )
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.create:create"),
    alias="-c",
    help="Create a node remediation",
    help_epilogue=BETA_CLUSTERS_REMEDIATIONS_CREATE_HELP_EXAMPLES,
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.list:list"),
    alias="ls",
    help="List node remediations",
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.retrieve:retrieve"),
    alias="get",
    help="Get remediation details",
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.approve:approve"),
    help="Approve a pending remediation",
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.cancel:cancel"),
    help="Cancel a pending remediation",
)
remediations_app.command(
    (f"{_CLI}.beta.clusters.remediations.reject:reject"),
    help="Reject a pending remediation",
)

### Beta Endpoints API commands

beta_endpoints_app = beta_app.command(
    App(
        name="endpoints",
        help="Deploy and manage dedicated inference endpoints",
        help_epilogue=BETA_ENDPOINTS_HELP_EXAMPLES,
    )
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.deploy:deploy"),
    help="Create a deployment on a new or existing endpoint",
    help_epilogue=BETA_ENDPOINTS_DEPLOY_HELP_EXAMPLES,
    sort_key=1,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.list:list"),
    name="ls",
    help="List project, organization, or public endpoints",
    help_epilogue=BETA_ENDPOINTS_LS_HELP_EXAMPLES,
    sort_key=2,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.retrieve:retrieve"),
    name="get",
    help="Get endpoint or deployment details by ID",
    help_epilogue=BETA_ENDPOINTS_GET_HELP_EXAMPLES,
    sort_key=3,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.retrieve:retrieve"), show=False
)  # This is just here to allow the default command to work
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.update:update"),
    help="Update a deployment's name, autoscaling, or traffic weight",
    help_epilogue=BETA_ENDPOINTS_UPDATE_HELP_EXAMPLES,
    sort_key=4,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.rm:rm"),
    name="rm",
    alias="-d",
    sort_key=5,
    help="Delete an endpoint, deployment, A/B experiment, or shadow experiment by ID",
    help_epilogue=BETA_ENDPOINTS_RM_HELP_EXAMPLES,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.shadow:shadow"),
    help="Mirror sampled live traffic to a new deployment without serving its responses",
    help_epilogue=BETA_ENDPOINTS_SHADOW_HELP_EXAMPLES,
    sort_key=9999,
)
beta_endpoints_app.command(
    (f"{_CLI}.beta.endpoints.ab:ab"),
    help="Create a variant deployment and split live traffic from a control deployment",
    help_epilogue=BETA_ENDPOINTS_AB_HELP_EXAMPLES,
    sort_key=9999,
)

### Beta Models API commands
beta_models_app = beta_app.command(
    App(
        name="models",
        help="Register and manage models for dedicated inference",
        help_epilogue=BETA_MODELS_HELP_EXAMPLES,
    )
)
beta_models_app.command((f"{_CLI}.beta.models.list:list"), alias="ls", help="List models in the caller's project")
beta_models_app.command(
    (f"{_CLI}.beta.models.public:public"),
    help="List publicly-visible models across all projects",
    help_epilogue=BETA_MODELS_PUBLIC_HELP_EXAMPLES,
)
beta_models_app.command(
    (f"{_CLI}.beta.models.org:org"), help="List internal-visibility models in the caller's organization"
)
beta_models_app.command(
    (f"{_CLI}.beta.models.create:create"),
    alias="-c",
    help="Register a model (does not upload files)",
    help_epilogue=BETA_MODELS_CREATE_HELP_EXAMPLES,
)
beta_models_app.command(
    (f"{_CLI}.beta.models.list_files:list_files"), name="ls-files", help="List files in a model or adapter"
)
beta_models_app.command(
    (f"{_CLI}.beta.models.list_revisions:list_revisions"), name="ls-revisions", help="List revisions for a model"
)
beta_models_app.command((f"{_CLI}.beta.models.retrieve:retrieve"), alias="get", help="Get a model by ID")
beta_models_app.command(
    (f"{_CLI}.beta.models.update:update"),
    help="Update a model (provided fields only)",
    help_epilogue=BETA_MODELS_UPDATE_HELP_EXAMPLES,
)
beta_models_app.command(
    (f"{_CLI}.beta.models.rm:rm"),
    name="rm",
    alias="-d",
    help="Delete a model (metadata; does not delete files)",
)
beta_models_app.command(
    (f"{_CLI}.beta.models.upload:upload"),
    help="Upload files to a model or adapter",
    help_epilogue=BETA_MODELS_UPLOAD_HELP_EXAMPLES,
)
beta_models_app.command(
    (f"{_CLI}.beta.models.download:download"),
    help="Download files from a model or adapter",
    help_epilogue=BETA_MODELS_DOWNLOAD_HELP_EXAMPLES,
)

### Beta Models > Remote Uploads API commands
beta_models_remote_uploads_app = beta_models_app.command(
    App(
        name="remote-uploads",
        help="Import model weights from Hugging Face or presigned URLs",
        group="Subcommands",
        help_epilogue=BETA_MODELS_REMOTE_UPLOADS_HELP_EXAMPLES,
    )
)
beta_models_remote_uploads_app.command(
    (f"{_CLI}.beta.models.remote_uploads.create:create"),
    alias="-c",
    help="Start a remote upload job",
    help_epilogue=BETA_MODELS_REMOTE_UPLOADS_CREATE_HELP_EXAMPLES,
)
beta_models_remote_uploads_app.command(
    (f"{_CLI}.beta.models.remote_uploads.retrieve:retrieve"),
    alias="get",
    help="Get a remote upload job by ID",
)
beta_models_remote_uploads_app.command(
    (f"{_CLI}.beta.models.remote_uploads.list:list"),
    alias="ls",
    help="List remote upload jobs",
)

### Beta Models > Configs API commands
beta_models_app.command(
    (f"{_CLI}.beta.models.configs.list:list"),
    name="configs",
    help="List deployable configs for a model",
    help_epilogue=BETA_MODELS_CONFIGS_HELP_EXAMPLES,
)

### Jig commands
jig_app = beta_app.command(
    App(name="jig", help="Build, deploy, and manage custom containers", help_epilogue=JIG_HELP_EXAMPLES)
)
jig_app.command((f"{_CLI}.beta.jig.jig:init"), help="Initialize configuration for a Jig deployment")
jig_app.command(
    (f"{_CLI}.beta.jig.jig:dockerfile_cli"), name="dockerfile", help="Generate Dockerfile from jig configuration"
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:build_cli"),
    name="build",
    help="Build container image",
    help_epilogue=JIG_BUILD_HELP_EXAMPLES,
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:push_cli"), name="push", help="Push image to registry", help_epilogue=JIG_PUSH_HELP_EXAMPLES
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:deploy_cli"),
    name="deploy",
    help="Deploy model to Together",
    help_epilogue=JIG_DEPLOY_HELP_EXAMPLES,
)
jig_app.command((f"{_CLI}.beta.jig.jig:status_cli"), name="status", help="Get deployment status")
jig_app.command((f"{_CLI}.beta.jig.jig:endpoint_cli"), name="endpoint", help="Get deployment endpoint URL")
jig_app.command(
    (f"{_CLI}.beta.jig.jig:logs_cli"), name="logs", help="Get deployment logs", help_epilogue=JIG_LOGS_HELP_EXAMPLES
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:destroy_cli"),
    name="destroy",
    help="Destroy deployment",
    help_epilogue=JIG_DESTROY_HELP_EXAMPLES,
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:submit_cli"),
    name="submit",
    help="Submit a job to the deployment",
    help_epilogue=JIG_SUBMIT_HELP_EXAMPLES,
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:job_status_cli"),
    name="job-status",
    help="Get status of a specific job",
    help_epilogue=JIG_JOB_STATUS_HELP_EXAMPLES,
)
jig_app.command(
    (f"{_CLI}.beta.jig.jig:queue_status_cli"), name="queue-status", help="Get queue metrics for the deployment"
)
jig_app.command((f"{_CLI}.beta.jig.jig:list_deployments_cli"), name="list", alias="ls", help="List all deployments")

secrets_app = jig_app.command(
    App(name="secrets", help="Manage deployment secrets", group="Subcommands", help_epilogue=JIG_SECRETS_HELP_EXAMPLES)
)
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_set_cli"),
    name="set",
    help="Set a secret (create or update)",
    help_epilogue=JIG_SECRETS_SET_HELP_EXAMPLES,
)
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_unset_cli"),
    name="unset",
    help="Remove a secret from local state",
    help_epilogue=JIG_SECRETS_UNSET_HELP_EXAMPLES,
)
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_delete_cli"),
    name="delete",
    help="Delete a secret and unset it locally",
    alias="-d",
    help_epilogue=JIG_SECRETS_DELETE_HELP_EXAMPLES,
)
secrets_app.command(
    (f"{_CLI}.beta.jig.jig:secrets_list_cli"), name="list", alias="ls", help="List all secrets with sync status"
)

### Jig > volumes
storage_app = jig_app.command(
    App(
        name="volumes",
        help="Manage volumes for Jig deployments",
        group="Subcommands",
        help_epilogue=JIG_VOLUMES_HELP_EXAMPLES,
    )
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_create_cli"),
    name="create",
    alias="-c",
    help="Create a new volume for a Jig deployment",
    help_epilogue=JIG_VOLUMES_CREATE_HELP_EXAMPLES,
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_update_cli"),
    name="update",
    help="Update a volume and re-upload files",
    help_epilogue=JIG_VOLUMES_UPDATE_HELP_EXAMPLES,
)
storage_app.command((f"{_CLI}.beta.jig.jig:jig_volumes_delete_cli"), name="delete", help="Delete a volume", alias="-d")
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_describe"),
    alias=("retrieve", "get"),
    name="describe",
    help="Get volume details",
)
storage_app.command(
    (f"{_CLI}.beta.jig.jig:jig_volumes_list"), name="list", alias="ls", help="List volumes for a Jig deployment"
)

app.command((f"{_CLI}.whoami:whoami"), help="Show the current user")

app.help_epilogue = TOP_LEVEL_HELP_EXAMPLES
endpoints_app.help_epilogue = ENDPOINTS_HELP_EXAMPLES


def main() -> None:
    install_completion(app)

    # Shown in the root help page, but not a functional command
    BETA_GROUP_TITLE = "Beta Commands"
    app.command(App(name="beta clusters", help="Create and manage GPU clusters", group=BETA_GROUP_TITLE))
    app.command(
        App(name="beta endpoints", help="Deploy and manage dedicated inference endpoints", group=BETA_GROUP_TITLE)
    )
    app.command(
        App(name="beta models", help="Register and manage models for dedicated inference", group=BETA_GROUP_TITLE)
    )
    app.command(App(name="beta jig", help="Container deployment", group=BETA_GROUP_TITLE))
    beta_root_app.show = False

    _propagate_global_param_group(app)

    app.meta()
