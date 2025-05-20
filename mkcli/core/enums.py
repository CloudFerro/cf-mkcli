from enum import Enum, auto


class Format(str, Enum):
    table = "table"
    json = "json"


class AuthType(Enum):
    JWT = auto()
    APP_CREDENTIAL = auto()
