import typer
from mkcli.core.models.context import ContextCatalogue
from mkcli.core.state import State
from mkcli.utils import console

HELP: str = "Cli token management"

app = typer.Typer(no_args_is_help=True, help="Token management")


# Token subcommands
@app.command()
def clear():
    cat = ContextCatalogue.from_storage()  # TODO: cosider typer context
    s = State(cat.current_context)

    s.clear()
    cat.save()


@app.command()
def refresh():
    cat = ContextCatalogue.from_storage()
    s = State(cat.current_context)

    s.renew_token()


@app.command()
def show():
    cat = ContextCatalogue.from_storage()
    s = State(cat.current_context)

    console.display("[bold green]Current access token:[/bold green]")
    console.display(s.token)
