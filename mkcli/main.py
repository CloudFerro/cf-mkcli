import typer
from mkcli.cli import auth
from mkcli.cli import cluster
from mkcli.cli import node_pool
from loguru import logger
import logging

# Suppress all logging
logger.remove()
logging.getLogger("mkcli").setLevel(logging.ERROR)

MAIN_HELP: str = "mkcli - A CLI for managing your Kubernetes clusters"

cli = typer.Typer(no_args_is_help=True, help=MAIN_HELP)
cli.add_typer(auth.app, name="auth", no_args_is_help=True)
cli.add_typer(cluster.app, name="cluster", no_args_is_help=True)
cli.add_typer(node_pool.app, name="node-pool", no_args_is_help=True)


if __name__ == "__main__":
    cli()
