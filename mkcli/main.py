import typer
from core.state import State, Format
from typing import Annotated


cli = typer.Typer(no_args_is_help=True)
ctx = typer.Typer(no_args_is_help=True, help="Cli context")

cli.add_typer(ctx, name="ctx", no_args_is_help=True)


@ctx.command()
def clear_token():
    s = State()
    s.clear()


@ctx.command()
def refresh_token():
    s = State()
    s.renew_token()


@ctx.command()
def show_token():
    s = State()
    print("------------------TOKEN-----------------------")
    print(s.token)
    print("==============================================")


@ctx.command()
def current(
    ctx: typer.Context,
    format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    s = State()
    s.show(format.json)


if __name__ == "__main__":
    cli()
