from cyclopts import CycloptsError

from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._prompt import confirm


async def assert_explicit_project_id(config: CLIConfig) -> None:
    if config.project_id is not None:
        return

    if config.json is True:
        raise CycloptsError("""Project argument is required.
    
Use the --project flag to specify the project you are operating on or set the TOGETHER_PROJECT_ID environment variable.
You can use `tg whoami` to see your current project ID.""")

    me = await config.client.whoami()
    try:
        if await confirm(f"Confirm that you want to perform this action in the project: {me.project_name}") is False:
            raise CycloptsError("Operation cancelled.")
    except Exception:
        raise CycloptsError("""Project argument is required.
    
Use the --project flag to specify the project you are operating on or set the TOGETHER_PROJECT_ID environment variable.
You can use `tg whoami` to see your current project ID.""") from None
