from typing import Annotated
import json

import typer
from mkcli.core.exceptions import ResourceNotFound
from mkcli.core.models.resource_usage import ResourceUsage
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.core.mk8s import MK8SClient
from mkcli.core.enums import Format
from mkcli.utils import console
from mkcli.settings import APP_SETTINGS

app = typer.Typer(
    no_args_is_help=True, help="Show resource usage for Kubernetes clusters"
)


_HELP: dict = {
    "format": "Output format, either 'table' or 'json'",
}


@app.command(name="show", help="Show resource usage for a cluster")
def show(
    cluster_id: Annotated[
        str, typer.Argument(help="Cluster ID to show resource usage for")
    ],
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """Show resource usage statistics for a Kubernetes cluster"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        try:
            # Get resource usage data
            resource_usage: list[ResourceUsage] = client.get_resource_usage(cluster_id)
        except ResourceNotFound:
            console.display(f"[bold red]Cluster {cluster_id} not found.[/bold red]")
            raise typer.Exit(code=1)

        match format:
            case Format.TABLE:
                table = console.ResourceTable(
                    title="Resources usage", columns=ResourceUsage.table_columns
                )
                for resource in resource_usage:
                    table.add_row(
                        resource.as_table_row(),
                    )
                table.display()
                console.display("See more details with json output format.")
            case Format.JSON:
                console.display(
                    json.dumps(
                        {"count": [c.model_dump() for c in resource_usage]}, indent=2
                    )
                )
