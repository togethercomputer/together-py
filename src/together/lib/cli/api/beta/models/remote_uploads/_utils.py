from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse, urlunparse

from together.lib.cli.utils._console import console

# Matches hermes ParseRemoteSource: org/model or org/model@revision.
_HF_REPO_ID = re.compile(r"^[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+(@[a-zA-Z0-9_\-\.]+)?$")
_HF_HOSTS = frozenset({"huggingface.co", "www.huggingface.co"})

if TYPE_CHECKING:
    from together.types.beta.models.remote_upload_create_response import RemoteUploadCreateResponse
    from together.types.beta.models.remote_upload_retrieve_response import RemoteUploadRetrieveResponse


def apply_huggingface_revision(remote_url: str, revision: str | None) -> str:
    """Pin a Hugging Face revision on a remote-upload source URL.

    CreateRemoteUpload has no revision field. Hermes reads the pin from an
    ``@<commit|tag|branch>`` suffix on a Hugging Face repo id or URL.
    """
    if not revision:
        return remote_url

    if remote_url.startswith(("http://", "https://")):
        parsed = urlparse(remote_url)
        if parsed.hostname in _HF_HOSTS:
            return _pin_hf_url_revision(remote_url, parsed, revision)
        raise ValueError("--revision is only supported for Hugging Face sources")

    if _HF_REPO_ID.match(remote_url):
        return _pin_repo_id_revision(remote_url, revision)

    raise ValueError("--revision is only supported for Hugging Face sources")


def _pin_repo_id_revision(remote_url: str, revision: str) -> str:
    _, separator, embedded = remote_url.partition("@")
    if separator:
        if embedded != revision:
            raise ValueError("conflicting revisions from --from (@…) and --revision")
        return remote_url
    return f"{remote_url}@{revision}"


def _pin_hf_url_revision(remote_url: str, parsed: ParseResult, revision: str) -> str:
    path = parsed.path.strip("/")
    parts = path.split("/", 2)
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"invalid Hugging Face URL (expected https://huggingface.co/org/model): {remote_url}")
    _, separator, embedded = f"{parts[0]}/{parts[1]}".partition("@")
    if separator:
        if embedded != revision:
            raise ValueError("conflicting revisions from --from (@…) and --revision")
        return remote_url
    parts[1] = f"{parts[1]}@{revision}"
    new_path = "/" + "/".join(parts)
    if parsed.path.endswith("/") and not new_path.endswith("/"):
        new_path += "/"
    return urlunparse(parsed._replace(path=new_path))


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
