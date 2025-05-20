from typing import Annotated
import typer

from mkcli.core.state import State, Format


auth = typer.Typer(no_args_is_help=True, help="Cli context")


@auth.command()
def clear_token():
    s = State()
    s.clear()


@auth.command()
def refresh_token():
    s = State()
    s.renew_token()


@auth.command()
def show_token():
    s = State()
    print(s.token)


@auth.command()
def current(
    auth: typer.Context,
    format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    s = State()
    s.show(format.json)
