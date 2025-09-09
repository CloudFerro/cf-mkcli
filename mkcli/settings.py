from collections import defaultdict
import os

from platformdirs import user_cache_dir
import typer
from pydantic_settings import BaseSettings
from pathlib import Path
from mkcli.core.enums import Format, AuthType


ENV: str = os.getenv("MKCLI_ENV") or ""


API_URL_MAPPING = {
    "Creodias-new": "https://managed-kubernetes.creodias.eu/api/v1",
    "CloudFerro-Cloud": "https://managed-kubernetes.cloudferro.com/api/v1",
}

if ENV == "dev":
    API_URL_MAPPING = defaultdict(lambda: "http://localhost:8080/api/v1")


class AppSettings(BaseSettings):
    name: str = "mkcli"
    session_persistence_file: Path = Path("contexts.json")
    default_format: str = Format.TABLE
    resource_mappings_cache: bool = False

    @property
    def cached_context_path(self) -> Path:
        return Path(typer.get_app_dir(self.name)) / self.session_persistence_file

    @property
    def cache_dir(self) -> Path:
        return Path(user_cache_dir(self.name))


class DefaultContextSettings(BaseSettings):
    name: str = "default"
    realm: str = "Creodias-new"
    client_id: str = "managed-kubernetes"
    scope: str = "email profile openid"
    region: str = "WAW4-1"
    identity_server_url: str = "https://identity.cloudferro.com/auth/"
    auth_type: AuthType = AuthType.OPENID


class DefaultClusterSettings(BaseSettings):
    kubernetes_version: str = "1.30.10"
    master_count: int = 3
    master_flavor: str = "hma.medium"


DEFAULT_CTX_SETTINGS = DefaultContextSettings()
APP_SETTINGS = AppSettings()
