import pytest
from unittest.mock import patch
from tests.conftest import MemoryStorage


@pytest.fixture(scope="session", autouse=True)
def patch_json_storage():
    """
    Automatically patch JsonStorage with MemoryStorage for unit tests.
    This ensures no unit tests accidentally write to the filesystem.
    We patch it in mkcli.core.session where it's used in open_context_catalogue.
    """
    with patch("mkcli.core.session.JsonStorage", MemoryStorage):
        yield


@pytest.fixture(scope="session", autouse=True)
def setup_unit_test_settings():
    """
    Additional unit test specific settings.
    This extends the base test_app_settings from the main conftest.py
    """
    # The main conftest.py already handles most settings
    # Add any unit-test-specific overrides here if needed
    yield
