import json
from pydantic import BaseModel
from typing import List, Optional
from mkcli.utils import names


class KubernetesVersion(BaseModel):
    id: str


class MachineSpec(BaseModel):
    id: str


class ControlPlaneCustom(BaseModel):
    size: int
    machine_spec: MachineSpec


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
    machine_spec: MachineSpec
    name: str
    size: int
    size_min: int
    size_max: int
    autoscale: bool
    shared_networks: List[str]
    labels: List[Label]
    taints: List[Taint]


class ClusterPayload(BaseModel):
    name: Optional[str] = names.generate()
    kubernetes_version: Optional[KubernetesVersion] = None
    control_plane: Optional[ControlPlane]
    node_pools: List[NodePool] = []

    _raw_data: Optional[str] = None

    @classmethod
    def from_json(cls, data: str) -> "ClusterPayload":
        json_data = json.loads(data)
        obj = cls(**json_data, _raw_data=data)
        return obj

    @property
    def raw_data(self) -> str:
        if self._raw_data:
            return self._raw_data
        return json.dumps(self.dict(), indent=2)
