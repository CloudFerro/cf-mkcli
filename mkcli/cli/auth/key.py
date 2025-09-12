import typer
from mkcli.core.session import open_context_catalogue
from mkcli.utils import console


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
