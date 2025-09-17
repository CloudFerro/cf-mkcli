from typing import Annotated, Optional
import json

import typer
from mkcli.core.exceptions import ResourceNotFound
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.core.mk8s import MK8SClient
from mkcli.utils import console
from mkcli.utils.names import generate as generate_name

app = typer.Typer(no_args_is_help=True, help="Manage Kubernetes cluster backups")


@app.command(name="create", help="Create a new backup for a cluster")
def create(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID to create backup for")],
    name: Annotated[
        Optional[str], typer.Option(help="Backup name, if None, generate with petname")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option(help="Description for the backup")
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If True, do not perform any actions, just print the payload"
        ),
    ] = False,
):
    """Create a new backup for a Kubernetes cluster"""
    # Generate name if not provided
    backup_name = name or generate_name()

    # Create payload
    payload = {
        "name": backup_name,
    }

    if description:
        payload["description"] = description

    if dry_run:
        console.display(f"[bold]Backup creation payload[/bold]:\n{payload}")
        return

    # Create backup
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)
        result = client.create_backup(cluster_id, payload)

    console.display(
        f"[bold green]Backup creation initiated for cluster {cluster_id}.[/bold green]"
    )
    console.display(f"Backup ID: {result['id']}")
    console.display(f"Backup Name: {result['name']}")
    console.display(f"Status: {result['status']}")


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


@app.command(name="delete", help="Delete a backup")
def delete(
    cluster_id: Annotated[str, typer.Argument(help="Cluster ID to operate on")],
    backup_id: Annotated[str, typer.Argument(help="Backup ID to delete")],
    confirm: Annotated[
        bool, typer.Option("--confirm", "-y", help="Confirm deletion without prompting")
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If True, do not perform any actions, just print the payload"
        ),
    ] = False,
):
    """Delete a backup"""
    if not confirm:
        confirmed = typer.confirm(
            f"Are you sure you want to delete backup {backup_id}?"
        )
        if not confirmed:
            console.display("[yellow]Deletion canceled.[/yellow]")
            raise typer.Exit()

    if dry_run:
        console.display(
            f"[bold]Would delete backup {backup_id} from cluster {cluster_id}[/bold]"
        )
        return

    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        try:
            client.delete_backup(cluster_id, backup_id)
            console.display(
                f"[bold green]Backup {backup_id} deleted successfully.[/bold green]"
            )
        except ResourceNotFound:
            console.display(
                f"[bold red]Backup {backup_id} not found for cluster {cluster_id}.[/bold red]"
            )
            raise typer.Exit(code=1)
