import typer

from mkcli.core.state import State
from mkcli.utils import console


HELP: str = "Cli auth context management"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def show(
    app: typer.Context,
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Show current auth context"""
    s = State()
    data = s.ctx.json()
    console.Console().print(data)
