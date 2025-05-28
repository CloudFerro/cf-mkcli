from __future__ import annotations
import datetime
import json
from typing import Dict, Optional
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from mkcli.settings import APP_SETTINGS, DEFAULT_CTX_SETTINGS


# NOTE(EA): this code comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4
# TODO(EA): refactor it, move const out of here etc.


class Token(BaseModel):
    access_token: str | None = None  # TODO: use SecretStr
    refresh_token: str | None = None
    expires_in: datetime.datetime | None = None
    renew_after: datetime.datetime | None = None
    refresh_expires_in: datetime.datetime | None = None

    def clear(self):
        """Clear the token and its related fields"""
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.renew_after = None
        self.refresh_expires_in = None

    def is_valid(self) -> bool:
        """Check if the token is valid"""
        return (
            self.access_token is not None and self.expires_in > datetime.datetime.now()
        )

    def is_refresh_token_valid(self) -> bool:
        return self.refresh_expires_in > datetime.datetime.now()

    def should_be_renew(self) -> bool:
        return self.renew_after < datetime.datetime.now()


class Context(BaseModel):
    name: str
    client_id: str
    realm: str
    scope: str
    identity_server_url: str
    public_key: str | None = None

    # TODO: use Enum to annotate auth_type,
    # TODO: add managing different auth types, which should inherit from some abc abstract class or
    #  Protocol and have consistent interface
    # auth_type: str = Field(default="token", exclude=True)
    token: Optional[Token] = None


# TODO: next use prompt to create this
default_context = Context(**DEFAULT_CTX_SETTINGS.dict())


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
        logger.info(f"Data saved to {self.path}")

    def load_all(self) -> ContextCatalogue:
        """Read the context data catalogue from the storage"""
        with open(self.path, "r") as f:
            data = json.load(f)
            cat = ContextCatalogue.model_validate(data)
            logger.info(f"Loaded context catalogue from {ContextStorage.PATH_PATTERN}")
        return cat

    def clear(self) -> None:
        """Clear the context data catalogue"""
        self.save_all(ContextCatalogue())


class ContextCatalogue(BaseModel):
    """Catalogue of contexts, used to store and manage multiple connection contexts."""

    cat: Dict[str, Context] = {default_context.name: default_context}
    current: str = default_context.name

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
        logger.info(f"Current context set to '{value}'.")

    @property
    def current_context(self) -> Context:
        return self.cat[self.current]  # TODO: maybe setter

    def add(self, item: Context):
        self.cat[item.name] = item
        self.save()
        logger.info(f"Context '{item.name}' added to the catalogue.")

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
        cat = ContextStorage().load_all()
        return cat

    def __repr__(self):
        return f"Current context: {self.cat.get(self.current)}\nCatalogue: {self.list_available()}"
