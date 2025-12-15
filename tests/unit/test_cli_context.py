import json
import pytest
from mkcli.core.enums import SupportedAuthTypes
from mkcli.core.models.context import Context


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
            auth_type=SupportedAuthTypes.OPENID,
        )
    )

    catalogue.add(
        Context(
            name="dev_ctx",
            client_id="test_dev_client_id",
            realm="test_realm",
            scope="test_scope",
            region="test_region",
            identity_server_url="https://test.identity.server",
            auth_type=SupportedAuthTypes.OPENID,
        )
    )
    catalogue.current = "test_ctx"


def test_auth_command(mock_open_context, make_mkcli_call):
    """Test the auth command with default parameters"""
    result = make_mkcli_call(["auth", "--help"])
    assert result.exit_code == 0


def test_auth_context_list(mock_open_context, make_mkcli_call):
    """Test the auth context list command"""
    result = make_mkcli_call(["auth", "context", "list"])
    assert result.exit_code == 0

    # Check that the context names are in the output
    for ctx in mock_open_context.list_all():
        assert ctx.name in result.stdout

    # check if formats works fine
    result = make_mkcli_call(["auth", "context", "list", "--format", "json"])
    assert result.exit_code == 0
    # check if output is really json-serializable  # TODO(EA): move formating test to separate serializable test
    assert json.loads(result.stdout)


def test_auth_context_add(mock_open_context, make_mkcli_call):
    new_ctx_name = "new_ctx"
    result = make_mkcli_call(
        args=[
            "auth",
            "context",
            "add",
            "--realm",
            "Creodias-new",
            "--region",
            "WAW4-1",
        ],
        _input=f"{new_ctx_name}\nhttps://test.api.url\nhttps://test.identity.server\nopenid\n",  # name, api-url, identity-server, auth-type
    )

    assert result.exit_code == 0

    # Check that the new context is in the list of available contexts
    assert new_ctx_name in [ctx.name for ctx in mock_open_context.list_all()]
    assert len(mock_open_context.list_available()) == 3


def test_auth_context_switch(mock_open_context, make_mkcli_call):
    """Test switching contexts"""
    new_ctx_name = "dev_ctx"
    result = make_mkcli_call(["auth", "context", "switch", new_ctx_name])
    assert result.exit_code == 0

    # Check that the current context is now the new context
    assert mock_open_context.current == new_ctx_name
    assert mock_open_context.get(new_ctx_name).name == new_ctx_name


def test_auth_context_delete(mock_open_context, make_mkcli_call):
    new_ctx_name = "new_ctx"
    result = make_mkcli_call(
        args=["auth", "context", "delete", new_ctx_name], _input="y\n"
    )
    assert result.exit_code == 0

    # Check that the context is no longer available
    assert new_ctx_name not in mock_open_context.list_available()
    assert len(mock_open_context.list_available()) == 2


def test_auth_context_edit(mock_open_context, make_mkcli_call):
    edit_ctx = "dev_ctx"
    new_ctx_name = "dev_ctx"
    result = make_mkcli_call(
        args=["auth", "context", "edit", edit_ctx, "--name", new_ctx_name],
    )
    assert result.exit_code == 0

    # Check that the context has been updated
    updated_ctx = mock_open_context.get(new_ctx_name)
    assert updated_ctx.name == new_ctx_name
    assert updated_ctx.client_id == "test_dev_client_id"
    assert updated_ctx.scope == "test_scope"
    assert updated_ctx.identity_server_url == "https://test.identity.server"
    assert updated_ctx.realm == "test_realm"


def test_auth_context_edit_nonexistent(mock_open_context, make_mkcli_call):
    """Test editing a non-existent auth context"""
    result = make_mkcli_call(
        args=["auth", "context", "edit", "non_existent_ctx", "--name", "new_name"],
    )
    assert result.exit_code == 1
    assert "Auth context 'non_existent_ctx' not found!" in result.stdout


def test_auth_context_duplicate(mock_open_context, make_mkcli_call):
    """Test duplicating an auth context"""
    result = make_mkcli_call(
        args=["auth", "context", "duplicate", "dev_ctx", "--name", "new_dev_ctx"],
    )
    assert result.exit_code == 0

    # Check that the new context is in the list of available contexts
    assert "new_dev_ctx" in [ctx.name for ctx in mock_open_context.list_all()]
    assert len(mock_open_context.list_available()) == 3


def test_auth_context_can_edit_active(mock_open_context, make_mkcli_call):
    """Test that the active context can be edited"""
    active_ctx = mock_open_context.current
    new_name = "edited_active_ctx"
    print(f"Debug {mock_open_context.current=}, {active_ctx=}, {new_name=}")
    result = make_mkcli_call(
        args=["auth", "context", "edit", active_ctx, "--name", new_name],
    )
    assert result.exit_code == 0

    # Check that the active context has been updated
    updated_ctx = mock_open_context.get(new_name)
    assert updated_ctx.name == new_name
    assert mock_open_context.current == new_name
