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


class DefaultContextSettings(BaseSettings):
    name: str = "creodias"
    realm: str = "Creodias-new"
    client_id: str = "managed-kubernetes"
    scope: str = "email profile openid"
    identity_server_url: str = "https://identity.cloudferro.com/auth/"


class DefaultNodePoolSettings(BaseSettings):
    name: str | None = None
    node_count: int = 1
    min_nodes: int = 1
    max_nodes: int = 10
    autoscale: bool = False
    flavor_id: str = "b003e1cf-fd40-4ad1-827c-cc20c2ddd519"  # Example default flavor ID


class DefaultClusterSettings(BaseSettings):
    kubernetes_version: str | None = "52be568f-5875-4c92-a6ba-07c06368a6fe"
    master_count: int = 3
    master_flavor_id: str = (
        "b003e1cf-fd40-4ad1-827c-cc20c2ddd519"  # Example default flavor ID
    )


APP_SETTINGS = AppSettings()
DEFAULT_CTX_SETTINGS = DefaultContextSettings()
