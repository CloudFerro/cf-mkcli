from datetime import datetime

from pydantic import BaseModel


class Region(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    is_active: bool
