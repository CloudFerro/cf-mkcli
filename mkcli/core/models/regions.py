from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Region(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: Optional[datetime] | None = None
    updated_at: Optional[datetime] | None = None
