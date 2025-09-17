from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class ResourceUsage(BaseModel):
    """Model representing resource usage statistics for a cluster"""

    table_columns: ClassVar[list[str]] = [
        "Name",
        "Usage Count",
    ]

    # Instead of fixed fields, we'll use dynamic fields based on the response
    # The API returns a dictionary of resource types and their counts
    model_config = ConfigDict(extra="allow")

    name: str
    usage_count: int

    def as_table_row(self):
        return [self.name, self.usage_count]
