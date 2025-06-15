from mkcli.core.mk8s import MK8SClient
from typing import Dict
from mkcli.core.models import MachineSpec, KubernetesVersion, Region
from mkcli.utils.cache import cache

type seconds = int


type KubernetesVersionMapping = Dict[str, KubernetesVersion]
type RegionNameIdMapping = Dict[str, Region]
type MachineSpecMapping = Dict[str, MachineSpec]


CACHE_TTL: seconds = 3600


@cache(ttl=CACHE_TTL)
def get_kubernetes_versions_mapping(client: MK8SClient) -> KubernetesVersionMapping:
    versions = client.list_kubernetes_versions()
    return {
        v["version"]: KubernetesVersion(
            id=v["id"],
            version=v["version"],
            created_at=v["created_at"],
            updated_at=v["updated_at"],
            is_active=v["is_active"],
        )
        for v in versions
    }


@cache(CACHE_TTL)
def get_regions_mapping(client: MK8SClient) -> RegionNameIdMapping:
    regions = client.list_regions()
    return {
        region["name"]: Region(
            name=region["name"], id=region["id"], is_active=region["is_active"]
        )
        for region in regions
    }


@cache(CACHE_TTL)
def get_machine_spec_mapping(client: MK8SClient, region_id: str) -> MachineSpecMapping:
    machine_specs = client.list_machine_specs(region_id)
    return {
        machine["name"]: MachineSpec(
            id=machine["id"],
            region=machine["region"],
            name=machine["name"],
            cpu=machine["cpu"],
            memory=machine["memory"],
            local_disk_size=machine["local_disk_size"],
            is_active=machine["is_active"],
            tags=machine.get("tags", []),
            created_at=machine["created_at"],
            updated_at=machine["updated_at"],
        )
        for machine in machine_specs
    }
