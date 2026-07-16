from __future__ import annotations

from typing import TYPE_CHECKING

from together.lib.cli.utils._console import console

if TYPE_CHECKING:
    from together.types.beta.models.remote_upload_create_response import RemoteUploadCreateResponse
    from together.types.beta.models.remote_upload_retrieve_response import RemoteUploadRetrieveResponse


def format_status(status: str | None) -> str:
    if not status:
        return ""
    prefix = "REMOTE_UPLOAD_STATUS_"
    if status.startswith(prefix):
        return status[len(prefix) :]
    return status


def print_remote_upload_detail(
    upload: RemoteUploadCreateResponse | RemoteUploadRetrieveResponse | None,
) -> None:
    if upload is None:
        console.print("Remote upload job not found.")
        return
    if upload.id:
        console.print(f"[dim][primary]Job ID:[/primary][/dim]\t\t[bold]{upload.id}[/bold]")
    if upload.status:
        console.print(f"[dim][primary]Status:[/primary][/dim]\t\t{format_status(upload.status)}")
    if upload.status_message:
        console.print(f"[dim][primary]Message:[/primary][/dim]\t\t{upload.status_message}")
    if upload.api_model_id:
        console.print(f"[dim][primary]Model:[/primary][/dim]\t\t{upload.api_model_id}")
    if upload.remote_url:
        console.print(f"[dim][primary]Source:[/primary][/dim]\t\t{upload.remote_url}")
    if upload.restart_count is not None:
        console.print(f"[dim][primary]Restarts:[/primary][/dim]\t\t{upload.restart_count}")
    if upload.created_at:
        console.print(f"[dim][primary]Created:[/primary][/dim]\t\t{upload.created_at}")
    if upload.updated_at:
        console.print(f"[dim][primary]Updated:[/primary][/dim]\t\t{upload.updated_at}")
