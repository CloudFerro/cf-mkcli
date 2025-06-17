import json

import typer

from mkcli.core import mappings
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import Region
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
                table = console.ResourceTable(
                    title="Available Regions",
                    columns=Region.table_columns,
                )
                for region in region_map.values():
                    table.add_row(
                        region.as_table_row(),
                        style="dim" if not region.is_active else None,
                    )
                table.display()
            case Format.JSON:
                console.display_json(
                    json.dumps(
                        {"regions": [r.model_dump() for r in region_map.values()]},
                        indent=2,
                    )
                )
