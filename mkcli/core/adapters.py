import os
import webbrowser
from typing import Dict, Optional, Protocol

from keycloak import KeycloakOpenID
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from .callback import CallbackServer
from .models import Context, Token
from mkcli.utils import wait_until


class AuthProtocol(Protocol):
    def get_auth_header(self) -> Dict[str, str | None]: ...

    def validate(self) -> None: ...


class APIKeyAdapter:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.ctx.api_key = ctx.api_key or os.getenv("MK8S_API_KEY")

    def get_auth_header(self) -> Dict[str, str | None]:
        self.validate()
        return {"Authorization": f"Token {self.ctx.api_key}"}

    def validate(self):
        if not self.ctx.api_key:
            raise ValueError("API Key is not set")


class OpenIDAdapter:
    def __init__(self, ctx: Context):
        self._ctx = ctx  # Note(EA): I dont like that auth adapter changes smth in ctx (token attrs values)
        self._keycloak_openid: Optional[KeycloakOpenID] = None

    def get_auth_header(self) -> Dict[str, str | None]:
        if not self.token.access_token:
            raise ValueError("Token is not set")
        return {
            "authorization": f"Bearer {self.token.access_token}",
        }

    def clear(self) -> None:
        self._ctx.token = Token()

    @property
    def token(self) -> Token:
        if self._ctx.token is None:
            self._ctx.token = Token()
        if self._ctx.token.should_be_renew():
            if self._ctx.token.is_refresh_token_valid():
                self._renew_token_with_refresh_token()
            else:
                self.renew_token()
        return self._ctx.token

    @property
    def keycloak_openid(self) -> KeycloakOpenID:
        if self._keycloak_openid:
            return self._keycloak_openid
        self._keycloak_openid = KeycloakOpenID(
            server_url=self._ctx.identity_server_url,
            client_id=self._ctx.client_id,
            realm_name=self._ctx.realm,
        )
        return self._keycloak_openid

    def _renew_token_with_refresh_token(self) -> None:
        logger.debug(
            "Renewing token with refresh token for context: {}", self._ctx.name
        )
        response = self.keycloak_openid.refresh_token(self._ctx.token.refresh_token)  # type: ignore
        self._ctx.token = Token.load_from_response(response)

    def renew_token(self) -> None:
        logger.debug("Renewing token for context: {}", self._ctx.name)
        with CallbackServer() as s:
            if not wait_until(s.ready, 5, 0.02):
                raise Exception("Server not ready")

            auth_url = self.keycloak_openid.auth_url(
                redirect_uri=f"{s.base_url}/callback", scope=self._ctx.scope
            )
            webbrowser.open(auth_url)

            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]"), transient=True
            ) as progress:
                progress.add_task("waiting for callback...")
                wait_until(s.called, 60, 0.05)
                resp = self.keycloak_openid.token(
                    grant_type="authorization_code",
                    code=s.access_code,  # type: ignore
                    redirect_uri=f"{s.base_url}/callback",
                )
            self._ctx.token = Token.load_from_response(resp)

    def validate(self) -> None:
        if not self.token.access_token:
            raise ValueError("Token is not set")  # TODO(EA): custom exception
