import json
from typing import Annotated

import typer

from mkcli.core import mappings
from mkcli.core.enums import Format
from mkcli.core.exceptions import FlavorNotFound
from mkcli.core.models import NodePoolPayload
from mkcli.core.state import State
from mkcli.settings import APP_SETTINGS
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
    "from_json": "Node-pool payload in JSON format, if None, use provided options",
    "dry_run": "If True, do not perform any actions, just print the payload",
    "format": "Output format, either 'table' or 'json'",
    "shared_networks": "List of shared networks for the node pool",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])

DEFAULT_NODEPOOL = NodePoolPayload()


@app.command()
def create(
    flavor_name: Annotated[str, typer.Option("--flavor", help=_HELP["flavor"])],
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
    name: str = typer.Option(help=_HELP["name"]),
    node_count: int = typer.Option(DEFAULT_NODEPOOL.size, help=_HELP["node_count"]),
    min_nodes: int = typer.Option(DEFAULT_NODEPOOL.size_min, help=_HELP["min_nodes"]),
    max_nodes: int = typer.Option(DEFAULT_NODEPOOL.size_max, help=_HELP["max_nodes"]),
    shared_networks: list[str] = typer.Option(None, help=_HELP["shared_networks"]),
    autoscale: bool = typer.Option(DEFAULT_NODEPOOL.autoscale, help=_HELP["autoscale"]),
    from_json: Annotated[
        NodePoolPayload,
        typer.Option(
            parser=NodePoolPayload.from_json,
            help=_HELP["from_json"],
        ),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Create a new node pool"""
    if from_json is not None:
        console.display(
            "Using provided node-pool payload from JSON, ignoring other options."
        )
        new_nodepool = from_json
    else:
        with open_context_catalogue() as cat:  # TODO: move mappings to callback
            state = State(cat.current_context)
            client = MK8SClient(state)
            region_map = mappings.get_regions_mapping(client)
            flavor_map = mappings.get_machine_spec_mapping(
                client, region_map[state.ctx.region].id
            )
            flavor = flavor_map.get(flavor_name)

        if flavor is None:
            raise FlavorNotFound(
                flavor_name=flavor_name, available_flavors=list(flavor_map.keys())
            )

        if name is None:
            name = names.generate()

        node_pool_data = {
            "name": name,
            "size": node_count,
            "min_nodes": min_nodes,
            "max_nodes": max_nodes,
            "autoscale": autoscale,
            "shared_networks": shared_networks or [],
            "machine_spec": {"id": flavor.id},
        }

        new_nodepool = NodePoolPayload.model_validate(node_pool_data)

    if dry_run:
        console.display(
            f"[bold yellow]Dry run mode:[/bold yellow] {new_nodepool.model_dump_json(indent=2)}"
        )
        return
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        response = client.create_node_pool(
            cluster_id=cluster_id, node_pool_data=new_nodepool.dict()
        )
        console.display(f"[bold green]Node Pool created:[/bold green] {response}")


@app.command(name="list")
def _list(
    cluster_id: str = typer.Argument(..., help=_HELP["cluster_id"]),
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """List all node pools in the cluster"""

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        region_map = mappings.get_regions_mapping(client)
        region = region_map[state.ctx.region]
        flavor_map = mappings.get_machine_spec_mapping(client, region.id)
        reversed_flavor_map = {v.id: v for v in flavor_map.values()}
        node_pools = client.list_node_pools(cluster_id)

    match format:
        case Format.JSON:
            console.display(json.dumps({"node-pools": node_pools}, indent=2))
        case Format.TABLE:
            console.display_table(
                title=f"Node Pools in Cluster {cluster_id}",
                columns=["ID", "Name", "Autoscale", "Status", "Flavor"],
                rows=[
                    [
                        np["id"],
                        np["name"],
                        np["autoscale"],
                        np["status"],
                        reversed_flavor_map.get(np["machine_spec"]["id"]).name
                        if np["machine_spec"]
                        else "N/A",
                    ]
                    for np in node_pools
                ],
            )


@app.command(help=_HELP["update"])
def update(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    node_pool_id: Annotated[str, typer.Argument(help="Node Pool ID to update")],
    node_count: int = typer.Option(None, help=_HELP["node_count"]),
    min_nodes: int = typer.Option(None, help=_HELP["min_nodes"]),
    max_nodes: int = typer.Option(None, help=_HELP["max_nodes"]),
    shared_networks: list[str] = typer.Option(None, help=_HELP["shared_networks"]),
    autoscale: bool = typer.Option(None, help=_HELP["autoscale"]),
):
    """Update the node pool with given id"""

    if not any([node_count, min_nodes, max_nodes, shared_networks, autoscale]):
        console.display(
            "At least one of the options must be provided to update the node pool."
        )
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)

        # Fetch existing node pool
        node_pool = client.get_node_pool(cluster_id, node_pool_id)

        node_pool.size = node_count if node_count is not None else node_pool.size
        node_pool.size_min = min_nodes if min_nodes is not None else node_pool.size_min
        node_pool.size_max = max_nodes if max_nodes is not None else node_pool.size_max
        node_pool.autoscale = (
            autoscale if autoscale is not None else node_pool.autoscale
        )
        node_pool.shared_networks = (
            shared_networks
            if shared_networks is not None
            else node_pool.shared_networks
        )

        # Update the node pool
        updated_node_pool = client.update_node_pool(
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
            node_pool_data=node_pool.dict(),
        )

    console.display(f"Node Pool updated: {updated_node_pool}")


@app.command(name="show")
def show(
    cluster_id: str = typer.Argument(..., help=_HELP["cluster_id"]),
    node_pool_id: str = typer.Argument(..., help=_HELP["node_pool_id"]),
):
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        node_pool = client.get_node_pool(cluster_id, node_pool_id)

    console.display(node_pool)


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
