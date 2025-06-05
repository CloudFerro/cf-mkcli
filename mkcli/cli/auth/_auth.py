import typer
from mkcli.core.session import open_context_catalogue
from mkcli.utils import console


_HELP: dict = {
    "general": "Cli auth context",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(name="init")
def init(
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Initialize a first auth context"""
    """This command will prompt you for the necessary information to create a new auth context."""
    with open_context_catalogue() as cat:
        if cat.current_context is not None:
            console.display(
                f"[bold red]You are already in the auth context {cat.current_context.name}![/bold red]"
            )
            return

    console.display("[bold green]Initializing a new auth context...[/bold green]")
    name = typer.prompt("Enter the name for the new auth context")
    description = typer.prompt(
        "Enter a description for the new auth context", default=""
    )

    cat.add_context(name, description)
    cat.save()

    console.display(
        f"[bold green]New auth context '{name}' created successfully![/bold green]"
    )
