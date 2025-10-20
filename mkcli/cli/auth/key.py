import typer
from mkcli.core.session import open_context_catalogue
from mkcli.utils import console
from mkcli.core.mk8s import MK8SClient
from mkcli.core.adapters import OpenIDAdapter
from mkcli.settings import APP_SETTINGS


app = typer.Typer(no_args_is_help=True, help="MK8s API key management")


@app.command()
def clear():
    """Clear the current API key from the session (current context)"""
    with open_context_catalogue() as cat:
        cat.current_context.api_key = None


@app.command()
def show():
    """Show the current API key from the session (current context)"""
    with open_context_catalogue() as cat:
        if cat.current_context.api_key is not None:
            console.display(cat.current_context.api_key)
        else:
            console.display("No API key found in the current context. ")


@app.command()
def set(
    api_key: str = typer.Argument(..., help="API key to set for the current context"),
):
    """Set the current API key for the session (current context)"""
    with open_context_catalogue() as cat:
        cat.current_context.api_key = api_key
    console.display("API key set successfully.")


@app.command(hidden=not APP_SETTINGS.beta_feature_flag)
def create():
    """Create a new API key"""
    with open_context_catalogue() as cat:
        client = MK8SClient(
            OpenIDAdapter(cat.current_context), cat.current_context.mk8s_api_url
        )
        api_key = client.create_api_key()
        console.display(api_key)
        cat.save()
