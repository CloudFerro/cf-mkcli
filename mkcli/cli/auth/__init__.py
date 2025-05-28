import typer
from .context import app as context_app  # noqa: F401
from ._token import app as token_app  # noqa: F401

HELP: str = "Cli auth management"


app = typer.Typer(no_args_is_help=True, help=HELP)

app.add_typer(token_app, name="token", no_args_is_help=True)
app.add_typer(context_app, name="context", no_args_is_help=True)
