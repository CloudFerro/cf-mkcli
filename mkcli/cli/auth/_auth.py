from typing import Annotated

import typer
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.core.enums import SupportedRealms, SupportedRegions
from mkcli.utils import console
from mkcli.core.models.context import (
    default_context,
    Context,
)


_HELP: dict = {
    "general": "mkcli authorization and authentication management",
    "init": "Initialize authentication session",
    "end": "End authentication session and clear saved tokens",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(name="init", help=_HELP["init"])
def init(
    realm: Annotated[
        SupportedRealms, typer.Option(prompt=True, help="Realm name")
    ] = SupportedRealms.CREODIAS,
    region: Annotated[
        SupportedRegions, typer.Option(prompt=True, help="Region name")
    ] = SupportedRegions.WAW4_1,
):
    """
    Initialize your first auth context (with default attribute values).
    This command is used to set up the initial authentication context for the CLI.
    It will prompt you for the necessary information to create a new auth context (just like `mkli auth context add`).
    """
    new_ctx = Context(
        name=default_context.name,
        client_id=default_context.client_id,
        realm=realm,
        scope=default_context.scope,
        region=region,
        identity_server_url=default_context.identity_server_url,
    )

    with open_context_catalogue() as cat:
        cat.add(new_ctx)
        cat.switch(new_ctx.name)
        console.display(
            f"[bold green]Initialized a new auth session in `{cat.current_context.name} context`.[/bold green]"
        )
        # Validate token or log in browser
        state = State(cat.current_context)
        state.renew_token()
        console.display(
            f"[bold green]Successfully refreshed token in `{cat.current_context.name}` context.[/bold green]"
        )
        cat.save()


@app.command(name="end", help=_HELP["end"])
def end():
    """End all saved auth sessions"""
    with open_context_catalogue() as cat:
        cat.purge()
        console.display(
            "[bold green]All saved auth sessions ended and cleared.[/bold green]"
        )
