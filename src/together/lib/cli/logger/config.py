from together import AsyncTogether

class CLIConfig:
    client: AsyncTogether
    non_interactive: bool
    json: bool

    def __init__(self, client: AsyncTogether, non_interactive: bool, json: bool):
        self.client = client
        self.non_interactive = non_interactive
        self.json = json