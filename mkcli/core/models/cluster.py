from pydantic import BaseModel, ConfigDict
from typing import List, Optional, ClassVar
from .base import BaseResourceModel
from .labels import Label, Taint
from .request import RequestPayload
from .machine_spec import MachineSpec, MachineSpecPayload
from .kubernetes_version import KubernetesVersion, KubernetesVersionPayload
from mkcli.settings import APP_SETTINGS


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


class Cluster(BaseResourceModel):
    table_columns: ClassVar[list[str]] = APP_SETTINGS.cluster_columns

    id: str
    name: str
    status: str
    phase: Optional[str]
    health: Optional[str]
    control_plane: ControlPlane
    version: KubernetesVersion
    metadata: dict | None = None
    is_active: bool | None = None
    errors: List[str] = []

    @property
    def flavor(self) -> str:
        if self.control_plane is None:
            return "N/A"
        if (
            self.control_plane.custom is None
            or self.control_plane.custom.machine_spec is None
        ):
            return "N/A"
        return self.control_plane.custom.machine_spec.name

    @property
    def kubernetes_version(self) -> str:
        if self.version is None:
            return "N/A"
        return self.version.version
