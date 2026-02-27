from __future__ import annotations

from typing_extensions import override

from clypi import Command

from .list import List
from .upload import Upload


class Models(Command):
    subcommand: List | Upload | None

    @override
    async def run(self):
        self.print_help()
