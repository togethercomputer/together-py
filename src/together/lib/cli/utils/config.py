from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import AsyncTogether


class CLIConfig:
    # None for out-of-band-auth commands (e.g. `beta clusters ssh`) that make no
    # Together API calls; every API-backed command sets a real client.
    client: Optional[AsyncTogether]
    non_interactive: bool
    json: bool
    project_id: Optional[str]

    def __init__(
        self, client: Optional[AsyncTogether], non_interactive: bool, json: bool, project_id: Optional[str]
    ):
        self.client = client
        self.non_interactive = non_interactive
        self.json = json
        self.project_id = project_id


CLIConfigParameter = Annotated[CLIConfig, Parameter(parse=False)]
