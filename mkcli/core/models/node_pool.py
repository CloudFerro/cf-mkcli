from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List, Optional
from mkcli.utils import names
from .request import RequestPayload


class ShortSpec(BaseModel):
    id: str


class NodePoolPayload(RequestPayload):
    name: Optional[str] = names.generate()
    quantity: int = 0

    size: int = 0
    size_min: int = 0
    size_max: int = 0

    machine_spec: Optional[ShortSpec] = None

    autoscale: bool = False

    shared_networks: List[str] = []
    labels: List[dict] = []
    taints: List[dict] = []

    model_config = ConfigDict(extra="allow")


class NodePool(NodePoolPayload):
    created_at: datetime
    updated_at: datetime
    status: str

    deleted_at: Optional[str] = None
    attach_external_ip: Optional[bool] = False
    autoheal: Optional[bool] = False

    errors: List[dict] = []

    model_config = ConfigDict(extra="allow")

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"
