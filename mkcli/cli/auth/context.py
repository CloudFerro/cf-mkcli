import typer

from mkcli.core.models import ContextCatalogue
from mkcli.utils import console


HELP: str = "Cli auth context management"

app = typer.Typer(no_args_is_help=True, help=HELP)


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
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Remove given auth context from the catalogue"""
    cat = ContextCatalogue.from_storage()
    console.display("[bold green]Available auth contexts:[/bold green]")
    console.display(",".join(cat.list_available()))


@app.command()
def add(
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Prompt for new auth context and add it to the catalogue"""
    raise NotImplementedError


@app.command()
def delete(
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Remove given auth context from the catalogue"""
    raise NotImplementedError
