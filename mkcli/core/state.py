import datetime
import webbrowser
from typing import Dict, Optional

from keycloak import KeycloakOpenID
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from .callback import CallbackServer
from .models import Context, Token
from mkcli.utils import wait_until

# NOTE(EA): this code basically comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4
# TODO(EA): refactor it, move const out of here etc.


class State:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self._keycloak_openid: Optional[KeycloakOpenID] = None

    def clear(self) -> None:  # maybe clear creds
        self.ctx.token.clear()

    @property
    def token(self) -> str:
        if (
            self.ctx.token is None or self.ctx.token.access_token is None
        ):  # TODO: refactor this ugliness (!)
            self.renew_token()
        if self.ctx.token.should_be_renew():
            if self.ctx.token.is_refresh_token_valid():
                self._renew_token_with_refresh_token()
            else:
                self.renew_token()

        return self.ctx.token.access_token

    @token.setter
    def token(self, value: str) -> None:
        if self.ctx.token is None:
            self.ctx.token = Token()
        self.ctx.token.access_token = value

    @property
    def keycloak_openid(self) -> KeycloakOpenID:
        if self._keycloak_openid:
            return self._keycloak_openid
        self._keycloak_openid = KeycloakOpenID(
            server_url=self.ctx.identity_server_url,
            client_id=self.ctx.client_id,
            realm_name=self.ctx.realm,
        )
        return self._keycloak_openid

    def _renew_token_with_refresh_token(self) -> None:
        logger.info("Renewing token with refresh token for context: {}", self.ctx.name)
        token = self.keycloak_openid.refresh_token(self.ctx.token.refresh_token)
        self._save_token(token)

    def renew_token(self) -> None:
        logger.info("Renewing token for context: {}", self.ctx.name)
        with CallbackServer() as s:
            if not wait_until(s.ready, 5, 0.02):
                raise Exception("Server not ready")

            auth_url = self.keycloak_openid.auth_url(
                redirect_uri=f"{s.base_url}/callback", scope=self.ctx.scope
            )
            webbrowser.open(auth_url)

            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]"), transient=True
            ) as progress:
                progress.add_task("waiting for callback...")
                wait_until(s.called, 60, 0.05)

            access_token = self.keycloak_openid.token(
                grant_type="authorization_code",
                code=s.access_code,
                redirect_uri=f"{s.base_url}/callback",
            )
            self._save_token(access_token)

    def _save_token(self, openid_response: Dict) -> None:
        now = datetime.datetime.now()
        expires_in = now + datetime.timedelta(seconds=openid_response.get("expires_in"))
        renew_after = now + datetime.timedelta(
            seconds=int(openid_response.get("expires_in") / 2)
        )
        refresh_expires_in = now + datetime.timedelta(
            seconds=openid_response.get("refresh_expires_in")
        )
        logger.info("Setting new token to context: {}", self.ctx.name)
        self.ctx.token = Token(
            access_token=openid_response.get("access_token"),
            expires_in=expires_in,
            renew_after=renew_after,
            refresh_token=openid_response.get("refresh_token"),
            refresh_expires_in=refresh_expires_in,
        )

    def __repr__(self):
        return f"State(ctx={self.ctx}, token={self.ctx.token})"
