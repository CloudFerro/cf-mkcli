import pytest
import os
from unittest import mock
from typing import Optional
from mkcli.core.models.context import ContextCatalogue
import re
import hashlib
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from mkcli.main import cli
import random
import string
from pytest_dependency import DependencyManager
from tests.src.bdd_logger import BDDLogger
from tests.src.log import log

DependencyManager.ScopeCls["module"] = DependencyManager.ScopeCls["session"]

# Set wider terminal width for consistent table output in CI/CD
os.environ["COLUMNS"] = "120"
os.environ["LINES"] = "30"

ECHO: bool = True


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


@pytest.fixture(scope="session")
def api_token_prod():
    """Fixture to provide access to API_TOKEN_PROD environment variable"""
    return os.getenv("API_TOKEN_PROD")


@pytest.fixture(scope="session")
def created_cluster_id():
    """Fixture to store cluster ID created in test_cluster_create for deletion testing."""
    cluster_data = {"id": None, "name": None}
    yield cluster_data


@pytest.fixture(scope="session")
def created_node_pool_id():
    """Fixture to store node pool ID created in test_node_pool_create for deletion testing."""
    node_pool_data = {"id": None, "name": None, "cluster_id": None}
    yield node_pool_data


def generate_cluster_name() -> str:
    generated_name = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    return f"mkcli-test-cluster-{generated_name}"


def mask_api_tokens(text: str) -> str:
    """
    Mask API tokens in text by replacing them with hashed versions.
    Pattern to detect API token (64 hex characters)

    Args:
        text: Text that may contain API tokens

    Returns:
        Text with API tokens replaced by [TOKEN:hash] format
    """
    token_pattern = re.compile(r"[a-f0-9]{64}")

    def replace_token(match):
        token = match.group()
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:8]
        return f"[TOKEN:{token_hash}]"

    return token_pattern.sub(replace_token, text)


def run_mkcli_cmd(
    args: list[str],
    input: Optional[str] = None,
    show_output: bool = False,
    assert_success: bool = False,
):
    """
    Run mkcli command with proper Typer CliRunner approach.

    Args:
        args: Command line arguments
        input: Optional input to pass to the command
        show_output: Whether to print the output
        assert_success: Whether to assert that exit code is 0

    Returns:
        Result object from CliRunner
    """
    masked_command = mask_api_tokens(" ".join(args))
    log.info("Calling mkcli command", command=masked_command)

    runner = CliRunner(echo_stdin=ECHO)

    result = runner.invoke(cli, args, input=input)

    log.info("Command completed", exit_code=result.exit_code)
    if show_output:
        masked_output = mask_api_tokens(result.output)
        print(f"Command output: {masked_output}")

    if assert_success:
        assert result.exit_code == 0, (
            f"Command failed with exit code {result.exit_code}: {result.exception}"
        )

    return result


@pytest.fixture
def bdd(request):
    """Fixture that provides a BDD logger instance for the current test."""
    test_name = request.node.name
    logger = BDDLogger(test_name)
    log.info(f"🚀 Starting test: {test_name}")
    yield logger
    log.info(f"🏁 End of test: {test_name}")
