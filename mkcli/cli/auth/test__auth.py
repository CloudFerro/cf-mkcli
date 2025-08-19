import pytest
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
            public_key="test_key",
        )
    )
