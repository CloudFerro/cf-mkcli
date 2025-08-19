from typing import Annotated, Optional
import typer
from mkcli.core.exceptions import ResourceNotFound, StorageBaseError

from mkcli.cli import auth, cluster, node_pool, kubernetes_version, flavors, regions
from keycloak import KeycloakPostError
from loguru import logger
import logging

from mkcli.core.mk8s import APICallError
from mkcli.utils.console import display

__version__ = "0.2.0"  # TODO(EA): load it in pyproject toml

state = {"verbose": False}


MAIN_HELP: str = "mkcli - A CLI for managing your Kubernetes clusters"

cli = typer.Typer(
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
    help=MAIN_HELP,
)


def version_callback(value: bool):
    if value:
        print(f"cf-mkcli version: {__version__}")
        raise typer.Exit()


def verbosity_callback(
    value: bool,
):
    """
    Manage verbosity.
    """
    if value:
        logging.getLogger("mkcli").setLevel(logging.INFO)
    logger.remove()
    logging.getLogger("mkcli").setLevel(logging.ERROR)


cli.add_typer(auth.app, name="auth", no_args_is_help=True)
cli.add_typer(cluster.app, name="cluster", no_args_is_help=True)
cli.add_typer(node_pool.app, name="node-pool", no_args_is_help=True)
cli.add_typer(kubernetes_version.app, name="kubernetes-version", no_args_is_help=True)
cli.add_typer(flavors.app, name="flavors", no_args_is_help=True)
cli.add_typer(regions.app, name="regions", no_args_is_help=True)


@cli.callback()
def main(
    verbose: Annotated[
        Optional[bool], typer.Option("--verbose", callback=verbosity_callback)
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = False,
):
    pass


def run():
    try:
        cli()
    except StorageBaseError as err:
        display(f"[red]Storage Error: {err}[/red]")
    except APICallError as err:
        display(f"[red]API Call Error: {err}[/red]")
        if err.code in [401, 403]:
            display(
                "[bold red]Please check your authentication token or login credentials.[/bold red]\n"
                "You might want to mkake `mkcli auth token refresh call`."
            )

    except KeycloakPostError:
        logger.exception(
            "Keycloak Post Error occurred. Please check your auth configuration."
            "Ensure that you successfully logged in the browser during `mkcli auth token refresh`."
        )
    except ResourceNotFound as err:
        display(f"[red]Resource Not Found[/red]: {err}")
