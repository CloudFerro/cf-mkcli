from typer.testing import CliRunner

from mkcli.main import cli

runner = CliRunner()

HELP_MESSAGE: str = "mkcli - A CLI for managing your Kubernetes clusters"


def test_cli():
    result = runner.invoke(cli, None)
    assert result.exit_code == 0
    assert HELP_MESSAGE in result.stdout
