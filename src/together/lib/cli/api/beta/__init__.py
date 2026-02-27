from typing_extensions import override

from clypi import Command


class Beta(Command):
    @override
    async def run(self):
        self.print_help()
