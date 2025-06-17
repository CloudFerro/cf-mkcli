from datetime import datetime

from pydantic import ConfigDict, field_serializer
from typing import List, Optional, ClassVar
from mkcli.utils import names
from mkcli.core.models import MachineSpec, MachineSpecPayload
from .labels import Label, Taint
from .request import RequestPayload


class NodePoolPayload(RequestPayload):
    name: Optional[str] = names.generate()
    quantity: int = 0

    size: int = 0
    size_min: int = 0
    size_max: int = 0

    machine_spec: Optional[MachineSpecPayload] = None

    autoscale: bool = False

    shared_networks: List[str] = []
    labels: List[Label] = []
    taints: List[Taint] = []

    model_config = ConfigDict(extra="allow")


class NodePool(NodePoolPayload):
    table_columns: ClassVar[List[str]] = [
        "ID",
        "Name",
        "Size",
        "Flavor",
        "Status",
        "Labels",
        "Taints",
    ]

    created_at: datetime
    updated_at: datetime
    status: str
    machine_spec: MachineSpec

    deleted_at: Optional[str] = None
    attach_external_ip: Optional[bool] = False
    autoheal: Optional[bool] = False
    errors: List[dict] = []

    model_config = ConfigDict(extra="allow")

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    def as_table_row(self):
        return [
            self.id,
            self.name,
            self.size,
            self.machine_spec.name if self.machine_spec else "N/A",
            self.status,
            "-"
            if not self.labels
            else ",\n".join(label.as_table_cell() for label in self.labels),
            "-"
            if not self.taints
            else ",\n".join(taint.as_table_cell() for taint in self.taints),
        ]
