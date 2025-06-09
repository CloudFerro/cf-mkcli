import datetime

from pydantic import BaseModel
from typing import List, Optional
from mkcli.utils import names
from .request import RequestPayload


class KubernetesVersion(BaseModel):
    id: str


class ShortSpec(BaseModel):
    id: str


class ControlPlaneCustom(BaseModel):
    size: int
    machine_spec: ShortSpec


class ControlPlane(BaseModel):
    preset: str | None = None
    custom: ControlPlaneCustom


class Label(BaseModel):
    key: str
    value: str


class Taint(BaseModel):
    key: str
    value: str
    effect: str


class NodePool(BaseModel):
    quantity: int
    machine_spec: ShortSpec
    name: str
    size: int
    size_min: int
    size_max: int
    autoscale: bool
    shared_networks: List[str]
    labels: List[Label]
    taints: List[Taint]


class Cluster(BaseModel):
    id: str
    name: str
    kubernetes_version: KubernetesVersion
    control_plane: ControlPlane
    node_pools: List[NodePool]
    region_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool = True

    @classmethod
    def from_request(cls, _data: dict):
        _data["kubernetes_version"] = KubernetesVersion(**_data["kubernetes_version"])
        _data["control_plane"] = ControlPlane(**_data["control_plane"])
        _data["node_pools"] = [NodePool(**np) for np in _data.get("node_pools", [])]
        return cls(**_data)

    def as_table_row(self):
        return [
            self.id,
            self.name,
            self.kubernetes_version.id,
            self.control_plane.preset or "Custom",
            len(self.node_pools),
            self.region_id,
            "Yes" if self.is_active else "No",
            self.created_at.isoformat(),
            self.updated_at.isoformat(),
        ]


class ClusterPayload(RequestPayload):
    name: Optional[str] = names.generate()
    kubernetes_version: Optional[KubernetesVersion] = None
    control_plane: Optional[ControlPlane]
    node_pools: List[NodePool] = []

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
