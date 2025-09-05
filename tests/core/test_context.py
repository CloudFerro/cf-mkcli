import pytest
import json
from mkcli.core import exceptions as exc
from mkcli.core.enums import AuthType
from mkcli.core.models.context import Context
from mkcli.core.models.context import JsonStorage


def test_context_catalogue(catalogue, ctx_storage):
    catalogue = catalogue
    assert catalogue.storage == ctx_storage
    assert catalogue.cat == {}

    ctx_storage.load.assert_called_once()


def test_context_catalogue_add(catalogue):
    new_ctx = Context(
        name="test",
        client_id="test_client",
        realm="test_realm",
        scope="test_scope",
        region="test_region",
        identity_server_url="https://test.identity.server",
        auth_type=AuthType.OPENID,
    )
    catalogue.add(new_ctx)
    assert catalogue.cat["test"] == new_ctx
    assert len(catalogue.list_available()) == 1
    assert len(catalogue.storage.save.mock_calls) == 1


def test_context_catalogue_switch(catalogue):
    assert len(catalogue.list_available()) == 1

    ctx2 = Context(
        name="test2",
        client_id="test2_client",
        realm="test2_realm",
        scope="test2_scope",
        region="test2_region",
        identity_server_url="https://test2.identity.server",
        auth_type=AuthType.OPENID,
    )
    catalogue.add(ctx2)
    assert catalogue.cat["test2"] == ctx2
    assert len(catalogue.list_available()) == 2
    assert len(catalogue.storage.save.mock_calls) == 2

    catalogue.switch("test2")
    assert catalogue.current == "test2"

    catalogue.storage.load.assert_called_once()
    assert len(catalogue.storage.save.mock_calls) == 3


def test_context_catalogue_remove(catalogue):
    assert len(catalogue.list_available()) == 2

    catalogue.delete("test")
    assert "test" not in catalogue.cat
    assert len(catalogue.storage.save.mock_calls) == 4
    assert len(catalogue.list_available()) == 1


def test_context_catalogue_switch_to_non_existent(catalogue):
    with pytest.raises(exc.ContextNotFound):
        catalogue.switch("non_existent_context")

    # Ensure the current context remains unchanged
    assert catalogue.current == "test2"


def test_context_catalogue_get_non_existent(catalogue):
    with pytest.raises(exc.ContextNotFound):
        catalogue.get("non_existent_context")


def test_json_storage_init_storage(tmp_path):
    # Create a JsonStorage instance with a path in a temporary directory
    test_data = {"current": None, "cat": {}}
    test_file = tmp_path / "test_context.json"
    storage = JsonStorage()
    storage.path = test_file

    # Test initialization of storage
    storage.init_storage(test_data)

    # Verify file was created
    assert test_file.exists()

    # Verify data was written correctly
    with open(test_file, "r") as f:
        loaded_data = json.load(f)
        assert loaded_data == test_data

    # Test with nested directories
    nested_path = tmp_path / "nested" / "dirs" / "context.json"
    storage.path = nested_path
    storage.init_storage(test_data)

    # Verify nested directories were created and file exists
    assert nested_path.exists()

    # Test with existing file (should overwrite)
    modified_data = {"current": "test", "cat": {"test": {"name": "test"}}}
    storage.init_storage(modified_data)
    with open(nested_path, "r") as f:
        loaded_data = json.load(f)
        assert loaded_data == modified_data
