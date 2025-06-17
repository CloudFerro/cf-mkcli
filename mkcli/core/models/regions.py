from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, field_serializer


class Region(BaseModel):
    table_columns: ClassVar[list[str]] = [
        "ID",
        "Name",
        "Is Active",
        "Created At",
        "Updated At",
    ]

    id: str
    name: str
    is_active: bool
    created_at: Optional[datetime] | None = None
    updated_at: Optional[datetime] | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    def as_table_row(self):
        return [
            self.id,
            self.name,
            "Yes" if self.is_active else "No",
            self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "N/A",
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "N/A",
        ]
