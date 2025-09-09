import json

import typer

from mkcli.core import mappings
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console
from mkcli.core.enums import Format
from mkcli.core.models import KubernetesVersion


_HELP: dict = {
    "general": "Manage Kubernetes versions",
    "list": "List all Kubernetes versions",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(name="list", help=_HELP["list"])
def _list(
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """List all Kubernetes versions"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        k8sv_map = mappings.get_kubernetes_versions_mapping(client)

        match format:
            case Format.TABLE:
                table = console.ResourceTable(
                    title="Available Kubernetes Versions",
                    columns=KubernetesVersion.table_columns,
                )
                for row in k8sv_map.values():
                    table.add_row(
                        row.as_table_row(), style="dim" if not row.is_active else None
                    )
                table.display()
            case Format.JSON:
                console.display_json(
                    json.dumps(
                        {key: value.as_json() for key, value in k8sv_map.items()}
                    )
                )
