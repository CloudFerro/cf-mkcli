from tests.conftest import run_mkcli_cmd
import pytest


@pytest.mark.dependency(scope="session")
@pytest.mark.order(1)
def test_auth_session_init(bdd: classmethod, api_token_prod):
    """
    Fixture that initializes mkcli auth session at the start of pytest.
    This ensures all tests have proper authentication context.
    """
    if not api_token_prod:
        pytest.fail("API_TOKEN_PROD environment variable not set")

    with bdd.given("Preparing to initialize authentication session for test suite"):
        result = run_mkcli_cmd(
            [
                "auth",
                "init",
                "--realm",
                "Creodias-new",
                "--region",
                "WAW4-1",
                "--api-url",
                "https://managed-kubernetes.creodias.eu/api/v1",
                "--auth-type",
                "api_key",
            ],
            input=api_token_prod,
            show_output=True,
            assert_success=True,
        )

        output_lower = result.output.lower()

    with bdd.then("Authentication session should be initialized successfully"):
        assert "initialized a new auth session in `default context`" in output_lower, (
            "Auth session initialization message not found"
        )
        assert "initialized a new auth session in `default context`" in output_lower, (
            "Auth session initialization message not found"
        )


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_session_init"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_session_init"],
    scope="session",
)
def test_auth_verify_session_initialized(
    bdd: classmethod,
):
    """Verify that the auth session has been initialized by the session fixture."""
    with bdd.given("Auth session is initialized by session fixture"):
        result = run_mkcli_cmd(
            ["auth", "context", "show"],
            show_output=True,
            assert_success=True,
        )

        output_lower = result.output.lower()

    with bdd.then("Auth context should be properly configured"):
        assert "default" in output_lower, "Expected 'default' context not found"
        assert "managed-kubernetes" in output_lower, (
            "Expected 'managed-kubernetes' client ID not found"
        )
        assert "creodias-new" in output_lower, "Expected 'Creodias-new' realm not found"
        assert "waw4-1" in output_lower, "Expected 'WAW4-1' region not found"
        assert "authtype.api_key" in output_lower, (
            "Expected 'api_key' auth type not found"
        )

        assert result.exit_code == 0


