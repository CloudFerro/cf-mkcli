from enum import Enum, auto


class Format(str, Enum):
    TABLE = "table"
    JSON = "json"


class AuthType(Enum):
    JWT = auto()
    APP_CREDENTIAL = auto()


class SupportedRealms(str, Enum):
    CREODIAS = "Creodias-new"
    CF_CLOUD = "CloudFerro-Cloud"


class SupportedRegions(str, Enum):
    WAW4_1 = "WAW4-1"
    FRA1_2 = "FRA1-2"
