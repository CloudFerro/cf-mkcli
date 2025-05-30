import typer
from typing_extensions import Annotated
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import ClusterPayload, ContextCatalogue
from mkcli.core.state import State
from mkcli.utils import console
from mkcli.settings import DefaultClusterSettings


default_cluster = DefaultClusterSettings()

_HELP: dict = {
    "general": "Manage Kubernetes clusters",
    "create": "Create a new k8s cluster",
    "update": "Update the cluster with given id",
    "delete": "Delete the cluster with given id",
    "list": "List all clusters",
    "show": "Show cluster details",
    "name": "Cluster name, if None, generate with petname",
    "get_kubeconfig": "Download kube-config.yaml for the cluster",
    "kubernetes_version": "Kubernetes version ID, if None, use default",
    "master_count": "Number of master nodes, if None, use default",
    "master_flavor_id": "Master node flavor ID, if None, use default",
    "from_json": "Cluster payload in JSON format, if None, use provided options",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command()
def create(
    name: str = typer.Option(
        None,
        help=_HELP["name"],
    ),
    kubernetes_version: str = typer.Option(
        default_cluster.kubernetes_version,
        help=_HELP["kubernetes_version"],
    ),
    master_count: int = typer.Option(
        default=default_cluster.master_count, help=_HELP["master_count"]
    ),
    master_flavor_id: str = typer.Option(
        default=default_cluster.master_flavor_id, help=_HELP["master_flavor_id"]
    ),
    from_json: Annotated[
        ClusterPayload,
        typer.Option(
            parser=ClusterPayload.from_json, help="Cluster payload in JSON format"
        ),
    ] = None,
):
    """Create a new k8s cluster"""

    _payload = {
        "name": name or None,
        "kubernetes_version": {"id": kubernetes_version},
        "control_plane": {
            "custom": {
                "size": master_count,
                "machine_spec": {"id": master_flavor_id},
            }
        },
        "node_pools": [],
    }
    new_cluster = from_json or ClusterPayload(**_payload)

    console.display(f"Creating new cluster: {new_cluster}")
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)
    _out = client.create_cluster(cluster_data=new_cluster.dict())
    console.Console().print(_out)

    cat.save()


@app.command()
def update(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    from_json: Annotated[
        ClusterPayload,
        typer.Argument(
            parser=ClusterPayload.from_json, help="Cluster payload in JSON format"
        ),
    ] = None,
):
    """Update the cluster with given id"""
    console.Console().print(f"Updating cluster {cluster_id}\nwith {from_json}")
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)

    client = MK8SClient(state)
    _out = client.update_cluster(cluster_id, cluster_data=from_json.dict())
    console.Console().print(_out)


@app.command()
def delete(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
):
    """
    Delete the cluster with given id
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

    cat.save()


@app.command()
def show(cluster_id: Annotated[str, typer.Argument(help="Cluster ID")]):
    """Show cluster details"""
    cat = ContextCatalogue.from_storage()
    state = State(cat.current_context)
    client = MK8SClient(state)

    _out = client.get_cluster(cluster_id)
    console.Console().print_json(data=_out)


@app.command()
def get_kubeconfig(cluster_id: Annotated[str, typer.Argument(help="Cluster ID")]):
    """Download kube-config.yaml"""
    raise NotImplementedError
