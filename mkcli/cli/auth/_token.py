import typer

from mkcli.core.state import State


HELP: str = "Cli token management"

app = typer.Typer(no_args_is_help=True, help="Token management")


# Token subcommands
@app.command()
def clear():
    s = State()
    s.clear()


@app.command()
def refresh():
    s = State()
    s.renew_token()


@app.command()
def show():
    s = State()
    print(s.token)
