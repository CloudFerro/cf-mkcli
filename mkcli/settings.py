import typer
from pydantic_settings import BaseSettings
from pathlib import Path


class AppSettings(BaseSettings):
    name: str = "mkcli"
    state_file: Path = "config.json"
    # mk8s_api_url: str = "http://localhost:10000/api/v1"
    mk8s_api_url: str = "https://managed-kubernetes.creodias.eu/api/v1"

    @property
    def confing_path(self) -> Path:
        return Path(typer.get_app_dir(self.name)) / self.state_file


APP_SETTINGS = AppSettings()
