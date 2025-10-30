from unittest import mock
import pydantic
import pytest
from mkcli.core import exceptions as exc
from mkcli.core.enums import AuthType
from mkcli.core.models.context import Context
from mkcli.core.session import get_auth_adapter
from mkcli.core.adapters import OpenIDAdapter, APIKeyAdapter


def get_context(auth_type: AuthType) -> Context:
    return Context(
        name="test_ctx",
        client_id="test_client_id",
        realm="test_realm",
        scope="test_scope",
        region="test_region",
        identity_server_url="https://test.identity.server",
        auth_type=auth_type,
    )


def test_no_active_session(mock_open_context):
    cat = mock_open_context
    assert len(cat.list_all()) == 0  # Ensure no contexts are available
    with pytest.raises(exc.NoActiveSession):
        print("cat.current_context:", len(cat.list_all()), cat.current_context)
        get_auth_adapter(cat.current_context)


@pytest.mark.parametrize(
    "auth_type, expected_adapter",
    [(AuthType.OPENID, OpenIDAdapter), (AuthType.API_KEY, APIKeyAdapter)],
)
def test_get_auth_adapter(auth_type, expected_adapter):
    ctx = get_context(auth_type)
    adapter = get_auth_adapter(ctx)
    assert adapter is not None
    assert isinstance(adapter, expected_adapter)


def test_cant_set_unsupported_auth_type():
    with pytest.raises(ValueError):  # can't create Enum with unsupported value
        _ = AuthType("UNSUPPORTED")  # type: ignore

    with pytest.raises(
        pydantic.ValidationError
    ):  # can't pass pydantic validation for Context since auth_type is Enum
        auth_type = mock.Mock()
        _ = get_context(auth_type)

    with pytest.raises(
        ValueError
    ):  # raise error even if Context is created as other type
        ctx = mock.Mock()
        ctx.auth_type = "UNSUPPORTED"
        _ = get_auth_adapter(ctx)  # type: ignore
