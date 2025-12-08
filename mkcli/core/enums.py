from enum import Enum


class Format(str, Enum):
    TABLE = "table"
    JSON = "json"


class AuthType(str, Enum):
    API_KEY = "api_key"
    OPENID = "openid"
