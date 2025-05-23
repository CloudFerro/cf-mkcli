from .context import app  # noqa: F401
from ._token import app as token_app  # noqa: F401


app.add_typer(token_app, name="token", no_args_is_help=True)
