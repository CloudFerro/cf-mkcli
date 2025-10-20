from enum import Enum


class Format(str, Enum):
    TABLE = "table"
    JSON = "json"


class AuthType(str, Enum):
    API_KEY = "api_key"
    OPENID = "openid"


class SupportedRealms(str, Enum):
    CREODIAS = "Creodias-new"
    CF_CLOUD = "CloudFerro-Cloud"


class SupportedRegions(str, Enum):
    WAW4_1 = "WAW4-1"
