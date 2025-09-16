import datetime
import os
from unittest import mock
import pytest
from mkcli.core.models.context import Context, Token
from mkcli.core.enums import AuthType
from mkcli.core.adapters import APIKeyAdapter, OpenIDAdapter
from mkcli.core.exceptions import AuthorizationError


def get_context(auth_type: AuthType) -> Context:
    return Context(
        name="test_ctx",
        client_id="test_client_id",
        realm="test_realm",
        scope="test_scope",
        region="test_region",
        identity_server_url="https://test.identity.server",
        auth_type=auth_type,
        api_key=None,  # type: ignore
    )


os.environ["MK8S_API_KEY"] = "test_api_key_from_env"


def test_api_key_adapter_loading_key():
    # case when api key is not set in the context, but is in env vars
    ctx = get_context(AuthType.API_KEY)
    adapter = APIKeyAdapter(ctx)

    assert adapter.ctx.api_key is not None
    assert adapter.ctx.api_key == "test_api_key_from_env"
    assert adapter.get_auth_header() == {"Authorization": "Token test_api_key_from_env"}

    # case when api key is set in the context
    ctx.api_key = "ctx_api_key"
    adapter = APIKeyAdapter(ctx)
    assert adapter.ctx.api_key == "ctx_api_key"
    assert adapter.get_auth_header() == {"Authorization": "Token ctx_api_key"}

    # case when api key is not set in the context neither in env vars
    os.environ["MK8S_API_KEY"] = ""
    ctx.api_key = ""
    adapter = APIKeyAdapter(ctx)

    with pytest.raises(AuthorizationError):
        adapter.validate()


@mock.patch.dict(os.environ, {"MK8S_API_KEY": ""}, clear=True)
def test_api_key_adapter_no_env_var():
    ctx = get_context(AuthType.API_KEY)
    ctx.api_key = None
    adapter = APIKeyAdapter(ctx)
    assert adapter.ctx.api_key == ""
    with pytest.raises(AuthorizationError):
        adapter.get_auth_header()


def test_openid_adapter_getting_empty_header_raises_error():
    with mock.patch("mkcli.core.models.token.Token") as MockedToken:
        MockedToken.return_value = Token(access_token=None, refresh_token=None)
        OpenIDAdapter.renew_token = mock.Mock(return_value=None)
        OpenIDAdapter._renew_token_with_refresh_token = mock.Mock(return_value=None)

        ctx = get_context(AuthType.OPENID)
        adapter = OpenIDAdapter(ctx)

        with pytest.raises(AuthorizationError):
            adapter.get_auth_header()


def test_openid_adapter_with_valid_token():
    # mocked_token = mock.Mock()
    ctx = get_context(AuthType.OPENID)
    ctx.token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=300),
        refresh_expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=600),
    )
    adapter = OpenIDAdapter(ctx)
    adapter.validate()
    assert adapter.get_auth_header() == {"authorization": "Bearer test_access_token"}


def test_openid_adapter_with_refresh_token():
    # mocked_token = mock.Mock()
    ctx = get_context(AuthType.OPENID)
    ctx.token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(seconds=300),
        renew_after=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(seconds=150),
        refresh_expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=600),
    )
    new_token = Token(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=300),
        refresh_expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=600),
    )
    # Mock the methods that would perform network calls

    mock_renew_with_refresh_token = mock.Mock(
        return_value=None, side_effect=lambda: setattr(ctx, "token", new_token)
    )
    OpenIDAdapter._renew_token_with_refresh_token = mock_renew_with_refresh_token

    adapter = OpenIDAdapter(ctx)

    assert adapter.get_auth_header() == {"authorization": "Bearer new_access_token"}
    assert (
        mock_renew_with_refresh_token.call_count == 1
    )  # called once to renew the token


def test_openid_adapter_with_expired_token():
    # mocked_token = mock.Mock()
    ctx = get_context(AuthType.OPENID)
    ctx.token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(seconds=300),
        renew_after=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(seconds=150),
        refresh_expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        - datetime.timedelta(seconds=600),
    )
    new_token = Token(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=300),
        refresh_expires_in=datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=600),
    )
    # Mock the methods that would perform network calls

    mock_renew_token = mock.Mock(
        return_value=None, side_effect=lambda: setattr(ctx, "token", new_token)
    )
    OpenIDAdapter.renew_token = mock_renew_token

    adapter = OpenIDAdapter(ctx)

    assert adapter.get_auth_header() == {"authorization": "Bearer new_access_token"}
    assert mock_renew_token.call_count == 1  # called once to renew the token
