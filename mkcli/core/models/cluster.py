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


class ClusterPayload(RequestPayload):
    name: Optional[str] = names.generate()
    kubernetes_version: Optional[KubernetesVersion] = None
    control_plane: Optional[ControlPlane]
    node_pools: List[NodePool] = []
