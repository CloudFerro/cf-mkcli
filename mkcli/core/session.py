from contextlib import contextmanager
from mkcli.core.models.context import ContextCatalogue


@contextmanager
def open_context_catalogue() -> "ContextCatalogue":
    """Context manager to open a ContextCatalogue and ensure it is closed properly."""
    cat = ContextCatalogue.from_storage()
    try:
        yield cat
    finally:
        cat.save()
