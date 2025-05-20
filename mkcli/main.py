import typer
from mkcli.cli import auth
from mkcli.cli import cluster
from mkcli.cli import node_pool

cli = typer.Typer(no_args_is_help=True)
cli.add_typer(auth.app, name="auth", no_args_is_help=True)
cli.add_typer(cluster.app, name="cluster", no_args_is_help=True)
cli.add_typer(node_pool.app, name="node-pool", no_args_is_help=True)


if __name__ == "__main__":
    cli()
