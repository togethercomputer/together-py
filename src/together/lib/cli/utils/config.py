from typing_extensions import Annotated

from cyclopts import Parameter

from together import AsyncTogether


class CLIConfig:
    client: AsyncTogether
    non_interactive: bool
    json: bool

    def __init__(self, client: AsyncTogether, non_interactive: bool, json: bool):
        self.client = client
        self.non_interactive = non_interactive
        self.json = json


CLIConfigParameter = Annotated[CLIConfig, Parameter(parse=False)]
