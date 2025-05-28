import typer


HELP: str = "Cli auth context management"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def show(
    app: typer.Context,
    # format: Annotated[Format, typer.Option("--output-format", "-o")] = Format.table,
):
    """Show current auth context"""
    print(1)
