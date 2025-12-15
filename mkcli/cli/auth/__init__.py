from ._auth import app  # noqa: F401
from .context import app as context_app  # noqa: F401
from ._token import app as token_app  # noqa: F401
from .key import app as key_app  # noqa: F401
from mkcli.settings import APP_SETTINGS


app.add_typer(
    token_app,
    name="token",
    no_args_is_help=True,
    help="OpenID token management [BETA]",
    hidden=not APP_SETTINGS.beta_feature_flag,
)
app.add_typer(key_app, name="key", no_args_is_help=True)
app.add_typer(context_app, name="context | ctx", no_args_is_help=True)
