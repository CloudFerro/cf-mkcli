from rich import get_console
import typer
from mkcli.core.mk8s import MK8SClient
from mkcli.core.session import get_auth_adapter, open_context_catalogue
from mkcli.utils.layout import Dashboard


app = typer.Typer(help="Live dashboard presenting clusters")


@app.callback(
    invoke_without_command=True
)  # TODO(EAdamska): TO BE REMOVED, just a hack for beta phase of this feature
def main(ctx: typer.Context):
    """Watch cluster status until it's running"""
    if ctx.invoked_subcommand is None:
        dashboard()


def dashboard():
    """Start the dashboard"""
    with open_context_catalogue() as cat:
        ctx = cat.current_context
        client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

        console = get_console()
        dashboard_instance = Dashboard(
            console=console,
            func_clusters_sync=lambda: client.get_clusters(),
            func_node_pools_sync=lambda x: client.list_node_pools(x),
        )
        dashboard_instance.go_live()
