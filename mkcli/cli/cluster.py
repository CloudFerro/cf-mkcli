import typer
from mkcli.core.mk8s import MK8SClient
from mkcli.utils import console

HELP: str = "Cli auth context"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def create():
    """Create a new k8s cluster"""
    ...


@app.command()
def update():
    """Update the cluster with given id"""
    ...


@app.command()
def delete():
    """
    Delete the cluster.

    If --force is not used, will ask for confirmation.
    """
    ...


@app.command(name="list")
def _list():
    """List all clusters"""
    # s = State()
    client = MK8SClient()

    clusters = client.get_clusters()
    console.Console().print(clusters)


@app.command()
def show():
    """Show cluster details"""
    ...
