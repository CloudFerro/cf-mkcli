from unittest import mock
import pytest
from typer.testing import CliRunner
from mkcli.core.models.context import Context
from mkcli.core.enums import AuthType, SupportedRealms, SupportedRegions
from mkcli.main import cli


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


@mock.patch("typer.prompt", return_value="")
def test_auth_init_no_api_key(mock_prompt, mock_open_context, make_mkcli_call):
    """Test the auth init command without providing an API key"""
    runner = CliRunner(echo_stdin=True, catch_exceptions=False)
    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            "Creodias-new",
            "--region",
            "WAW4-1",
            "--auth-type",
            "api_key",
        ],
    )

    # The command should succeed - empty API key is allowed during creation
    # (will be validated later when making API calls)
    assert result.exit_code == 0
    # Verify that typer.prompt was called to ask for API key
    mock_prompt.assert_called_once_with(
        "Enter your API key", hide_input=False, default=""
    )


def test_auth_init_valid_enum_values(mock_open_context):
    """Test auth init with valid enum values"""
    runner = CliRunner(echo_stdin=True, catch_exceptions=False)

    # Test with valid realm, region, and auth type
    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            "Creodias-new",
            "--region",
            "WAW4-1",
            "--auth-type",
            "api_key",
        ],
        input="test-api-key\n",
    )

    assert result.exit_code == 0


def test_auth_init_invalid_realm(mock_open_context):
    """Test auth init with invalid realm value"""
    runner = CliRunner(catch_exceptions=False)

    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            "invalid-realm",
            "--region",
            "WAW4-1",
            "--auth-type",
            "api_key",
        ],
    )

    # Should fail with validation error
    assert result.exit_code != 0
    assert (
        "Invalid value for '--realm'" in result.output
        or "invalid-realm" in result.output
    )


def test_auth_init_invalid_region(mock_open_context):
    """Test auth init with invalid region value"""
    runner = CliRunner(catch_exceptions=False)

    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            "Creodias-new",
            "--region",
            "invalid-region",
            "--auth-type",
            "api_key",
        ],
    )

    # Should fail with validation error
    assert result.exit_code != 0
    assert (
        "Invalid value for '--region'" in result.output
        or "invalid-region" in result.output
    )


def test_auth_init_invalid_auth_type(mock_open_context):
    """Test auth init with invalid auth type value"""
    runner = CliRunner(catch_exceptions=False)

    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            "Creodias-new",
            "--region",
            "WAW4-1",
            "--auth-type",
            "invalid-auth",
        ],
    )

    # Should fail with validation error
    assert result.exit_code != 0
    assert (
        "Invalid value for '--auth-type'" in result.output
        or "invalid-auth" in result.output
    )


def test_auth_init_prompt_validation(mock_open_context):
    """Test auth init with invalid values in prompts"""
    runner = CliRunner(echo_stdin=True, catch_exceptions=False)

    # Test invalid realm in prompt - user should be re-prompted
    # Note: Typer automatically handles this validation and re-prompts
    result = runner.invoke(
        cli,
        ["auth", "init"],
        input="invalid-realm\nCreodias-new\ninvalid-region\nWAW4-1\ninvalid-auth\napi_key\ntest-key\n",
    )

    # Should eventually succeed after valid inputs are provided
    assert result.exit_code == 0


@pytest.mark.parametrize("realm", [r.value for r in SupportedRealms])
@pytest.mark.parametrize("region", [r.value for r in SupportedRegions])
@pytest.mark.parametrize("auth_type", [a.value for a in AuthType])
def test_auth_init_all_valid_combinations(mock_open_context, realm, region, auth_type):
    """Test auth init with all valid combinations of enum values"""
    runner = CliRunner(echo_stdin=True, catch_exceptions=False)

    input_data = "test-api-key\n" if auth_type == "api_key" else ""

    result = runner.invoke(
        cli,
        [
            "auth",
            "init",
            "--realm",
            realm,
            "--region",
            region,
            "--auth-type",
            auth_type,
        ],
        input=input_data,
    )

    assert result.exit_code == 0
