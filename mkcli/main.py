import typer
from mkcli.cli import auth, cluster, node_pool, kubernetes_version, flavors, regions

from loguru import logger
import logging

state = {"verbose": False}


MAIN_HELP: str = "mkcli - A CLI for managing your Kubernetes clusters"

cli = typer.Typer(
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
    help=MAIN_HELP,
)


@cli.callback()
def main(verbose: bool = False):
    """
    Manage verbosity.
    """
    if verbose:
        return
    logger.remove()
    logging.getLogger("mkcli").setLevel(logging.ERROR)


cli.add_typer(auth.app, name="auth", no_args_is_help=True)
cli.add_typer(cluster.app, name="cluster", no_args_is_help=True)
cli.add_typer(node_pool.app, name="node-pool", no_args_is_help=True)
cli.add_typer(kubernetes_version.app, name="kubernetes-version", no_args_is_help=True)
cli.add_typer(flavors.app, name="flavors", no_args_is_help=True)
cli.add_typer(regions.app, name="regions", no_args_is_help=True)


if __name__ == "__main__":
    cli()
