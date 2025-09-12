from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List, Optional, ClassVar

from .labels import Label, Taint
from .request import RequestPayload
from .machine_spec import MachineSpec, MachineSpecPayload
from .kubernetes_version import KubernetesVersion, KubernetesVersionPayload


class ControlPlaneCustom(BaseModel):
    size: Optional[int] = 1
    machine_spec: MachineSpec


class ControlPlaneCustomPayload(BaseModel):
    size: Optional[int] = 1
    machine_spec: MachineSpecPayload


class ControlPlanePayload(BaseModel):
    custom: ControlPlaneCustomPayload
    preset: Optional[dict] = None


class ControlPlane(BaseModel):
    custom: ControlPlaneCustom
    preset: Optional[dict] = None


class NodePoolPayload(BaseModel):
    quantity: int
    machine_spec: MachineSpecPayload
    name: str
    size: int
    autoscale: Optional[bool] = False
    size_min: Optional[int] = 1
    size_max: Optional[int] = 1
    shared_networks: List[str] = []
    labels: List[Label] = []
    taints: List[Taint] = []


class ClusterPayload(RequestPayload):
    name: Optional[str]
    kubernetes_version: Optional[KubernetesVersionPayload] = None
    control_plane: Optional[ControlPlanePayload] = None
    node_pools: List[NodePoolPayload] = []

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_cli_args(
        cls,
        name: str,
        k8s_version_id: str,
        master_count: int,
        master_flavor: str,
    ):
        _payload = {
            "name": name or None,
            "kubernetes_version": {"id": k8s_version_id},
            "control_plane": {
                "custom": {
                    "size": master_count,
                    "machine_spec": {"id": master_flavor},
                }
            },
            "node_pools": [],
        }
        return cls(**_payload)


class Cluster(BaseModel):
    table_columns: ClassVar[list[str]] = [
        "ID",
        "Name",
        "Status",
        "Flavor",
        "Created At",
        "Updated At",
    ]

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    status: str
    control_plane: ControlPlane
    version: KubernetesVersion
    metadata: dict | None = None
    is_active: bool | None = None
    errors: List[str] = []

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    model_config = ConfigDict(extra="allow")

    def as_table_row(self) -> List[str]:
        return [
            self.id,
            self.name,
            self.status,
            self.control_plane.custom.machine_spec.name,
            self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]
