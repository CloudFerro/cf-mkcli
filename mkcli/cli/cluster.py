import json

import typer
from typing_extensions import Annotated

from mkcli.core.enums import Format
from mkcli.core.exceptions import FlavorNotFound, K8sVersionNotFound
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import ClusterPayload
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.utils import console
from mkcli.settings import DefaultClusterSettings, APP_SETTINGS
from mkcli.core import mappings


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
    "kubernetes_version": "Kubernetes version, if None, use default",
    "master_count": "Number of master nodes, if None, use default",
    "master_flavor": "Master node flavor name, if None, use default",
    "from_json": "Cluster payload in JSON format, if None, use provided options",
    "dry_run": "If True, do not perform any actions, just print the payload",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(help=_HELP["create"])
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
    master_flavor: str = typer.Option(
        default=default_cluster.master_flavor, help=_HELP["master_flavor"]
    ),
    from_json: Annotated[
        ClusterPayload,
        typer.Option(
            parser=ClusterPayload.from_json,
            help=_HELP["from_json"],
        ),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Create a new k8s cluster"""
    if from_json is not None:
        console.display(
            "Using provided cluster payload from JSON, ignoring other options."
        )
        new_cluster = from_json
    else:
        with open_context_catalogue() as cat:
            state = State(cat.current_context)
            client = MK8SClient(state)
            k8sv_map = mappings.get_kubernetes_versions_mapping(client)
            region_map = mappings.get_regions_mapping(client)
            region = region_map[state.ctx.region]
            flavor_map = mappings.get_machine_spec_mapping(client, region.id)
            flavor = flavor_map.get(master_flavor)

        if flavor is None:
            raise FlavorNotFound(
                flavor_name=master_flavor, available_flavors=list(flavor_map.keys())
            )

        new_cluster = ClusterPayload.from_cli_args(
            name=name,
            k8s_version_id=k8sv_map[kubernetes_version].id,
            master_count=master_count,
            master_flavor=flavor.id,
        )

    console.display(f"Creating new cluster: {new_cluster}")

    if dry_run:
        console.display(
            f"[bold yellow]Dry run mode:[/bold yellow] would create cluster with data: {new_cluster}"
        )
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        _out = client.create_cluster(cluster_data=new_cluster.dict())

    console.display(_out)


@app.command(help=_HELP["update"])
def update(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    kubernetes_version: str = typer.Option(None, help=_HELP["kubernetes_version"]),
    master_count: int = typer.Option(
        None, help=_HELP["master_count"]
    ),  # TODO(EA): maybe control-plane count?
    master_flavor: str = typer.Option(None, help=_HELP["master_flavor"]),
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Update the cluster with given id"""
    if not kubernetes_version and not master_count and not master_flavor:
        console.display(
            "[bold red]No options provided to update the cluster![/bold red]"
        )
        raise typer.Exit()

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        k8sv_map = mappings.get_kubernetes_versions_mapping(client)

        region_map = mappings.get_regions_mapping(client)
        region = region_map[state.ctx.region]
        flavor_map = mappings.get_machine_spec_mapping(client, region.id)
        cluster = client.get_cluster(cluster_id)

        if kubernetes_version is not None:
            try:
                cluster.version = k8sv_map[kubernetes_version]
            except KeyError:
                raise K8sVersionNotFound(
                    version=kubernetes_version,
                    available_versions=list(k8sv_map.keys()),
                )

        if master_flavor is not None:
            try:
                cluster.control_plane.custom.machine_spec = flavor_map[master_flavor]
            except KeyError:
                raise FlavorNotFound(
                    flavor_name=master_flavor, available_flavors=list(flavor_map.keys())
                )

        if dry_run:
            console.display(
                f"[bold yellow]Dry run mode:[/bold yellow] would update cluster {cluster_id}"
            )
            console.display_json(cluster.model_dump_json())
            return

        console.display(f"Updating cluster {cluster_id} ({cluster.name}) with:")
        payload = cluster.model_dump()
        out = client.update_cluster(cluster_id, payload)
        console.display_json(json.dumps(payload, indent=2))
        console.display(f"Cluster {cluster_id} updated:")
        console.display_json(json.dumps(out, indent=2))


@app.command(help=_HELP["delete"])
def delete(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    auto_confirm: Annotated[bool, typer.Option("--confirm", "-y")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """
    Delete the cluster with given id
    """
    confirmed = auto_confirm or typer.confirm(
        f"Are you sure you want to delete cluster {cluster_id}?"
    )

    if confirmed is False:
        console.display("Aborted.")
        return

    if dry_run:
        console.display(f"Dry run: would delete cluster {cluster_id}")
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)

        client.delete_cluster(cluster_id)
        console.display(f"Cluster {cluster_id} deleted.")


@app.command(name="list", help=_HELP["list"])
def _list(
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):  # TODO: add resource mappings
    """List all clusters"""
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        region_map = mappings.get_regions_mapping(client)
        region = region_map[state.ctx.region]
        flavor_map = mappings.get_machine_spec_mapping(client, region.id)
        reversed_flavor_map = {v.id: v for v in flavor_map.values()}
        clusters = client.get_clusters()

        match format:
            case Format.TABLE:
                # TODO: add info about region and machine spec using mapping
                clusters = clusters.get(
                    "items", []
                )  # TODO: move operating on 'items' to client
                # )
                console.display_table(
                    title="Kubernetes Clusters",
                    columns=[
                        "ID",
                        "Name",
                        "Status",
                        "Flavor",
                        "Created At",
                        "Updated At",
                    ],
                    rows=[
                        [
                            cluster["id"],
                            cluster["name"],
                            cluster["status"],
                            reversed_flavor_map.get(
                                cluster["control_plane"]["custom"]["machine_spec"]["id"]
                            ).name,
                            cluster["created_at"],
                            cluster["updated_at"],
                        ]
                        for cluster in clusters
                    ],
                )
                console.display("See more details with json output format.")
            case Format.JSON:
                console.display_json(json.dumps(clusters, indent=2))


@app.command(help=_HELP["show"])
def show(cluster_id: Annotated[str, typer.Argument(help="Cluster ID")]):
    """Show cluster details"""
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        _out = client.get_cluster(cluster_id)

    console.display(f"Cluster details for {cluster_id}:")
    console.display(_out)


@app.command(help=_HELP["get_kubeconfig"])
def get_kubeconfig(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    output: str = typer.Option(
        default="kube-config.yaml",
        help="Output file for kube-config, default is 'kube-config.yaml'",
    ),
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Download kube-config.yaml"""
    if dry_run:
        console.display(f"Dry run: would download kube-config for cluster {cluster_id}")
        return

    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        _out = client.download_kubeconfig(cluster_id)

    with open(output, "w") as f:
        f.write(_out)

    console.display(f"Downloaded kube-config for cluster {cluster_id}")
    console.display(f"Kubeconfig file saved to [blue]{output}[/blue]")
    cat.save()
