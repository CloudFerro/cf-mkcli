import json

import typer

from mkcli.core import mappings
from mkcli.core.mk8s import MK8SClient
from mkcli.core.models import MachineSpec
from mkcli.core.session import open_context_catalogue
from mkcli.core.state import State
from mkcli.settings import APP_SETTINGS
from mkcli.utils import console
from mkcli.core.enums import Format


_HELP: dict = {
    "general": "Manage Kubernetes machine specs (flavors)",
    "list": "List all available flavors",
    "format": "Output format, either 'table' or 'json'",
}

app = typer.Typer(no_args_is_help=True, help=_HELP["general"])


@app.command(name="list", help=_HELP["list"])
def _list(
    format: Format = typer.Option(
        default=APP_SETTINGS.default_format, help=_HELP["format"]
    ),
):
    """List all available Kubernetes machine specs (flavors)"""
    with open_context_catalogue() as cat:
        state = State(cat.current_context)
        client = MK8SClient(state)  # TODO: add region name AND id to state.ctx
        region_map = mappings.get_regions_mapping(client)
        region = region_map[state.ctx.region]
        flavor_map = mappings.get_machine_spec_mapping(client, region.id)

    match format:
        case Format.TABLE:
            table = console.ResourceTable(
                title="Available Kubernetes Flavors", columns=MachineSpec.table_columns
            )
            for flavor in flavor_map.values():
                table.add_row(
                    flavor.as_table_row(), style="dim" if not flavor.is_active else None
                )
            table.display()
        case Format.JSON:
            console.display_json(
                json.dumps(
                    {key: value.as_json() for key, value in flavor_map.items()},
                    indent=2,
                )
            )
