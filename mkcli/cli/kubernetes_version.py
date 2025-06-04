import typer

from mkcli.core import mappings
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console
from mkcli.core.enums import Format


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
    with open_context_catalogue() as catalogue:
        state = State(catalogue.current_context)
        client = MK8SClient(state)

        k8sv_map = mappings.get_kubernetes_versions_mapping(client)

        match format:
            case Format.TABLE:
                console.display_table(
                    title="Available Kubernetes Versions",
                    columns=["ID", "Version", "Created At", "Updated At", "Is Active"],
                    rows=[v.as_table_row() for v in k8sv_map.values()],
                )
            case Format.JSON:
                console.display(
                    {key: value.model_dump() for key, value in k8sv_map.items()}
                )
