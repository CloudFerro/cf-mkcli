from typing import Annotated
import typer

from mkcli.core.state import State, Format


HELP: str = "Cli auth context"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def clear_token():
    s = State()
    s.clear()


@app.command()
def refresh_token():
    s = State()
    s.renew_token()


@app.command()
def show_token():
    s = State()
    print(s.token)


@app.command()
def current(
    app: typer.Context,
    format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    s = State()
    s.show(format.json)
