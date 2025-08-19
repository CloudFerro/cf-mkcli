from contextlib import contextmanager
from mkcli.core.models.context import ContextCatalogue, JsonStorage


@contextmanager
def open_context_catalogue():
    """Context manager to open a ContextCatalogue and ensure it is closed properly."""
    storage = JsonStorage()
    cat = ContextCatalogue(storage=storage)

    try:
        yield cat
    finally:
        cat.save()
