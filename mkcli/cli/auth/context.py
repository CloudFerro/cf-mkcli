import json
from typing import Annotated

import typer

from mkcli.core.enums import AuthType, Format, SupportedRealms, SupportedRegions
from mkcli.core.models.context import default_context, Context
from mkcli.core.session import open_context_catalogue
from mkcli.utils import console


_HELP: dict = {
    "general": "Manage authentication contexts",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command()
def show(
    format: Annotated[Format, typer.Option("--format", "-f")] = Format.TABLE,
):
    """Show current auth context"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context

    if ctx is None:
        console.display(
            "[bold red]No current auth context is set! Use 'mk auth context switch' to set one.[/bold red]"
        )
        typer.Abort()

    match format:
        case Format.TABLE:
            table = console.ResourceTable(
                title="Current Authorization Context",
                columns=Context.table_columns,
            )
            table.add_row(ctx.as_table_row())
            table.display()
        case Format.JSON:
            console.display_json(ctx.json())


@app.command(name="list")
def _list(
    format: Annotated[Format, typer.Option("--format", "-f")] = Format.TABLE,
):
    """Remove given auth context from the catalogue"""
    with open_context_catalogue() as cat:
        contexts = cat.list_all()
    match format:
        case Format.TABLE:
            table = console.ResourceTable(
                title="Available Auth Contexts",
                columns=Context.table_columns,
            )
            for ctx in contexts:
                table.add_row(
                    ctx.as_table_row(),
                    style=console.HIGHLIGHTED if ctx.name == cat.current else None,
                )
            table.display()
            console.draw_rule()
            console.display(f"Current context: [bold]{cat.current}[/bold]")
            console.draw_rule()
        case Format.JSON:
            console.display_json(
                json.dumps({"contexts": [ctx.as_json() for ctx in contexts]}),
            )


@app.command()
def add(
    name: str,
    client_id: Annotated[
        str, typer.Option(prompt=True, help="Client ID for the new auth context")
    ] = default_context.client_id,
    realm: Annotated[
        SupportedRealms,
        typer.Option(prompt=True, help="Realm for the new auth context"),
    ] = SupportedRealms.CREODIAS,
    scope: Annotated[
        str, typer.Option(prompt=True, help="Scope for the new auth context")
    ] = default_context.scope,
    region: Annotated[
        SupportedRegions,
        typer.Option(prompt=True, help="Region for the new auth context"),
    ] = SupportedRegions.WAW4_1,
    identity_server: Annotated[
        str,
        typer.Option(prompt=True, help="Identity server URL for the new auth context"),
    ] = default_context.identity_server_url,
    auth_type: Annotated[
        AuthType,
        typer.Option(prompt=True, help="Authentication type for the new auth context"),
    ] = AuthType.OPENID,
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
        auth_type=auth_type,
    )
    console.display_json(new_ctx.model_dump_json())

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
    """emove given auth context from the catalogue"""
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
    """Duplicate given auth context with a new name"""
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


@app.command()
def edit(
    ctx: Annotated[str, typer.Argument(help="Name of the auth context to update")],
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="New name of the edited auth context"),
    ] = None,
    client_id: Annotated[
        str | None,
        typer.Option("--client_id", help="New Client ID for the edited auth context"),
    ] = None,
    realm: Annotated[
        SupportedRealms | None,
        typer.Option("--realm", help="Realm for the edited auth context"),
    ] = None,
    scope: Annotated[
        str | None, typer.Option("--scope", help="Scope for the edited auth context")
    ] = None,
    region: Annotated[
        SupportedRegions | None,
        typer.Option("--region", help="Region for the edited auth context"),
    ] = None,
    identity_server: Annotated[
        str | None,
        typer.Option(
            "--identity_server", help="Identity server URL for the edited auth context"
        ),
    ] = None,
    auth_type: Annotated[
        AuthType | None,
        typer.Option("--auth_type", help="Auth type for the edited auth context"),
    ] = None,
):
    """Update given auth context"""
    with open_context_catalogue() as cat:
        if ctx not in cat.list_available():
            console.display(f"[bold red]Auth context '{ctx}' not found![/bold red]")
            typer.Abort()

        if name in cat.list_available():
            console.display(
                f"[bold red]Auth context named '{name}' already exists![/bold red]. Aborting."
            )
            typer.Abort()

        context = cat.get(ctx)
        is_active = context.name == cat.current
        context.name = name or context.name
        context.client_id = client_id or context.client_id
        context.realm = realm or context.realm
        context.scope = scope or context.scope
        context.region = region or context.region
        context.identity_server_url = identity_server or context.identity_server_url
        context.auth_type = auth_type or context.auth_type

        cat.delete(ctx)
        if is_active:
            cat.current = context.name
        cat.add(context)

        console.display(f"[bold green]Edited auth context '{ctx}'[/bold green]")
        console.display(context.as_json())  # type: ignore


@app.command()
def switch(
    ctx: Annotated[
        str, typer.Argument(help="Name of the auth context to set as current")
    ],
):
    """Switch to a different auth context"""
    with open_context_catalogue() as cat:
        if ctx not in cat.list_available():
            console.display(f"[bold red]Auth context '{ctx}' not found![/bold red]")
            typer.Abort()

        cat.switch(ctx)
        console.display(
            f"[bold green]Set auth context '{ctx}' as current![/bold green]"
        )
