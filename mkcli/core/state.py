import datetime
import webbrowser
from typing import Dict, Optional

from keycloak import KeycloakOpenID
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .callback import CallbackServer
from .models import ContextData
from .enums import AuthType
from mkcli.utils import wait_until
from mkcli.settings import APP_SETTINGS

# NOTE(EA): this code comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4
# TODO(EA): refactor it, move const out of here etc.


class State:
    def __init__(self):
        self.ctx = ContextData(APP_SETTINGS.confing_path)
        self._keycloak_openid: Optional[KeycloakOpenID] = None

    def show(self) -> None:
        data = self.ctx.json()
        console = Console()
        console.print(data)

    def clear(self) -> None:
        self.ctx.clear_token()

    def _select_auth_type(self) -> AuthType:  # TODO: implement other auth types
        return AuthType.JWT

    def auth_headers(self) -> Dict:
        auth_type = self._select_auth_type()
        match auth_type:
            case AuthType.JWT:
                return {"authorization": f"Bearer {self.token}"}
            case _:
                return {}

    def _maybe_refresh_token(self) -> None:
        if self.ctx.should_renew_token():
            if self.ctx.is_refresh_token_valid():
                self._renew_token_with_refresh_token()
            else:
                self.renew_token()

    @property
    def token(self) -> str:
        self._maybe_refresh_token()
        return self.ctx.token

    @property
    def keycloak_openid(self) -> KeycloakOpenID:
        if self._keycloak_openid:
            return self._keycloak_openid
        current = self.ctx.current_context()
        self._keycloak_openid = KeycloakOpenID(
            server_url=current.identity_server_url,
            client_id=current.client_id,
            realm_name=current.realm,
        )
        return self._keycloak_openid

    def _renew_token_with_refresh_token(self) -> None:
        token = self.keycloak_openid.refresh_token(self.ctx.refresh_token())
        self._save_token(token)

    def renew_token(self) -> None:
        with CallbackServer() as s:
            if not wait_until(s.ready, 5, 0.02):
                raise Exception("Server not ready")

            current = self.ctx.current_context()
            auth_url = self.keycloak_openid.auth_url(
                redirect_uri=f"{s.base_url}/callback", scope=current.scope
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

        self.ctx.save_token(
            openid_response.get("access_token"),
            expires_in,
            renew_after,
            openid_response.get("refresh_token"),
            refresh_expires_in,
        )
