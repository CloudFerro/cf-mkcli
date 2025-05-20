import typer

HELP: str = "Cli auth context"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def create():
    """Create a new k8s cluster"""
    ...


@app.command()
def update():
    ...


@app.command()
def delete():
    """
    Delete the cluster.

    If --force is not used, will ask for confirmation.
    """
    ...


@app.command(name='list')
def _list():
    """List all clusters"""
    ...


@app.command()
def show():
    """Show cluster details"""
    ...

