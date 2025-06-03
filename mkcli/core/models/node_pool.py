from pydantic import BaseModel
from typing import List, Optional
from mkcli.utils import names
from .request import RequestPayload


class ShortSpec(BaseModel):
    id: str


class NodePoolPayload(RequestPayload):
    name: Optional[str] = names.generate()

    size: int = 3
    machine_spec: ShortSpec

    autoscale: bool = False

    shared_networks: List[str] = []
    labels: List[str] = []
    taints: List[str] = []
