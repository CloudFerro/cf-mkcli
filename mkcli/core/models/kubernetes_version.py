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
        ..., description="Timestamp when the Kubernetes version was last updated"
    )
