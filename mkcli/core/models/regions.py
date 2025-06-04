from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Region(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: Optional[datetime] | None = None
    updated_at: Optional[datetime] | None = None

    def as_table_row(self):
        return [
            self.id,
            self.name,
            "Yes" if self.is_active else "No",
            self.created_at.isoformat() if self.created_at else "N/A",
            self.updated_at.isoformat() if self.updated_at else "N/A",
        ]
