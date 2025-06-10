import typer
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.utils import console

HELP: str = "Auth token management"

app = typer.Typer(no_args_is_help=True, help=HELP)


# Token subcommands
@app.command()
def clear():
    with open_context_catalogue() as cat:
        s = State(cat.current_context)
        s.clear()


@app.command()
def refresh():
    with open_context_catalogue() as cat:
        s = State(cat.current_context)
        s.renew_token()


@app.command()
def show():
    with open_context_catalogue() as cat:
        s = State(cat.current_context)

        console.display("[bold green]Current access token:[/bold green]")
        console.display(s.token)
        cat.save()
