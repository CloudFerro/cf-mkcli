import typer
from pydantic_settings import BaseSettings
from pathlib import Path


class AppSettings(BaseSettings):
    name: str = "mkcli"
    state_file: Path = "contexts.json"
    # mk8s_api_url: str = "http://localhost:10000/api/v1"
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


APP_SETTINGS = AppSettings()
DEFAULT_CTX_SETTINGS = DefaultContextSettings()
