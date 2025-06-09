import typer
from mkcli.core.state import State
from mkcli.utils import console
from mkcli.core.models.context import default_context, ContextCatalogue

_HELP: dict = {
    "general": "mkcli authorization and authentication management",
    "init": "Initialize your first auth context (with default attribute values).",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


# TODO: consider throwing it out since we have `mkli auth context add`
@app.command(name="init", help=_HELP["init"])
def init():
    """
    Initialize your first auth context (with default attribute values).
    This command is used to set up the initial authentication context for the CLI.
    It will prompt you for the necessary information to create a new auth context (just like `mkli auth context add`).

    """
    try:
        cat = ContextCatalogue().from_storage()
        if cat.current_context is not None:
            console.display(
                f"[bold red]You are already in the auth context {cat.current_context.name}![/bold red]"
            )
            typer.Exit()
    except FileNotFoundError:
        cat = ContextCatalogue()
        cat.add(default_context)
        cat.switch(default_context.name)
        cat.save()
        console.display(
            f"[bold green]Initialized a new default auth context `{default_context.name}`.[/bold green]"
        )
    finally:
        # Validate token or log in browser
        state = State(cat.current_context)
        _ = state.token
        console.display(
            f"[bold green]Successfully refreshed token in `{cat.current_context.name}` context.[/bold green]"
        )
        cat.save()
