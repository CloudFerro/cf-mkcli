import os

from platformdirs import user_cache_dir
import typer
from pydantic_settings import BaseSettings
from pathlib import Path


ENV: str = os.getenv("MKCLI_ENV")


class AppSettings(BaseSettings):
    name: str = "mkcli"
    state_file: Path = "contexts.json"
    mk8s_api_url: str = "https://managed-kubernetes.creodias.eu/api/v1"
    default_format: str = "table"
    resource_mappings_cache: bool = False

    @property
    def cached_context_path(self) -> Path:
        return Path(typer.get_app_dir(self.name)) / self.state_file

    @property
    def cache_dir(self) -> Path:
        return Path(user_cache_dir(self.name))


class LocalAppSettings(AppSettings):
    name: str = "mkcli-local"
    state_file: Path = "contexts-local.json"
    mk8s_api_url: str = "http://localhost:10000/api/v1/"
    default_format: str = "table"
    resource_mappings_cache: bool = False


class DefaultContextSettings(BaseSettings):
    name: str = "creodias"
    realm: str = "Creodias-new"
    client_id: str = "managed-kubernetes"
    scope: str = "email profile openid"
    region: str = "WAW4-1"
    identity_server_url: str = "https://identity.cloudferro.com/auth/"


class DefaultClusterSettings(BaseSettings):
    kubernetes_version: str = "1.30.10"
    master_count: int = 3
    master_flavor: str = "hma.medium"


if ENV == "dev":
    APP_SETTINGS = LocalAppSettings()
else:
    APP_SETTINGS = AppSettings()
DEFAULT_CTX_SETTINGS = DefaultContextSettings()
