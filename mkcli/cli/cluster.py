import typer
from typing_extensions import Annotated
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import ClusterPayload, ContextCatalogue
from mkcli.core.state import State
from mkcli.utils import console

HELP: str = "Cli auth context"

app = typer.Typer(no_args_is_help=True, help=HELP)


@app.command()
def create(
    cluster_payload: Annotated[
        ClusterPayload, typer.Argument(parser=ClusterPayload.from_json)
    ],
):
    """Create a new k8s cluster"""
    console.Console().print(
        f"Creating cluster {cluster_payload.name} with specification:\n{cluster_payload}"
    )
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)
    _out = client.create_cluster(cluster_data=cluster_payload.dict())
    console.Console().print(_out)


@app.command()
def update(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    payload: Annotated[
        ClusterPayload, typer.Option(parser=ClusterPayload.from_json)
    ] = None,
):
    """Update the cluster with given id"""
    console.Console().print(f"Updating cluster {cluster_id}\nwith {payload}")
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)
    _out = client.update_cluster(cluster_id, cluster_data=payload.dict())
    console.Console().print(_out)


@app.command()
def delete(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    force: Annotated[str, typer.Option(help="Cluster ID")] = False,
):
    """
    Delete the cluster.

    If --force is not used, will ask for confirmation.  # TODO: implement force
    """
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)
    confirmed = typer.confirm(f"Are you sure you want to delete cluster {cluster_id}?")
    if confirmed:
        client.delete_cluster(cluster_id)
        console.Console().print(f"Cluster {cluster_id} deleted.")
    else:
        console.Console().print("Aborted.")


@app.command(name="list")
def _list():
    """List all clusters"""
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)

    clusters = client.get_clusters()
    console.Console().print_json(data=clusters)


@app.command()
def show(cluster_id: Annotated[str, typer.Argument(help="Cluster ID")]):
    """Show cluster details"""
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)
    client = MK8SClient(state)

    _out = client.get_cluster(cluster_id)
    console.Console().print_json(data=_out)


@app.command()
def kube_config(cluster_id: Annotated[str, typer.Argument(help="Cluster ID")]):
    """Download kube-config.yaml"""
    raise NotImplementedError
