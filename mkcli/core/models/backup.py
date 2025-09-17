from typing import ClassVar, List, Optional

from pydantic import ConfigDict

from .base import BaseResourceModel
from .request import RequestPayload


class BackupPayload(RequestPayload):
    """Payload for backup creation request"""

    name: str
    description: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_cli_args(cls, name: str, description: Optional[str] = None):
        """Create a backup payload from CLI arguments"""
        _payload = {
            "name": name,
            "description": description,
        }
        return cls(**_payload)


class Backup(BaseResourceModel):
    """Backup model representing a cluster backup"""

    table_columns: ClassVar[list[str]] = [
        "Id",
        "Name",
        "Description",
        "Status",
        "Size",
        "Created At",
        "Updated At",
    ]

    id: str
    name: str
    description: Optional[str] = None
    status: str
    size: Optional[int] = None
    cluster_id: str

    def as_table_row(self) -> List[str]:
        size_display = (
            f"{self.size / (1024 * 1024 * 1024):.2f} GB" if self.size else "N/A"
        )

        return [
            self.id,
            self.name,
            self.description or "-",
            self.status,
            size_display,
            self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
