import pytest
from unittest import mock

from mkcli.core.models.context import ContextCatalogue

from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from mkcli.main import cli


class MemoryStorage:
    def __init__(self):
        self.data = {}

    def save(self, _dict: dict) -> None:
        self.data = _dict

    def load(self) -> dict:
        return self.data

    def clear(self) -> None:
        self.data = {}

    def ensure_exists(self) -> None: ...

    def init_storage(self, _data: dict) -> None:
        self.data = {}


@pytest.fixture(scope="module")
def ctx_storage():
    store = MemoryStorage()
    mocked = mock.Mock(spec=MemoryStorage)
    mocked.save = mock.Mock(side_effect=store.save)
    mocked.load = mock.Mock(side_effect=store.load)
    mocked.clear = mock.Mock(side_effect=store.clear)
    mocked.ensure_exists = mock.Mock(side_effect=store.ensure_exists)
    mocked.init_storage = mock.Mock(side_effect=store.init_storage)

    try:
        yield mocked
    finally:
        store.clear()


@pytest.fixture(scope="module")
def catalogue(ctx_storage):
    return ContextCatalogue(storage=ctx_storage)


@pytest.fixture
def make_mkcli_call():
    runner = CliRunner(echo_stdin=True)

    def _make_cli_call(args, _input=None):
        return runner.invoke(cli, args, _input)

    return _make_cli_call


@pytest.fixture()
def mock_open_context(catalogue):
    """Mock the open_context_catalogue context manager"""
    cm_mock = MagicMock()
    cm_mock.__enter__.return_value = catalogue
    with patch("mkcli.cli.auth.context.open_context_catalogue", return_value=cm_mock):
        yield catalogue


@pytest.fixture
def mock_console():
    """Mock the console module used for output"""
    with patch("mkcli.cli.auth.context.console") as mock:
        mock.ResourceTable.return_value = MagicMock()
        yield mock
