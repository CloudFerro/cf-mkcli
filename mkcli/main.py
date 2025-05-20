import typer
from mkcli.auth import auth

cli = typer.Typer(no_args_is_help=True)
cli.add_typer(auth, name="auth", no_args_is_help=True)


if __name__ == "__main__":
    cli()
