import typer
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.utils import console


app = typer.Typer(no_args_is_help=True, help="Authorization token management")


@app.command()
def clear():
    """Clear the current access token from the authorization session (current context)"""
    with open_context_catalogue() as cat:
        s = State(cat.current_context)
        s.clear()


@app.command()
def refresh():
    """Refresh the current access token from the authorization session (current context)"""
    with open_context_catalogue() as cat:
        s = State(cat.current_context)
        s.renew_token()


@app.command()
def show():
    """Show the current access token from the authorization session (current context)"""
    with open_context_catalogue() as cat:
        s = State(cat.current_context)

        if s.token is not None:
            console.display(s.token)
        else:
            console.display(
                "No access token found in the current context. "
                "Try running `mkcli auth token refresh` to obtain a new token."
            )
        cat.save()
