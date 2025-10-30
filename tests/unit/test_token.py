import json
from mkcli.core.models.token import Token
from datetime import datetime, timedelta, timezone


def test_is_token_valid():
    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert token.is_valid()

    token = Token(
        access_token=None,
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert not token.is_valid()

    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) - timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert not token.is_valid()


def test_is_refresh_token_valid():
    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert token.is_refresh_token_valid()

    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) - timedelta(seconds=600),
    )
    assert not token.is_refresh_token_valid()


def test_should_be_renew():
    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) - timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert token.should_be_renew()

    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=300),
        renew_after=datetime.now(tz=timezone.utc) + timedelta(seconds=150),
        refresh_expires_in=datetime.now(tz=timezone.utc) + timedelta(seconds=600),
    )
    assert not token.should_be_renew()


def test_serialize_date():
    token = Token(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=datetime(2024, 1, 1, 12, 0, 0),
        renew_after=datetime(2024, 1, 1, 12, 0, 0),
        refresh_expires_in=datetime(2024, 1, 1, 12, 0, 0),
    )
    serialized = token.model_dump_json()
    _dict = json.loads(serialized)
    assert _dict == {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": "2024-01-01T12:00:00.000000+00:00",
        "renew_after": "2024-01-01T12:00:00.000000+00:00",
        "refresh_expires_in": "2024-01-01T12:00:00.000000+00:00",
    }


def test_load_from_json():
    response = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 300,
        "refresh_expires_in": 600,
        "renew_after": 150,
    }
    now = datetime.now(tz=timezone.utc)
    token = Token.load_from_response(response)
    assert token.access_token == "test_access_token"
    assert token.refresh_token == "test_refresh_token"
    assert token.expires_in is not None
    assert token.refresh_expires_in is not None
    assert token.renew_after is not None
    assert token.expires_in > now
    assert token.renew_after > now + timedelta(seconds=150)
    assert token.refresh_expires_in > now + timedelta(seconds=600)
