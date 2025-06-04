import typer

from mkcli.core import mappings
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console
from mkcli.core.enums import Format


_HELP: dict = {
    "general": "Manage regions",
    "list": "List all available regions",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(name="list", help=_HELP["list"])
def _list(
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """List all available regions"""
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)
        region_map = mappings.get_regions_mapping(client)

        match format:
            case Format.TABLE:
                console.display_table(
                    title="Available Regions",
                    columns=["ID", "Name", "Created At", "Updated At", "Is Active"],
                    rows=[v.as_table_row() for v in region_map.values()],
                )
            case Format.JSON:
                console.display(
                    {key: value.model_dump() for key, value in region_map.items()}
                )