@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_auth_token_show(
    bdd: classmethod, command: list[str] = ["auth", "token", "show"]
):
    """Test that 'mkcli auth token show' command executes and returns None because authorization is API token."""
    with bdd.given("Show auth token"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth token show output should indicate no token is present"):
        assert "none" in result.output.lower(), "Expected 'None' in token show output"

        assert result.exit_code == 0


@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_auth_token_clear(
    bdd: classmethod, command: list[str] = ["auth", "token", "clear"]
):
    """Test that 'mkcli auth token clear' command executes and returns nothing."""
    with bdd.given("Clear auth token"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth token clear output should be empty"):
        output_stripped = result.output.strip()
        assert output_stripped == "", (
            f"Expected empty output, but got: '{result.output}'"
        )

    assert result.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
)
@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_auth_key_show(
    bdd: classmethod, api_token_prod: str, command: list[str] = ["auth", "key", "show"]
):
    """Test that 'mkcli auth key show' command executes and returns the API token."""
    with bdd.given("Show auth key"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth key show output should contain the API token"):
        assert api_token_prod in result.output, (
            "Expected API token in output, but token was not found"
        )

        assert result.exit_code == 0


@pytest.mark.order(after="tests/integration/test_auth_api_token.py::test_auth_key_show")
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_key_show"],
    scope="session",
)
def test_auth_key_clear(
    bdd: classmethod, api_token_prod: str, command: list[str] = ["auth", "key", "clear"]
):
    """Test that 'mkcli auth key clear' command executes and returns nothing."""
    with bdd.given("Clear auth key"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth key clear output should be empty"):
        assert api_token_prod not in result.output, (
            f"Expected API token '{api_token_prod}' to be cleared from output, but got: '{result.output}'"
        )

        assert result.exit_code == 0


@pytest.mark.order(after="tests/integration/test_auth_api_token.py::test_auth_key_show")
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_key_show"],
    scope="session",
)
def test_auth_key_set(
    bdd: classmethod,
    api_token_prod: str,
    base_command: list[str] = ["auth", "key", "set"],
):
    """Test that 'mkcli auth key set' command executes and returns the API token."""
    with bdd.given("Set auth key"):
        command = base_command + [api_token_prod]
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.when("Auth key set output should indicate success"):
        assert "API key set successfully." in result.output, (
            "Expected API key set success message in output"
        )

    assert result.exit_code == 0

    with bdd.then("Show auth key should return the set API token"):
        result_token_show = run_mkcli_cmd(
            ["auth", "key", "show"], assert_success=True, show_output=True
        )

        assert api_token_prod in result_token_show.output, (
            "Expected API token in output after setting, but token was not found"
        )

        assert result_token_show.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
)
@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_auth_context_show(
    bdd: classmethod, command: list[str] = ["auth", "context", "show"]
):
    """Test that 'mkcli auth context show' command executes successfully."""
    with bdd.given("Show auth context"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth context show output should contain expected fields"):
        output_lower = result.output.lower()

        assert "context" in output_lower
        assert "default" in output_lower
        assert "managed-kubernetes" in output_lower
        assert "creodias-new" in output_lower
        assert "waw4-1" in output_lower
        assert "https://managed-kubernetes.creodias.eu" in output_lower
        assert "authtype.api_key" in output_lower

        assert result.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
)
@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_authorized_auth_context_list(
    bdd: classmethod, command: list[str] = ["auth", "context", "list"]
):
    """Test that 'mkcli auth context list' command executes successfully."""
    with bdd.given("List auth contexts"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

    with bdd.then("Auth context list output should contain expected fields"):
        output_lower = result.output.lower()

        assert "context" in output_lower
        assert "default" in output_lower
        assert "managed-kubernetes" in output_lower
        assert "creodias-new" in output_lower
        assert "waw4-1" in output_lower
        assert "https://managed-kubernetes.creodias.eu" in output_lower
        assert "authtype.api_key" in output_lower

        assert result.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_authorized_auth_context_list"
)
@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_authorized_auth_context_list"
    ],
    scope="session",
)
def test_auth_context_add(
    bdd: classmethod,
    context_name: str = "test_ctx",
    client_id: str = "managed-kubernetes",
    realm: str = "Creodias-new",
    region: str = "WAW4-1",
    auth_type: str = "api_key",
    identity_server: str = "https://identity.cloudferro.com/auth/",
    mk8s_api_url: str = "https://managed-kubernetes.creodias.eu/api/v1",
):
    """Test that 'mkcli auth context add' command executes successfully."""
    with bdd.given("Add new auth context"):
        result = run_mkcli_cmd(
            [
                "auth",
                "context",
                "add",
                "--name",
                context_name,
                "--api-url",
                mk8s_api_url,
                "--realm",
                realm,
                "--region",
                region,
                "--auth-type",
                auth_type,
                "--identity-server",
                identity_server,
            ],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.when("New auth context should be added successfully"):
        assert "creating a new auth context" in output_lower, (
            "Context creation message not found"
        )
        assert f'"name": "{context_name}"' in output_lower, (
            "Context name not found in JSON output"
        )
        assert f'"client_id": "{client_id}"' in output_lower, (
            "Client ID not found in JSON output"
        )
        assert f'"realm": "{realm.lower()}"' in output_lower, (
            "Realm not found in JSON output"
        )
        assert f'"auth_type": "{auth_type}"' in output_lower, (
            "Auth type not found in JSON output"
        )

        assert result.exit_code == 0

    with bdd.then("The new context should appear in the context list"):
        result_list = run_mkcli_cmd(
            ["auth", "context", "list"], assert_success=True, show_output=True
        )

    with bdd.then("The new context should appear in the context list"):
        output_list_lower = result_list.output.lower()
        assert context_name in output_list_lower, (
            f"New context '{context_name}' not found in context list"
        )

        assert result.exit_code == 0

        output_list_lower = result_list.output.lower()
        assert "test_ctx" in output_list_lower, (
            "New context 'test_ctx' not found in context list"
        )

        assert result_list.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_context_add"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_context_add"],
    scope="session",
)
def test_auth_context_switch(
    bdd: classmethod,
    context_name: str = "test_ctx",
):
    """Test that 'mkcli auth context switch' command executes successfully."""
    with bdd.given("Switch auth context"):
        result = run_mkcli_cmd(
            [
                "auth",
                "context",
                "switch",
                context_name,
            ],
            assert_success=True,
            show_output=True,
        )

    with bdd.when("Auth context should be switched successfully"):
        output_lower = result.output.lower()

        assert f"set auth context '{context_name}' as current!" in output_lower, (
            f"Context switch success message for '{context_name}' not found"
        )

        assert result.exit_code == 0

    with bdd.then("The current context should be the switched context"):
        result_show = run_mkcli_cmd(
            ["auth", "context", "show"], assert_success=True, show_output=True
        )

        output_show_lower = result_show.output.lower()
        assert context_name in output_show_lower, (
            f"Current context is not '{context_name}' after switch"
        )

        assert "current authorization context" in output_show_lower, (
            "Expected 'Current Authorization Context' table header not found"
        )

        assert result_show.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_context_add"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_context_add"],
    scope="session",
)
def test_auth_context_duplicate(
    bdd: classmethod,
    context_name: str = "test_ctx",
    new_context_name: str = "test_ctx_copy",
):
    """Test that 'mkcli auth context add' command fails when adding a duplicate context."""
    with bdd.given("A duplicate context"):
        result = run_mkcli_cmd(
            [
                "auth",
                "context",
                "duplicate",
                context_name,
                "--name",
                new_context_name,
            ],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then("The context should be duplicated successfully"):
        assert (
            f"duplicated auth context '{context_name}' into {new_context_name}!"
            in output_lower
        ), "Context duplication message not found"


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_context_duplicate"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_context_duplicate"],
    scope="session",
)
def test_auth_context_delete(
    bdd: classmethod,
    context_name: str = "test_ctx_copy",
):
    """Test that 'mkcli auth context delete' command executes successfully."""
    with bdd.given("Delete auth context"):
        result = run_mkcli_cmd(
            ["auth", "context", "delete", context_name, "--confirm", "-y"],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.when("The context should be deleted successfully"):
        assert f"auth context '{context_name}' deleted successfully!" in output_lower, (
            f"Context deletion message for '{context_name}' not found"
        )

        assert result.exit_code == 0

    with bdd.then("The deleted context should not appear in the context list"):
        result_list = run_mkcli_cmd(
            ["auth", "context", "list"], assert_success=True, show_output=True
        )

        output_list_lower = result_list.output.lower()
        assert context_name not in output_list_lower, (
            f"Deleted context '{context_name}' still found in context list"
        )

        assert result.exit_code == 0


@pytest.mark.order(
    after="tests/integration/test_auth_api_token.py::test_auth_context_delete"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_context_delete"],
    scope="session",
)
def test_auth_context_edit(
    bdd: classmethod,
    context_name: str = "test_ctx",
    new_context_name: str = "edited_ctx_name",
    client_id: str = "managed-kubernetes",
    realm: str = "creodias-new",
    scope: str = "email profile openid",
    region: str = "waw4-1",
    identity_server_url: str = "https://identity.cloudferro.com/auth/",
    mk8s_api_url: str = "https://managed-kubernetes.creodias.eu/api/v1",
    auth_type: str = "<authtype.api_key: 'api_key'>",
):
    """Test that 'mkcli auth context edit' command executes successfully."""
    with bdd.given("Edit auth context"):
        result = run_mkcli_cmd(
            [
                "auth",
                "context",
                "edit",
                context_name,
                "--name",
                new_context_name,
            ],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.when("The context should be edited successfully"):
        assert f"edited auth context '{context_name}'" in output_lower, (
            f"Context edit message for '{context_name}' not found"
        )

        assert f"'name': '{new_context_name}'" in output_lower, (
            f"New context name '{new_context_name}' not found in JSON output"
        )

    with bdd.then("The edited fields should be reflected in the context details"):
        expected_fields = [
            f"'client_id': '{client_id}'",
            f"'realm': '{realm.lower()}'",
            f"'scope': '{scope}'",
            f"'region': '{region.lower()}'",
            f"'identity_server_url': '{identity_server_url}'",
            f"'mk8s_api_url': '{mk8s_api_url}'",
            f"'auth_type': {auth_type.lower()}",
        ]

        for field in expected_fields:
            assert field in output_lower, (
                f"Expected field '{field}' not found in JSON output"
            )

        assert result.exit_code == 0


@pytest.mark.order(-1)
@pytest.mark.dependency(
    depends=["tests/integration/test_auth_api_token.py::test_auth_context_edit"],
    scope="session",
)
def test_auth_end(bdd: classmethod, command: list[str] = ["auth", "end"]):
    """Test that 'mkcli auth end' command executes successfully and clears all auth sessions."""
    with bdd.given("End all auth sessions"):
        result = run_mkcli_cmd(command, assert_success=True, show_output=True)

        output_lower = result.output.lower()

    with bdd.when("All auth sessions should be ended and cleared"):
        assert "all saved auth sessions ended and cleared." in output_lower, (
            "Expected auth end success message not found"
        )

        assert result.exit_code == 0

    with bdd.then("The auth context list should be empty"):
        result_list = run_mkcli_cmd(
            ["auth", "context", "list"], assert_success=True, show_output=True
        )

        output_list_lower = result_list.output.lower()

        assert "available auth contexts" in output_list_lower, (
            "Expected 'Available Auth Contexts' table header not found"
        )

    with bdd.then("The auth context list should have only headers"):
        expected_headers = [
            "name",
            "client id",
            "realm",
            "region",
            "api url",
            "auth type",
        ]
        for header in expected_headers:
            assert header in output_list_lower, (
                f"Expected column header '{header}' not found in empty context list"
            )

        assert "default" not in output_list_lower, (
            "Expected no 'default' context after auth end"
        )

        assert "managed-kubernetes" not in output_list_lower, (
            "Expected no context data after auth end"
        )

        assert result_list.exit_code == 0
