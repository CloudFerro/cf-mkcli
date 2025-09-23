from typing import Annotated, Optional
import typer
from mkcli.core.exceptions import AuthorizationError, ResourceNotFound, StorageBaseError

from mkcli.cli import (
    auth,
    cluster,
    node_pool,
    kubernetes_version,
    flavors,
    regions,
    backup,
    resource,
)
from keycloak import KeycloakPostError
from loguru import logger
import logging

from mkcli.core.mk8s import APICallError
from mkcli.core import exceptions as exc
from mkcli.utils.console import display
from mkcli._version import __version__
from mkcli.settings import APP_SETTINGS

state = {"verbose": False}


MAIN_HELP: str = "mkcli - A CLI for managing your Kubernetes clusters"

cli = typer.Typer(
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
    help=MAIN_HELP,
)


def version_callback(value: bool):
    if value:
        print(f"mkcli version: {__version__}")
        raise typer.Exit()


def verbosity_callback(
    value: bool,
):
    """
    Manage verbosity.
    """
    if value:
        state["verbose"] = True
        logging.getLogger("mkcli").setLevel(logging.INFO)
    logger.remove()
    logging.getLogger("mkcli").setLevel(logging.ERROR)


cli.add_typer(auth.app, name="auth", no_args_is_help=True)
cli.add_typer(cluster.app, name="cluster", no_args_is_help=True)
cli.add_typer(node_pool.app, name="node-pool", no_args_is_help=True)
cli.add_typer(kubernetes_version.app, name="kubernetes-version", no_args_is_help=True)
cli.add_typer(flavors.app, name="flavors", no_args_is_help=True)
cli.add_typer(regions.app, name="regions", no_args_is_help=True)

if (
    APP_SETTINGS.beta_feature_flag
):  # export MKCLI_BETA_FEATURE_FLAG=True if you want to check it
    cli.add_typer(backup.app, name="backup", no_args_is_help=True)
    cli.add_typer(resource.app, name="resource-usage", no_args_is_help=True)


@cli.callback()
def main(
    verbose: Annotated[
        Optional[bool],
        typer.Option("--verbose", callback=verbosity_callback, is_flag=True),
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
    except AuthorizationError as err:
        display(f"[red]Authorization Error: {err}.[/red]")
        exit(1)
    except StorageBaseError as err:
        display(f"[red]Storage Error: {err}[/red]")
        exit(1)
    except APICallError as err:
        display(f"[red]API Call Error: {err}[/red]")
        if err.code in [401, 403]:
            display(
                "[bold red]Please check your authentication token or login credentials.[/bold red]\n"
                "You might want to make `mkcli auth token refresh call` if you authorize by OpenID "
                "or check if your API key is correct."
            )
    except exc.NoActiveSession as err:
        display(f"[red]No Active Session.{err}[/red]")
        display(
            "Please initialize an auth session using:\n"
            ">> [green]`mkcli auth init`[/green] or check if you have a valid auth context set."
        )
    except KeycloakPostError:
        logger.exception(
            "Keycloak Post Error occurred. Please check your auth configuration."
            "Ensure that you successfully logged in the browser during `mkcli auth token refresh`."
        )
    except ResourceNotFound as err:
        display(f"[red]Resource Not Found[/red]: {err}")

    except Exception as err:
        if state["verbose"]:
            display("An unexpected error occurred.")
            raise err
        else:
            display(f"[red]An unexpected error occurred - {err}[/red]")
            exit(1)
