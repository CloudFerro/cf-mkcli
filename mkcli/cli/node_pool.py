import json
from typing import Annotated, List

import typer

from mkcli.core import mappings
from mkcli.core.enums import Format
from mkcli.core.exceptions import FlavorNotFound
from mkcli.core.models import NodePoolPayload
from mkcli.core.models.labels import Label, Taint
from mkcli.core.models.node_pool import NodePool
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console, names
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import get_auth_adapter
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
    "labels": "List of labels in the format 'key=value', e.g. 'env=prod'",
    "taints": "List of taints in the format 'key=value:effect', e.g. 'key=value:NoSchedule'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])

DEFAULT_NODEPOOL = NodePoolPayload()


def _parse_labels(value):
    k, v = value.split("=")
    return Label(key=k.strip(), value=v.strip())


def _parse_taints(value):
    key, _v = value.split("=")
    value, effect = _v.split(":")
    return Taint(key=key.strip(), value=value.strip(), effect=effect.strip())


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
    labels: Annotated[
        List[Label],
        typer.Option(
            parser=_parse_labels,
            help=_HELP["labels"],
        ),
    ] = None,
    taints: Annotated[
        List[Taint],
        typer.Option(
            parser=_parse_taints,
            help=_HELP["taints"],
        ),
    ] = None,
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
            client = MK8SClient(get_auth_adapter(cat.current_context))
            region_map = mappings.get_regions_mapping(client)
            flavor_map = mappings.get_machine_spec_mapping(
                client, region_map[cat.current_context.region].id
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
            "labels": labels or [],
            "taints": taints or [],
        }

        new_nodepool = NodePoolPayload.model_validate(node_pool_data)

    if dry_run:
        console.display(
            f"[bold yellow]Dry run mode:[/bold yellow] {new_nodepool.model_dump_json(indent=2)}"
        )
        return

    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
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
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        node_pools = client.list_node_pools(cluster_id)

    match format:
        case Format.JSON:
            console.display(
                json.dumps(
                    {"node-pools": [np.model_dump() for np in node_pools]}, indent=2
                )
            )
        case Format.TABLE:
            table = console.ResourceTable(
                title=f"Node Pools in Cluster {cluster_id}",
                columns=NodePool.table_columns,
            )
            for np in node_pools:
                table.add_row(np.as_table_row())
            table.display()


@app.command(help=_HELP["update"])
def update(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    node_pool_id: Annotated[str, typer.Argument(help="Node Pool ID to update")],
    node_count: int = typer.Option(None, help=_HELP["node_count"]),
    min_nodes: int = typer.Option(None, help=_HELP["min_nodes"]),
    max_nodes: int = typer.Option(None, help=_HELP["max_nodes"]),
    shared_networks: list[str] = typer.Option(None, help=_HELP["shared_networks"]),
    autoscale: bool = typer.Option(None, help=_HELP["autoscale"]),
    labels: Annotated[
        List[Label],
        typer.Option(
            parser=_parse_labels,
            help=_HELP["labels"],
        ),
    ] = None,
    taints: Annotated[
        List[Taint],
        typer.Option(
            parser=_parse_taints,
            help=_HELP["taints"],
        ),
    ] = None,
):
    """Update the node pool with given id"""

    if not any(
        [node_count, min_nodes, max_nodes, shared_networks, autoscale, labels, taints]
    ):
        console.display(
            "At least one of the options must be provided to update the node pool."
        )
        return

    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

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
        node_pool.labels = labels if labels is not None else node_pool.labels
        node_pool.taints = taints if taints is not None else node_pool.taints

        console.display_json(node_pool.model_dump_json(indent=2))
        # Update the node pool
        updated_node_pool = client.update_node_pool(
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
            node_pool_data=node_pool.model_dump(),
        )

    console.display("Node Pool updated:")
    console.display_json(json.dumps(updated_node_pool))


@app.command(name="show")
def show(
    cluster_id: str = typer.Argument(..., help=_HELP["cluster_id"]),
    node_pool_id: str = typer.Argument(..., help=_HELP["node_pool_id"]),
):
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
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
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        client.delete_node_pool(cluster_id=cluster_id, node_pool_id=node_pool_id)

    console.display(f"Node pool {node_pool_id} deleted from cluster {cluster_id}.")
