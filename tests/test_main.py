from typer.testing import CliRunner

from mkcli.main import cli, __version__

runner = CliRunner()

HELP_MESSAGE: str = "mkcli - A CLI for managing your Kubernetes clusters"


def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert HELP_MESSAGE in result.stdout


def test_cli_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
