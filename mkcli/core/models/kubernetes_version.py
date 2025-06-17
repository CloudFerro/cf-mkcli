from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field, field_serializer


class KubernetesVersionPayload(BaseModel):
    id: str = Field(..., description="Unique identifier for the Kubernetes version")


class KubernetesVersion(KubernetesVersionPayload):
    table_columns: ClassVar[list[str]] = [
        "ID",
        "Version",
        "Is Active",
        "Created At",
        "Updated At",
    ]

    version: str = Field(..., description="Kubernetes version number")
    is_active: bool = Field(
        ..., description="Indicates if this Kubernetes version is currently active"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the Kubernetes version was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the Kubernetes version was last updated",
    )

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    def as_table_row(self):
        return [
            self.id,
            self.version,
            "Yes" if self.is_active else "No",
            self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]

    def as_json(self) -> dict[str, str | bool]:
        return {
            "id": self.id,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
