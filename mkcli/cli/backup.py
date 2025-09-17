from typing import Annotated, Optional
import json

import typer
from mkcli.core.exceptions import ResourceNotFound
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.core.mk8s import MK8SClient
from mkcli.utils import console

app = typer.Typer(no_args_is_help=True, help="Manage Kubernetes cluster backups")


# {enabled: true, ttl: "2592000s", schedule: "* * * * */5", should_backup_volumes: false}
@app.command(name="create", help="Create a new backup for a cluster")
def create(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID to create backup for")],
    enabled: Annotated[
        Optional[bool], typer.Option(help="Enable or disable the backup schedule")
    ] = True,
    ttl: Annotated[
        Optional[str],
        typer.Option(help="Time to live for the backup, e.g. '2592000s' (30 days)"),
    ] = "30d",
    schedule: Annotated[
        Optional[str],
        typer.Option(help="Cron schedule for automated backups, e.g. '* * * */1 *'"),
    ] = "* * * */1 *",
    backup_volumes: Annotated[
        Optional[bool], typer.Option(help="Whether to backup volumes")
    ] = False,
):
    """Create a new backup for a Kubernetes cluster"""
    payload = {}

    if enabled is not None:
        payload["enabled"] = enabled

    if ttl:
        payload["ttl"] = ttl

    if schedule:
        payload["schedule"] = schedule

    if backup_volumes is not None:
        payload["should_backup_volumes"] = backup_volumes

    # Create backup
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        result = client.create_backup(cluster_id, payload)

    console.display(
        f"[bold green]Backup creation initiated for cluster {cluster_id}.[/bold green]"
    )
    console.display(result)


@app.command(name="list", help="List all backups for a cluster")
def list_backups(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID to operate on")],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Output format, either 'table' or 'json'",
            show_default=True,
        ),
    ] = "table",
):
    """List all backups for a Kubernetes cluster"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        try:
            backups = client.list_backups(cluster_id)
        except ResourceNotFound:
            console.display(f"[bold red]Cluster {cluster_id} not found.[/bold red]")
            raise typer.Exit(code=1)

        if format == "json":
            console.display_json(
                json.dumps([backup.model_dump() for backup in backups])
            )
        else:
            # Create a table to display backups
            columns = backups[0].table_columns if backups else ["No backups found"]
            rows = [backup.as_table_row() for backup in backups] if backups else []
            console.display_table(
                columns=columns, rows=rows, title=f"Backups for cluster {cluster_id}"
            )


@app.command(name="show", help="Show backup details")
def show(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID to operate on")],
    backup_id: Annotated[str, typer.Argument(help="Backup ID to show")],
):
    """Show details for a specific backup"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        try:
            backup = client.get_backup(cluster_id, backup_id)
        except ResourceNotFound:
            console.display(
                f"[bold red]Backup {backup_id} not found for cluster {cluster_id}.[/bold red]"
            )
            raise typer.Exit(code=1)

        console.display("[bold]Backup details:[/bold]")
        console.display(f"ID: {backup.id}")
        console.display(f"Name: {backup.name}")
        console.display(f"Description: {backup.description or '-'}")
        console.display(f"Status: {backup.status}")
        console.display(
            f"Size: {backup.size / (1024 * 1024 * 1024):.2f} GB"
            if backup.size
            else "Size: N/A"
        )
        console.display(f"Created: {backup.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        console.display(f"Updated: {backup.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        console.display(f"Cluster ID: {backup.cluster_id}")
