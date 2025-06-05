from typing import Annotated

import typer

from mkcli.core.enums import Format
from mkcli.core.models import ContextCatalogue
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
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Prompt for new auth context and add it to the catalogue"""
    raise NotImplementedError


@app.command()
def delete(
    name: Annotated[str, typer.Argument(help="Name of the auth context to delete")],
    auto_confirm: Annotated[bool, typer.Option("--confirm", "-y")] = False,
):
    """Remove given auth context from the catalogue"""
    confirmed = auto_confirm or typer.confirm(
        f"Are you sure you want to delete auth context '{name}'?"
    )

    with open_context_catalogue() as cat:
        if name not in cat.list_available():
            console.display(f"[bold red]Auth context '{name}' not found![/bold red]")
            return

        if confirmed is False:
            console.display("Aborted.")
            return
        cat.remove(name)

    console.display(
        f"[bold green]Auth context '{name}' deleted successfully![/bold green]"
    )
