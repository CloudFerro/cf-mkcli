from enum import Enum

from pydantic_settings import BaseSettings

ENV_FILE_PATH = "config/.env"


class LogLevels(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppSettings(BaseSettings):
    log_level: LogLevels
    log_fmt_msg: str
    # log_path: str
    # log_retention_days: int
    # log_file_rotation_days: str  # ex. "1 day"
    # verify_certs: bool


app_settings = AppSettings()
