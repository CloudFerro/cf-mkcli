import typer

from mkcli.core.models import NodePoolPayload
from mkcli.core.state import State
from mkcli.settings import DefaultNodePoolSettings
from mkcli.utils import console, names
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import open_context_catalogue

HELP: str = "Nodepool operations"

app = typer.Typer(no_args_is_help=True, help=HELP)

DEFAULT_NODEPOOL = DefaultNodePoolSettings()


@app.command()
def create(
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
    name: str = typer.Option(
        None, help="Node pool name, if None, generate with petname"
    ),
    node_count: int = typer.Option(
        DEFAULT_NODEPOOL.node_count, help="Number of nodes in the pool"
    ),
    min_nodes: int = typer.Option(
        DEFAULT_NODEPOOL.min_nodes, help="Minimum number of nodes in the pool"
    ),
    max_nodes: int = typer.Option(
        DEFAULT_NODEPOOL.max_nodes, help="Maximum number of nodes in the pool"
    ),
    autoscale: bool = typer.Option(
        DEFAULT_NODEPOOL.autoscale, help="Enable autoscaling for the node pool"
    ),
    flavor_id: str = typer.Option(
        DEFAULT_NODEPOOL.flavor_id,
        help="Machine flavor ID for the node pool, if None, use default flavor",
    ),
):
    """Create a new node pool"""
    console.display(
        f"Creating node pool '{name}' in cluster ID: {cluster_id} with "
        f"{node_count} nodes (min: {min_nodes}, max: {max_nodes}, autoscale: {autoscale})"
    )
    if name is None:
        name = names.generate()

    node_pool_data = {
        "name": name,
        "node_count": node_count,
        "min_nodes": min_nodes,
        "max_nodes": max_nodes,
        "autoscale": autoscale,
        "machine_spec": {"id": flavor_id},
    }
    node_pool_data = NodePoolPayload.model_validate(node_pool_data)

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        response = client.create_node_pool(
            cluster_id=cluster_id, node_pool_data=node_pool_data.dict()
        )
        console.display(f"[bold green]Node Pool created:[/bold green] {response}")


@app.command(name="list")
def _list(
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
):
    """List all node pools in the cluster"""
    console.display(f"Listing node pools for cluster ID: {cluster_id}")

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        node_pools = client.list_node_pools(cluster_id)

    console.display("[bold green]Node Pools:[/bold green]")
    console.display(node_pools)  # TODO: format output nicely


@app.command()
def update():
    raise NotImplementedError


@app.command()
def delete(
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
    node_pool_id: str = typer.Argument(..., help="Node pool ID to delete"),
):
    """Delete a node pool"""
    console.display(f"Listing node pools for cluster ID: {cluster_id}")
    confirmed = typer.confirm(
        f"Are you sure you want to delete node pool {node_pool_id} in cluster {cluster_id}?"
    )
    if not confirmed:
        console.display("Aborted.")
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        client.delete_node_pool(cluster_id=cluster_id, node_pool_id=node_pool_id)

    console.display(f"Node pool {node_pool_id} deleted from cluster {cluster_id}.")
