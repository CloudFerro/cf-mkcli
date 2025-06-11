from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from mkcli.utils import names
from .request import RequestPayload


class ShortSpec(BaseModel):
    id: str


class NodePoolPayload(RequestPayload):
    name: Optional[str] = names.generate()

    quantity: int = 1
    size: int = 3
    size_min: int = Field(default=1, ge=1)
    size_max: int = Field(default=3, ge=2)

    machine_spec: ShortSpec

    autoscale: bool = False

    shared_networks: List[str] = []
    labels: List[dict] = []
    taints: List[dict] = []

    model_config = ConfigDict(extra="allow")
