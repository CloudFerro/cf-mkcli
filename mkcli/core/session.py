from contextlib import contextmanager

from mkcli.core.models.context import ContextCatalogue, JsonStorage, Context
from mkcli.settings import AuthType
from mkcli.core.adapters import AuthProtocol, OpenIDAdapter, APIKeyAdapter


@contextmanager
def open_context_catalogue():
    """Context manager to open a ContextCatalogue and ensure it is closed properly."""
    storage = JsonStorage()
    cat = ContextCatalogue(storage=storage)

    try:
        yield cat
    finally:
        cat.save()


def get_auth_adapter(ctx: Context) -> AuthProtocol:
    """Get auth adapter for given context."""
    match ctx.auth_type:
        case AuthType.OPENID:
            return OpenIDAdapter(ctx)

        case AuthType.API_KEY:
            return APIKeyAdapter()
