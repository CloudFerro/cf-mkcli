import datetime
import json
from typing import Dict
from pathlib import Path

from pydantic import BaseModel


class Context(BaseModel):
    name: str
    realm: str
    client_id: str
    scope: str
    identity_server_url: str
    token: str | None = None
    expires_in: datetime.datetime | None = None
    renew_after: datetime.datetime | None = None
    refresh_token: str | None = None
    refresh_expires_in: datetime.datetime | None = None
    public_key: str | None = None


class CliContext(BaseModel):
    contexts: Dict[str, Context]
    current_context: str


# next use prompt to create this
default_context = Context(
    name="creodias",
    realm="Creodias-new",
    client_id="auth-portal",
    scope="openid aud-public",
    identity_server_url="https://identity.cloudferro.com/auth/",
    token=None,
    public_key=None,
)


class ContextData:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        if not self.config_path.is_file():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                c = CliContext(
                    contexts={
                        default_context.name: default_context,
                    },
                    current_context=default_context.name,
                )
                f.write(c.model_dump_json())

        with open(self.config_path, "r") as f:
            data = json.load(f)
            self.state = CliContext.model_validate(data)

    def save(self, ctx: CliContext) -> None:
        with open(self.config_path, "w") as f:
            f.write(ctx.model_dump_json())

    def json(self):
        return self.state.model_dump_json()

    def current_context_name(self) -> str:
        return self.state.current_context

    def current_context(self) -> Context:
        return self.state.contexts[self.current_context_name()]

    @property
    def token(self):
        return self.state.contexts[self.state.current_context].token

    def refresh_token(self):
        return self.state.contexts[self.state.current_context].refresh_token

    def save_token(
        self, token, expires_in, renew_after, refresh_token, refresh_expires_in
    ):
        name = self.current_context_name()
        self.state.contexts[name].token = token
        self.state.contexts[name].expires_in = expires_in
        self.state.contexts[name].renew_after = renew_after
        self.state.contexts[name].refresh_token = refresh_token
        self.state.contexts[name].refresh_expires_in = refresh_expires_in
        self.save(self.state)

    def clear_token(self):
        name = self.current_context_name()
        self.state.contexts[name].token = None
        self.state.contexts[name].refresh_token = None
        self.state.contexts[name].expires_in = None
        self.state.contexts[name].renew_after = None
        self.state.contexts[name].refresh_expires_in = None
        self.save(self.state)

    def should_renew_token(self) -> bool:
        return self.current_context().renew_after < datetime.datetime.now()

    def is_refresh_token_valid(self) -> bool:
        return self.current_context().refresh_expires_in > datetime.datetime.now()
