from __future__ import annotations
import json
from typing import Dict, Optional, Any, ClassVar, Protocol
from pathlib import Path
from loguru import logger
from pydantic import BaseModel

from mkcli.core import exceptions as exc
from mkcli.core.models import Token
from mkcli.settings import APP_SETTINGS, DEFAULT_CTX_SETTINGS, AuthType

type key = str | None


class Context(BaseModel):
    """Represents a connection context for authentication with an identity server."""

    table_columns: ClassVar[list[str]] = [
        "Name",
        "Client ID",
        "Realm",
        "Scope",
        "Region",
        "Identity Server",
        "Auth Type",
    ]

    name: str
    client_id: str
    realm: str
    scope: str
    region: str
    identity_server_url: str
    auth_type: AuthType
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
            self.auth_type,
        ]

    def as_json(self) -> Dict[str, Any]:
        """Return the context as a JSON serializable dictionary"""
        return {
            "name": self.name,
            "client_id": self.client_id,
            "realm": self.realm,
            "scope": self.scope,
            "region": self.region,
            "identity_server_url": self.identity_server_url,
            "auth_type": self.auth_type,
        }


default_context = Context(**DEFAULT_CTX_SETTINGS.model_dump())


class ContextStorage(Protocol):
    """Protocol for context storage, defines methods for saving and loading contexts."""

    def ensure_exists(self) -> None: ...

    def init_storage(self, _data: dict) -> None: ...

    def save(self, _dict: dict) -> None: ...

    def load(self) -> dict: ...

    def clear(self) -> None: ...


class JsonStorage:
    PATH_PATTERN: Path = APP_SETTINGS.cached_context_path  # TODO(EA): rename

    def __init__(self):
        self.path: Path = self.PATH_PATTERN

    def ensure_exists(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"Context file {self.path} does not exist.")

    def init_storage(self, _data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        with open(self.path, "w") as f:
            f.write(json.dumps(_data))

    def save(self, _dict: dict) -> None:
        with open(self.path, "w") as f:
            f.write(json.dumps(_dict))
        logger.info(f"Data saved to {self.path}")

    def load(self) -> dict:
        with open(self.path, "r") as f:
            try:
                logger.info(f"Data loaded from {self.path}")
                return json.load(f)
            except json.JSONDecodeError:
                raise exc.InvalidFileLayout(file_path=str(self.path))

    def clear(self) -> None:
        if self.path.is_file():
            self.path.unlink()
            logger.info(f"Context file {self.path} cleared.")
        else:
            logger.warning(
                f"Context file {self.path} does not exist, nothing to clear."
            )

    def __repr__(self):
        return f"JsonStorage(path={self.path})"


class ContextCatalogue:
    """Catalogue of contexts, used to store and manage multiple connection contexts."""

    def __init__(self, storage: ContextStorage) -> None:
        self.current: str | None = None
        self.cat: Dict[key, Context] = {}

        self.storage: ContextStorage = storage
        self.ensure_storage()
        self.load()

    def ensure_storage(self):
        """Ensure the context storage is initialized and ready to use"""
        try:
            self.storage.ensure_exists()
        except FileNotFoundError:
            self.storage.init_storage({"current": None, "cat": {}})
        except json.JSONDecodeError:
            raise exc.InvalidFileLayout(file_path=str(self.storage))

    def load(self):
        """Load the context catalogue from storage"""
        # try:
        data = self.storage.load()
        self.current = data.get("current")
        self.cat = {name: Context(**ctx) for name, ctx in data.get("cat", {}).items()}

    def switch(self, value: str):
        """Set the current context by name"""
        if value not in self.cat:
            raise exc.ContextNotFound(
                context_name=value, available_contexts=self.list_available()
            )
        self.current = value
        self.save()
        logger.info(f"Current context set to '{value}'.")

    @property
    def current_context(self) -> Context:
        try:
            return self.cat[self.current]
        except KeyError:
            raise exc.NoActiveSession()

    def save(self):
        """Save the current context to the storage"""
        self.storage.save(self.as_dict())
        logger.info("Context catalogue saved.")

    def add(self, item: Context):
        """Add a new context to the catalogue"""
        self.cat[item.name] = item
        self.save()
        logger.info(f"Context '{item.name}' added to the catalogue.")

    def get(self, name: str) -> Context:
        """Returns the context deep copy"""
        if name not in self.cat:
            raise exc.ContextNotFound(
                context_name=name, available_contexts=self.list_available()
            )
        return self.cat[name].model_copy(deep=True)

    def delete(self, name: str):
        """Remove a context from the catalogue by name"""
        del self.cat[name]
        self.save()
        logger.info(f"Removed context '{name}' from the catalogue.")

    def purge(self):
        """Remove all contexts from the catalogue"""
        self.cat.clear()
        self.current = None
        self.save()
        logger.info("All contexts removed from the catalogue.")

    def list_all(self) -> list[Context]:
        """List all contexts in the catalogue"""
        return list(self.cat.values())

    def list_available(self) -> list[str]:
        """List all available context names in the catalogue"""
        return list(self.cat.keys())  # type: ignore

    def as_dict(self) -> dict[str, Any]:
        """Convert the context catalogue to a dictionary"""
        return {
            "current": self.current,
            "cat": {name: context.model_dump() for name, context in self.cat.items()},
        }

    def __repr__(self):
        return f"Current context: {self.cat.get(self.current)}\nCatalogue: {self.list_available()}"
