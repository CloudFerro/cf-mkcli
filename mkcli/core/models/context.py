from __future__ import annotations
import json
from typing import Dict, Optional
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from mkcli.core.models import Token
from mkcli.settings import APP_SETTINGS, DEFAULT_CTX_SETTINGS


# NOTE(EA): this code comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4
# TODO(EA): refactor it, move const out of here etc.


class Context(BaseModel):
    name: str
    client_id: str
    realm: str
    scope: str
    region: str
    identity_server_url: str
    public_key: str | None = None
    token: Optional[Token] = None

    def as_table_row(self):
        """Return a list of values to be used in a table row"""
        return [
            self.name,
            self.client_id,
            self.realm,
            self.scope,
            self.region,
            self.identity_server_url,
        ]


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
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                cat = ContextCatalogue.model_validate(data)
        except FileNotFoundError:
            logger.warning(
                f"Context file {self.path} not found, creating new catalogue."
            )
            cat = ContextCatalogue()
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

    def pop(self, name):
        """Get and remove a context from the catalogue by name"""
        if name not in self.cat:
            raise ValueError(f"Context '{name}' does not exist in the catalogue.")
        if self.current == name:
            raise ValueError(
                f"Cannot remove the current context '{name}'. Switch to another context first."
            )
        item = self.cat.pop(name)
        return item

    def get(self, name: str) -> Context:
        """Returns the context deep copy"""
        return self.cat[name].model_copy(deep=True)

    def delete(self, name: str):
        """Remove a context from the catalogue by name"""
        if self.current == name:
            raise ValueError(
                f"Cannot remove the current context '{name}'. Switch to another context first."
            )
        del self.cat[name]
        self.save()

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
