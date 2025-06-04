from platformdirs import user_cache_dir
import typer
from pydantic_settings import BaseSettings
from pathlib import Path


class AppSettings(BaseSettings):
    name: str = "mkcli"
    state_file: Path = "contexts.json"
    mk8s_api_url: str = "https://managed-kubernetes.creodias.eu/api/v1"

    @property
    def cached_context_path(self) -> Path:
        return Path(typer.get_app_dir(self.name)) / self.state_file

    @property
    def cache_dir(self) -> Path:
        return Path(user_cache_dir(self.name))


class DefaultContextSettings(BaseSettings):
    name: str = "creodias"
    realm: str = "Creodias-new"
    client_id: str = "managed-kubernetes"
    scope: str = "email profile openid"
    region: str = "WAW4-1"
    identity_server_url: str = "https://identity.cloudferro.com/auth/"


class DefaultNodePoolSettings(BaseSettings):
    name: str | None = None
    node_count: int = 1
    min_nodes: int = 1
    max_nodes: int = 10
    autoscale: bool = False
    flavor_id: str = "b003e1cf-fd40-4ad1-827c-cc20c2ddd519"  # Example default flavor ID


class DefaultClusterSettings(BaseSettings):
    kubernetes_version: str = "1.30.10"
    master_count: int = 3
    master_flavor: str = "hma.2xlarge"


APP_SETTINGS = AppSettings()
DEFAULT_CTX_SETTINGS = DefaultContextSettings()
