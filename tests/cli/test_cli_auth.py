import pytest
from mkcli.core.models.context import Context

from mkcli.settings import AuthType


@pytest.fixture(scope="module", autouse=True)
def mock_catalogue(catalogue):
    """Mock the context catalogue that would be returned by open_context_catalogue"""
    catalogue.add(
        Context(
            name="test_ctx",
            client_id="test_client_id",
            realm="test_realm",
            scope="test_scope",
            region="test_region",
            identity_server_url="https://test.identity.server",
            auth_type=AuthType.OPENID,
        )
    )


def test_auth_command(mock_open_context, make_mkcli_call):
    """Test the auth command with default parameters"""
    result = make_mkcli_call(["auth", "--help"])
    assert result.exit_code == 0


def test_auth_end(mock_open_context, make_mkcli_call):
    """Test the auth end command"""
    result = make_mkcli_call(args=["auth", "end"])
    assert result.exit_code == 0
    assert mock_open_context.current is None
