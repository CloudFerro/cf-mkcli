import typer
from typing_extensions import Annotated

from mkcli.cli.extension import AliasGroup
from mkcli.core.session import open_context_catalogue
from mkcli.utils import console
from mkcli.core import adapters
from mkcli.core.models.context import (
    default_context,
    Context,
)
from mkcli.settings import APP_SETTINGS
from mkcli.core.enums import SupportedAuthTypes


_HELP: dict = {
    "general": "Manage authentication sessions",
    "init": "Initialize authentication session",
    "end": "End authentication session and clear saved tokens",
}


app = typer.Typer(cls=AliasGroup, no_args_is_help=True, help=_HELP["general"])


@app.command(name="init", help=_HELP["init"])
def init(
    realm: Annotated[str, typer.Option(prompt=True, help="Realm name")],
    region: Annotated[str, typer.Option(prompt=True, help="Region name")],
    api_url: Annotated[str, typer.Option(prompt=True, help="MK8s API URL")],
    auth_type: Annotated[
        SupportedAuthTypes,
        typer.Option(
            prompt=True if APP_SETTINGS.beta_feature_flag else False,
            help="Auth type [BETA]",
            hidden=not APP_SETTINGS.beta_feature_flag,
        ),
    ] = "api_key",
):
    """
    Initialize your first auth context (with default attribute values).
    This command is used to set up the initial authentication context for the CLI.
    It will prompt you for the necessary information to create a new auth context (just like `mkli auth context add`).
    """
    console.display("[bold green]Creating a new auth context...[/bold green]")
    new_ctx = Context(
        name=default_context.name,
        client_id=default_context.client_id,
        realm=realm,
        region=region,
        mk8s_api_url=api_url,
        identity_server_url=default_context.identity_server_url,
        auth_type=auth_type,
        scope=default_context.scope,
    )

    match auth_type:
        case SupportedAuthTypes.API_KEY.value:
            api_key = typer.prompt("Enter your API key", hide_input=False, default="")
            new_ctx.api_key = api_key
        case SupportedAuthTypes.OPENID.value:
            adapters.OpenIDAdapter(new_ctx).initialize()

    with open_context_catalogue() as cat:
        cat.add(new_ctx)
        cat.switch(new_ctx.name)
        console.display_json(new_ctx.model_dump_json())
        console.display(
            f"[bold green]Initialized a new auth session in `{cat.current_context.name} context`.[/bold green]"
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
