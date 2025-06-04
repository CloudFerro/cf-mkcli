from datetime import datetime

from pydantic import BaseModel, Field


class MachineSpec(BaseModel):  # Flavor
    id: str
    region_name: str
    name: str = Field(..., description="Name of the machine specification")

    cpu: int = Field(..., description="Number of CPU cores")
    memory: int = Field(..., description="Memory in MB")
    local_disc_size: int = Field(..., description="Disk size in GB")
    is_active: bool = Field(..., description="Is this machine spec active?")
    tags: list[str] = Field(
        default_factory=list,
        description="List of tags associated with the machine spec",
    )
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    def as_table_row(self):
        return [
            self.id,
            self.region_name,
            self.name,
            self.cpu,
            self.memory,
            self.local_disc_size,
            "Yes" if self.is_active else "No",
            ", ".join(self.tags) if self.tags else "None",
            self.created_at.isoformat(),
            self.updated_at.isoformat(),
        ]
