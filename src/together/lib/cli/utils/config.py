from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import AsyncTogether


class CLIConfig:
    client: AsyncTogether
    non_interactive: bool
    json: bool
    project_id: Optional[str]

    def __init__(self, client: AsyncTogether, non_interactive: bool, json: bool, project_id: Optional[str]):
        self.client = client
        self.non_interactive = non_interactive
        self.json = json
        self.project_id = project_id


CLIConfigParameter = Annotated[CLIConfig, Parameter(parse=False)]
