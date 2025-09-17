from typing import ClassVar, Optional

from .base import BaseResourceModel

# {
#  "enabled": true,
#  "schedule": "* * * * */5",
#  "ttl": "172800s",
#  "storage_endpoint": "https://s3.waw4-1.cloudferro.com",
#  "storage_access_key": "",
#  "storage_secret_key": ",
#  "storage_bucket": "",
#  "should_backup_volumes": false
# }


class Backup(BaseResourceModel):
    """Backup model representing a cluster backup"""

    table_columns: ClassVar[list[str]] = [
        "Enabled",
        "Schedule",
        "TTL",
        "Storage Endpoint",
        "Backup Volumes",
    ]

    enabled: bool
    schedule: str
    ttl: str
    storage_endpoint: Optional[str] = None
    storage_access_key: Optional[str] = None
    storage_secret_key: Optional[str] = None
    storage_bucket: Optional[str] = None
    should_backup_volumes: bool
