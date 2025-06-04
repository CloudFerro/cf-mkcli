from enum import Enum, auto


class Format(str, Enum):
    TABLE = "table"
    JSON = "json"


class AuthType(Enum):
    JWT = auto()
    APP_CREDENTIAL = auto()
