from unittest import mock
import pytest
import json
from mkcli.core.models.context import Context
from mkcli.core.models.resource_usage import ResourceUsage
from mkcli.core.enums import SupportedAuthTypes


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
            mk8s_api_url="https://test.api.url",
        )
    )
    catalogue.switch("test_ctx")


@pytest.fixture
def mock_resource_client():
    """Mock the MK8SClient used by the resource-usage command"""
    with mock.patch("mkcli.cli.resource.MK8SClient") as mock_client:
        # Set up the mock to return a list of ResourceUsage objects
        mock_instance = mock_client.return_value

        # Sample resource count data
        sample_resources = [
            ResourceUsage(name="pods", usage_count=32),
            ResourceUsage(name="services", usage_count=4),
            ResourceUsage(name="deployments.apps", usage_count=5),
        ]

        mock_instance.get_resource_usage.return_value = sample_resources
        yield mock_instance


def test_resource_usage_show_help(make_mkcli_call):
    """Test the resource-usage show command help"""
    result = make_mkcli_call(["resource-usage", "show", "--help"])
    assert result.exit_code == 0
    assert "Show resource usage for a cluster" in result.stdout


def test_resource_usage_show_table(
    make_mkcli_call, mock_open_context, mock_resource_client
):
    """Test the resource-usage show command with table format"""
    with mock.patch("mkcli.cli.resource.console") as mock_console:
        # Mock the table display
        mock_table = mock.MagicMock()
        mock_console.ResourceTable.return_value = mock_table

        # Call the command
        result = make_mkcli_call(["resource-usage", "show", "test-cluster-id"])

        # Verify the command execution
        assert result.exit_code == 0
        mock_resource_client.get_resource_usage.assert_called_once_with(
            "test-cluster-id"
        )

        # Verify table creation and display
        mock_console.ResourceTable.assert_called_once()
        assert mock_table.add_row.call_count == 3  # One call for each resource
        mock_table.display.assert_called_once()


def test_resource_usage_show_json(
    make_mkcli_call, mock_open_context, mock_resource_client
):
    """Test the resource-usage show command with json format"""
    with mock.patch("mkcli.cli.resource.console") as mock_console:
        # Call the command with json format
        result = make_mkcli_call(
            ["resource-usage", "show", "test-cluster-id", "--format", "json"]
        )

        # Verify the command execution
        assert result.exit_code == 0
        mock_resource_client.get_resource_usage.assert_called_once_with(
            "test-cluster-id"
        )

        # Verify JSON output
        mock_console.display.assert_called_once()
        # Extract the JSON string from the call arguments
        json_str = mock_console.display.call_args[0][0]
        # Parse and verify the JSON structure
        json_data = json.loads(json_str)
        assert "count" in json_data
        assert len(json_data["count"]) == 3


def test_resource_usage_cluster_not_found(
    make_mkcli_call, mock_open_context, mock_resource_client
):
    """Test the resource-usage show command when cluster is not found"""
    from mkcli.core.exceptions import ResourceNotFound

    # Configure the mock to raise ResourceNotFound
    mock_resource_client.get_resource_usage.side_effect = ResourceNotFound(
        "Cluster not found"
    )

    with mock.patch("mkcli.cli.resource.console") as mock_console:
        # Call the command
        result = make_mkcli_call(["resource-usage", "show", "non-existent-cluster"])

        # Verify error handling
        assert result.exit_code == 1
        mock_console.display.assert_called_once_with(
            "[bold red]Cluster non-existent-cluster not found.[/bold red]"
        )
