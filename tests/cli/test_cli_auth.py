import pytest
from mkcli.core.models.context import Context
from unittest import mock


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
            public_key="test_key",
        )
    )


def test_auth_command(mock_open_context, make_mkcli_call):
    """Test the auth command with default parameters"""
    result = make_mkcli_call(["auth", "--help"])
    assert result.exit_code == 0


@mock.patch("mkcli.cli.auth._auth.State.renew_token")
def test_auth_init_when_context_exists(
    mock_renew_token, mock_open_context, make_mkcli_call
):
    """Test the auth init command when context already exists"""

    # Configure mock to return None or an appropriate value
    mock_renew_token.return_value = None

    result = make_mkcli_call(args=["auth", "init"], _input="\n\n")

    assert result.exit_code == 0
    # Verify the token renewal was attempted
    mock_renew_token.assert_called_once()


def test_auth_end(mock_open_context, make_mkcli_call):
    """Test the auth end command"""
    result = make_mkcli_call(args=["auth", "end"])
    assert result.exit_code == 0
    assert mock_open_context.current is None
