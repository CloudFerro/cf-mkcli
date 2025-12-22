import json

import typer
from typing_extensions import Annotated


from mkcli.core.enums import Format
from mkcli.core.exceptions import FlavorNotFound, K8sVersionNotFound
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import ClusterPayload, Cluster
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.utils import console
from mkcli.settings import DefaultClusterSettings, APP_SETTINGS
from mkcli.core import mappings


default_cluster = DefaultClusterSettings()

_HELP: dict = {
    "general": "Manage Kubernetes clusters",
    "create": "Create a new k8s cluster",
    "upgrade": "Upgrade the cluster with given id",
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
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """Create a new k8s cluster"""
    if from_json is not None:
        console.display(
            "Using provided cluster payload from JSON, ignoring other options."
        )
        new_cluster = from_json
    else:
        with open_context_catalogue() as cat:
            ctx = cat.current_context
            client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
            k8sv_map = mappings.get_kubernetes_versions_mapping(client)
            region_map = mappings.get_regions_mapping(client)
            region = region_map[ctx.region]
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

    if dry_run:
        console.display(
            f"[bold yellow]Dry run mode:[/bold yellow] would create cluster with data: {new_cluster}"
        )
        return

    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        _out = client.create_cluster(cluster_data=new_cluster.dict())

    match format:
        case Format.TABLE:
            console.display(f"Creating new cluster: {new_cluster}")
        case Format.JSON:
            console.display(json.dumps(_out, indent=2))


@app.command(help=_HELP["upgrade"])
def upgrade(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    kubernetes_version: Annotated[
        str, typer.Argument(help=_HELP["kubernetes_version"])
    ],
    dry_run: Annotated[bool, typer.Option("--dry-run", help=_HELP["dry_run"])] = False,
):
    """Upgrade the cluster with given id"""

    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        k8sv_map = mappings.get_kubernetes_versions_mapping(client)

        cluster = client.get_cluster(cluster_id)

        if kubernetes_version is not None:
            try:
                cluster.version = k8sv_map[kubernetes_version]
            except KeyError:
                raise K8sVersionNotFound(
                    version=kubernetes_version,
                    available_versions=list(k8sv_map.keys()),
                )
        if dry_run:
            console.display(
                f"[bold yellow]Dry run mode:[/bold yellow] would update cluster {cluster_id}"
            )
            console.display_json(cluster.model_dump_json())
            return

        payload = cluster.model_dump()
        client.update_cluster(cluster_id, payload)
        console.display(
            f"Updating cluster {cluster_id} [bold cyan]({cluster.name})[/bold cyan] to k8s version {kubernetes_version}"
        )


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
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        client.delete_cluster(cluster_id)
        console.display(f"Cluster {cluster_id} deleted.")


@app.command(name="list", help=_HELP["list"])
def _list(
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """List all clusters"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        clusters = client.get_clusters(region=ctx.region)

        match format:
            case Format.TABLE:
                table = console.ResourceTable(
                    title="Kubernetes Clusters", columns=Cluster.table_columns
                )
                for cluster in clusters:
                    table.add_row(
                        cluster.as_table_row(),
                    )
                table.display()
                console.display("See more details with json output format.")
            case Format.JSON:
                console.display(
                    json.dumps(
                        {"clusters": [c.model_dump() for c in clusters]}, indent=2
                    )
                )


@app.command(help=_HELP["show"])
def show(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID")],
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """Show cluster details"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        _out = client.get_cluster(cluster_id)

    match format:
        case Format.TABLE:
            console.display(f"Cluster details for {cluster_id}:")
            console.display(_out)
        case Format.JSON:
            console.display(json.dumps(_out.model_dump()))


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
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        _out = client.download_kubeconfig(cluster_id)

    with open(output, "w") as f:
        f.write(_out)

    console.display(f"Downloaded kube-config for cluster {cluster_id}")
    console.display(f"Kubeconfig file saved to [blue]{output}[/blue]")
    cat.save()
