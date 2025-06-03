from datetime import datetime

from pydantic import BaseModel, Field


class MachineSpec(BaseModel):
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
