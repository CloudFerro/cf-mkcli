from __future__ import annotations
import datetime
import json
from typing import Dict
from pathlib import Path
import loguru
from pydantic import BaseModel, ConfigDict, Field

from mkcli.settings import APP_SETTINGS

# NOTE(EA): this code comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4
# TODO(EA): refactor it, move const out of here etc.


class Token(BaseModel):
    ...  # TODO: move out of the context to separate class
    token: str | None = None  # TODO: use SecretStr
    refresh_token: str | None = None
    expires_in: datetime.datetime | None = None
    renew_after: datetime.datetime | None = None
    refresh_expires_in: datetime.datetime | None = None

    def is_valid(self) -> bool:
        """Check if the token is valid"""
        return self.token is not None and self.expires_in > datetime.datetime.now()

    def is_refresh_token_valid(self) -> bool:
        return self.refresh_expires_in > datetime.datetime.now()

    def refresh(self):
        """Renew the token using the refresh token"""
        # This method should implement the logic to renew the token
        # using the refresh token. For now, it's a placeholder.
        raise NotImplementedError("Token renewal logic is not implemented yet.")


class Context(BaseModel):
    name: str
    client_id: str
    realm: str
    scope: str
    identity_server_url: str
    public_key: str | None = None

    token: Token | None = None

    # token: str | None = None  # TODO: use SecretStr
    # refresh_token: str | None = None
    # expires_in: datetime.datetime | None = None
    # renew_after: datetime.datetime | None = None
    # refresh_expires_in: datetime.datetime | None = None


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


class ContextStorage:
    PATH_PATTERN: Path = APP_SETTINGS.cached_context_path

    def __init__(self):
        self.path: Path = self.PATH_PATTERN
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure that the context file exists, if not create it"""
        if not self.path.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_all(self, cat: ContextCatalogue) -> None:
        """Write the context data catalogue to the storage"""
        with open(self.path, "w") as f:
            f.write(cat.model_dump_json())
        loguru.logger.info(f"Data saved to {self.path}")

    def load_all(self) -> ContextCatalogue:
        """Read the context data catalogue from the storage"""
        with open(self.path, "r") as f:
            data = json.load(f)
            return ContextCatalogue.model_validate(data)

    def clear(self) -> None:
        """Clear the context data catalogue"""
        self.save_all(ContextCatalogue())


class ContextCatalogue(BaseModel):
    """Catalogue of contexts, used to store and manage multiple connection contexts."""

    cat: Dict[str, Context] = {default_context.name: default_context}
    current: str = default_context.name  # TODO: rename to "active"

    storage: ContextStorage = Field(default_factory=ContextStorage, exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def switch(self, value: str):
        """Set the current context by name"""
        if value not in self.cat:
            raise ValueError(
                f"Context '{value}' does not exist in the catalogue."
                f" Available contexts: {self.list_available()}"
            )
        self.current = value
        self.save()
        loguru.logger.info(f"Current context set to '{value}'.")

    def add(self, item: Context):
        self.cat[item.name] = item
        self.save()
        loguru.logger.info(f"Context '{item.name}' added to the catalogue.")

    def list_all(self) -> list[Context]:
        """List all contexts in the catalogue"""
        return list(self.cat.values())

    def list_available(self) -> list[str]:
        """List all available context names in the catalogue"""
        return list(self.cat.keys())

    def save(self):
        """Save the current context to the storage"""
        self.storage.save_all(self)

    @classmethod
    def from_storage(cls) -> "ContextCatalogue":
        """Load the context catalogue from the storage"""
        return ContextStorage().load_all()

    def __repr__(self):
        return f"Current context: {self.cat.get(self.current)}\nCatalogue: {self.list_available()}"


class ContexStorage_Old:
    def __init__(self, config_path: Path = APP_SETTINGS.cached_context_path):
        self.config_path = config_path
        if not self.config_path.is_file():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                c = ContextCatalogue(
                    contexts={
                        default_context.name: default_context,
                    },
                    current_context=default_context.name,
                )
                f.write(c.model_dump_json())

        with open(self.config_path, "r") as f:
            data = json.load(f)
            self.state = ContextCatalogue.model_validate(data)

    def save(self, ctx: ContextCatalogue) -> None: ...

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
