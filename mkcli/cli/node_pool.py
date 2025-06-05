from typing import Annotated

import typer

from mkcli.core import mappings
from mkcli.core.models import NodePoolPayload
from mkcli.core.state import State
from mkcli.settings import DefaultNodePoolSettings
from mkcli.utils import console, names
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import open_context_catalogue

_HELP: dict = {
    "general": "Manage Kubernetes cluster's node pools",
    "create": "Create a new node pool",
    "update": "Update the node pool with given id",
    "delete": "Delete the node pool with given id",
    "list": "List all node pools in the cluster",
    "cluster_id": "Cluster ID to operate on",
    "node_pool_id": "Node pool ID to operate on",
    "name": "Node pool name, if None, generate with petname",
    "node_count": "Number of nodes in the pool",
    "min_nodes": "Minimum number of nodes in the pool",
    "max_nodes": "Maximum number of nodes in the pool",
    "autoscale": "Enable autoscaling for the node pool",
    "flavor": "Machine flavor for the node pool, if None, use the default flavor",
    "dry_run": "If True, do not perform any actions, just print the payload",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])

DEFAULT_NODEPOOL = DefaultNodePoolSettings()


@app.command()
def create(
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
    name: str = typer.Option(
        None, help="Node pool name, if None, generate with petname"
    ),
    node_count: int = typer.Option(
        DEFAULT_NODEPOOL.node_count, help=_HELP["node_count"]
    ),
    min_nodes: int = typer.Option(DEFAULT_NODEPOOL.min_nodes, help=_HELP["min_nodes"]),
    max_nodes: int = typer.Option(DEFAULT_NODEPOOL.max_nodes, help=_HELP["max_nodes"]),
    autoscale: bool = typer.Option(DEFAULT_NODEPOOL.autoscale, help=_HELP["autoscale"]),
    flavor: str = typer.Option(
        DEFAULT_NODEPOOL.flavor,
        help=_HELP["flavor"],
    ),
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Create a new node pool"""
    with open_context_catalogue() as cat:  # TODO: move mappings to callback
        state = State(cat.current_context)
        client = MK8SClient(state)
        region_map = mappings.get_regions_mapping(client)
        flavor_map = mappings.get_machine_spec_mapping(
            client, region_map[state.ctx.region].id
        )
        flavor = flavor_map.get(flavor)

    if name is None:
        name = names.generate()

    node_pool_data = {
        "name": name,
        "node_count": node_count,
        "min_nodes": min_nodes,
        "max_nodes": max_nodes,
        "autoscale": autoscale,
        "machine_spec": {"id": flavor.id},
    }

    node_pool_data = NodePoolPayload.model_validate(node_pool_data)
    if dry_run:
        console.display(f"[bold yellow]Dry run mode:[/bold yellow] {node_pool_data}")
        return
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        response = client.create_node_pool(
            cluster_id=cluster_id, node_pool_data=node_pool_data.dict()
        )
        console.display(f"[bold green]Node Pool created:[/bold green] {response}")


@app.command(name="list")
def _list(
    cluster_id: str = typer.Argument(..., help=_HELP["cluster_id"]),
):
    """List all node pools in the cluster"""
    console.display(f"Listing node pools for cluster ID: {cluster_id}")

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        node_pools = client.list_node_pools(cluster_id)

    console.display("[bold green]Node Pools:[/bold green]")
    console.display(node_pools)  # TODO: format outp
    # ut nicely


@app.command()
def update():
    raise NotImplementedError


@app.command()
def delete(
    cluster_id: str = typer.Argument(..., help=_HELP["cluster_id"]),
    node_pool_id: str = typer.Argument(..., help=_HELP["node_pool_id"]),
    auto_confirm: Annotated[bool, typer.Option("--confirm", "-y")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Delete a node pool"""
    console.display(f"Listing node pools for cluster ID: {cluster_id}")
    confirmed = auto_confirm or typer.confirm(
        f"Are you sure you want to delete node pool {node_pool_id} in cluster {cluster_id}?"
    )
    if not confirmed:
        console.display("Aborted.")
        return

    if dry_run:
        console.display(
            f"[bold yellow]Dry run mode:[/bold yellow] would delete node pool {node_pool_id} from cluster {cluster_id}"
        )
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        client.delete_node_pool(cluster_id=cluster_id, node_pool_id=node_pool_id)

    console.display(f"Node pool {node_pool_id} deleted from cluster {cluster_id}.")
