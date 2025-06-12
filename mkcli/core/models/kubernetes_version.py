from datetime import datetime

from pydantic import BaseModel, Field


class KubernetesVersion(BaseModel):
    id: str = Field(..., description="Unique identifier for the Kubernetes version")
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

    def as_table_row(self):
        return [
            self.id,
            self.version,
            self.created_at.isoformat(),
            self.updated_at.isoformat(),
            "Yes" if self.is_active else "No",
        ]

    def as_json(self) -> dict[str, str | bool]:
        return {
            "id": self.id,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
