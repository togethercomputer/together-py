from typing import List

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Select

class Prompt(App[str]):
    # CSS_PATH = "select.tcss"
    def __init__(self, values: List[str]):
        self.values = values
        super().__init__()
    
    def on_mount(self) -> None:
        self.title = "Endpoint Deployment"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select.from_values(self.values, name="Available Hardware")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.exit(str(event.value))


def promptValue(values: List[str]) -> str:
    app = Prompt(values=values)
    return app.run()