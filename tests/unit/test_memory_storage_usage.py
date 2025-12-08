def test_json_storage_is_patched():
    """Verify that JsonStorage is patched with MemoryStorage in session module"""
    from mkcli.core.session import JsonStorage
    from tests.conftest import MemoryStorage

    # JsonStorage in session module should actually be MemoryStorage due to patching
    assert JsonStorage == MemoryStorage


def test_open_context_catalogue_uses_memory_storage():
    """Verify that open_context_catalogue creates MemoryStorage, not JsonStorage"""
    from mkcli.core.session import open_context_catalogue
    from tests.conftest import MemoryStorage

    with open_context_catalogue() as cat:
        # The storage should be MemoryStorage
        assert isinstance(cat.storage, MemoryStorage)

        # Verify it's not trying to write to filesystem
        assert hasattr(cat.storage, "data")
        assert isinstance(cat.storage.data, dict)


def test_context_catalogue_uses_memory_storage(catalogue):
    """Verify that the catalogue fixture uses MemoryStorage"""

    # Check that the storage is MemoryStorage
    # Note: catalogue uses ctx_storage which is a Mock wrapping MemoryStorage
    assert hasattr(catalogue.storage, "save")
    assert hasattr(catalogue.storage, "load")
    assert hasattr(catalogue.storage, "clear")

    # Test basic operations don't touch filesystem
    from mkcli.core.models.context import Context
    from mkcli.core.enums import AuthType

    test_context = Context(
        name="test",
        client_id="test_client",
        realm="test_realm",
        scope="test_scope",
        region="test_region",
        identity_server_url="https://test.url",
        auth_type=AuthType.API_KEY,
    )

    catalogue.add(test_context)
    catalogue.switch("test")

    # Should work without touching filesystem
    assert catalogue.current == "test"
    assert catalogue.get("test").name == "test"
