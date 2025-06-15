from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class MachineSpecPayload(BaseModel):
    id: str = Field(..., description="Unique identifier for the machine spec")


class MachineSpec(MachineSpecPayload):  # Flavor
    region_name: str = Field(
        alias="region", description="Region where the machine spec is available"
    )
    name: str = Field(..., description="Name of the machine specification")

    cpu: int = Field(..., description="Number of CPU cores")
    memory: int = Field(..., description="Memory in MB")
    local_disk_size: int = Field(..., description="Disk size in GB")
    is_active: bool = Field(..., description="Is this machine spec active?")
    tags: list[str] = Field(
        default_factory=list,
        description="List of tags associated with the machine spec",
    )
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    def as_table_row(self):
        return [
            self.id,
            self.region_name,
            self.name,
            self.cpu,
            self.memory,
            self.local_disk_size,
            "Yes" if self.is_active else "No",
            ", ".join(self.tags) if self.tags else "None",
            self.created_at.isoformat(),
            self.updated_at.isoformat(),
        ]

    def as_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "region_name": self.region_name,
            "name": self.name,
            "cpu": self.cpu,
            "memory": self.memory,
            "local_disk_size": self.local_disk_size,
            "is_active": self.is_active,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
