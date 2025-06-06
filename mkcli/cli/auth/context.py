from typing import Annotated

import typer

from mkcli.core.enums import Format
from mkcli.core.models import ContextCatalogue
from mkcli.core.models.context import default_context, Context
from mkcli.core.session import open_context_catalogue
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console


_HELP: dict = {
    "general": "Manage authentication contexts",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command()
def show(
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Show current auth context"""
    cat = ContextCatalogue.from_storage()

    console.display(
        "[bold green]Current auth context:[/bold green]"
    )  # TODO: show only with verbose
    console.display_json(cat.current_context.json())
    console.draw_rule("Summary:")
    console.display(
        f"Current auth context is:[bold green] {cat.current_context.name}[/bold green]"
    )
    console.draw_rule()


@app.command(name="list")
def _list(
    format: Annotated[
        Format, typer.Option("--format", "-f")
    ] = APP_SETTINGS.default_format,
):
    """Remove given auth context from the catalogue"""
    with open_context_catalogue() as cat:
        contexts = cat.list_all()
    match format:
        case Format.TABLE:
            console.display_table(
                title="Available Auth Contexts",
                columns=[
                    "Name",
                    "Client_id",
                    "Realm",
                    "Scope",
                    "Region",
                    "Identity server",
                ],
                rows=[ctx.as_table_row() for ctx in contexts],
            )
        case Format.JSON:
            console.display([ctx.model_dump() for ctx in contexts])


@app.command()
def add(
    name: str,
    client_id: Annotated[
        str, typer.Option(prompt=True, help="Client ID for the new auth context")
    ] = default_context.client_id,
    realm: Annotated[
        str, typer.Option(prompt=True, help="Realm for the new auth context")
    ] = default_context.realm,
    scope: Annotated[
        str, typer.Option(prompt=True, help="Scope for the new auth context")
    ] = default_context.scope,
    region: Annotated[
        str, typer.Option(prompt=True, help="Region for the new auth context")
    ] = default_context.region,
    identity_server: Annotated[
        str,
        typer.Option(prompt=True, help="Identity server URL for the new auth context"),
    ] = default_context.identity_server_url,
):
    """Prompt for new auth context and add it to the catalogue"""

    console.display("[bold green]Creating a new auth context...[/bold green]")
    new_ctx = Context(
        name=name,
        client_id=client_id,
        realm=realm,
        scope=scope,
        region=region,
        identity_server_url=identity_server,
        public_key=None,
    )
    console.display_json(new_ctx.json())

    with open_context_catalogue() as cat:
        if name in cat.list_available():
            console.display(
                f"[bold red]Auth context named '{name}' already exists![/bold red]. Aborting."
            )
            typer.Abort()
        cat.add(new_ctx)


@app.command()
def delete(
    names: Annotated[
        list[str], typer.Argument(help="Names of the auth context to delete")
    ],
    auto_confirm: Annotated[bool, typer.Option("--confirm", "-y")] = False,
):
    """Remove given auth context from the catalogue"""
    with open_context_catalogue() as cat:
        for name in names:
            confirmed = auto_confirm or typer.confirm(
                f"Are you sure you want to delete auth context '{name}'?"
            )
            if name not in cat.list_available():
                console.display(
                    f"[bold red]Auth context '{name}' not found![/bold red]"
                )
                return

            if confirmed is False:
                console.display("Aborted.")
                return
            cat.delete(name)

        console.display(
            f"[bold green]Auth context '{name}' deleted successfully![/bold green]"
        )


@app.command()
def duplicate(
    ctx: Annotated[str, typer.Argument(help="Name of the auth context to duplicate")],
    name: Annotated[
        str,
        typer.Option("--name", "-n", prompt=True, help="Name for the new auth context"),
    ],
):
    """Remove given auth context from the catalogue"""
    with open_context_catalogue() as cat:
        if ctx not in cat.list_available():
            console.display(f"[bold red]Auth context '{ctx}' not found![/bold red]")
            return
        if name in cat.list_available():
            console.display(
                f"[bold red]Auth context named '{name}' already exists![/bold red]. Aborting."
            )
            typer.Abort()

        copy = cat.get(ctx)
        copy.name = name
        cat.add(copy)

        console.display(
            f"[bold green]Duplicated auth context '{ctx}' into {name}![/bold green]"
        )
