import typer
from pydantic_settings import BaseSettings
from pathlib import Path


class AppSettings(BaseSettings):
    name: str = "mkcli"
    state_file: Path = "config.json"

    @property
    def confing_path(self) -> Path:
        return Path(typer.get_app_dir(self.name)) / self.state_file


APP_SETTINGS = AppSettings()
