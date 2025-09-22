import httpx

from mkcli.core.models.node_pool import NodePool
from mkcli.core.models.backup import Backup
from mkcli.core.models.resource_usage import ResourceUsage

from mkcli.core.models import Cluster, Region
from .adapters import AuthProtocol


class APICallError(Exception):
    """Custom exception for API call errors."""

    def __init__(self, status_code: int, message: str):
        _msg = f"API call failed with status code {status_code}: {message}"
        self.code = status_code
        super().__init__(_msg)


class APIResponseFormattingError(Exception):
    """Custom exception for API response formatting errors."""

    ...


class MK8SClient:
    def __init__(self, auth: AuthProtocol, api_url: str):
        self._auth = auth
        self.api_url = api_url
        self.api = httpx.Client(base_url=self.api_url, headers=self.headers)

    @property
    def headers(self) -> dict:
        return {"accept": "application/json", **self._auth.get_auth_header()}

    @staticmethod
    def _verify(response: httpx.Response) -> None:
        """Verify the response from the API call."""
        if response.status_code // 100 != 2:
            raise APICallError(response.status_code, response.text)

    def get_clusters(
        self, organisation_id=None, order_by=None, region=None
    ) -> list[Cluster]:
        params = {
            "organisationId": organisation_id,
            "orderBy": order_by,
            "region": region,
        }
        resp = self.api.get("/cluster", headers=self.headers, params=params)
        self._verify(resp)
        return [Cluster.model_validate(item) for item in resp.json().get("items", [])]

    def create_cluster(self, cluster_data: dict | str, organisation_id=None) -> dict:
        params = {"organisationId": organisation_id}
        resp = self.api.post("/cluster", json=cluster_data, params=params)
        self._verify(resp)
        return resp.json()

    def get_cluster(self, cluster_id: str) -> Cluster:
        resp = self.api.get(f"cluster/{cluster_id}")
        self._verify(resp)
        _dict = resp.json()
        return Cluster.model_validate(_dict)

    def update_cluster(self, cluster_id: str, cluster_data: dict) -> dict:
        resp = self.api.put(f"/cluster/{cluster_id}", json=cluster_data)
        self._verify(resp)
        return resp.json()

    def delete_cluster(self, cluster_id: str) -> None:
        resp = self.api.delete(f"cluster/{cluster_id}")
        self._verify(resp)

    def refresh_kubeconfig(self, cluster_id: str) -> dict:
        resp = self.api.post(f"cluster/{cluster_id}/refresh-kubeconfig")
        self._verify(resp)
        return resp.json()

    def download_kubeconfig(self, cluster_id: str) -> str:
        resp = self.api.get(f"cluster/{cluster_id}/files", headers=self.headers)
        self._verify(resp)
        return resp.json()["kubeconfig"]

    def list_node_pools(self, cluster_id: str) -> list[NodePool]:
        resp = self.api.get(f"/cluster/{cluster_id}/node-pool")
        self._verify(resp)
        return [NodePool.model_validate(item) for item in resp.json().get("items", [])]

    def create_node_pool(self, cluster_id: str, node_pool_data: dict) -> dict:
        resp = self.api.post(f"/cluster/{cluster_id}/node-pool", json=node_pool_data)
        self._verify(resp)
        return resp.json()

    def get_node_pool(self, cluster_id: str, node_pool_id: str) -> NodePool:
        resp = self.api.get(f"/cluster/{cluster_id}/node-pool/{node_pool_id}")
        self._verify(resp)
        return NodePool.model_validate(resp.json())

    def update_node_pool(
        self, cluster_id: str, node_pool_id: str, node_pool_data: dict
    ) -> dict:
        resp = self.api.put(
            f"/cluster/{cluster_id}/node-pool/{node_pool_id}", json=node_pool_data
        )
        self._verify(resp)
        return resp.json()

    def delete_node_pool(self, cluster_id: str, node_pool_id: str) -> None:
        resp = self.api.delete(f"/cluster/{cluster_id}/node-pool/{node_pool_id}")
        self._verify(resp)

    def list_kubernetes_versions(self) -> list:  # TODO: add region filter
        resp = self.api.get("/kubernetes-version", headers=self.headers)
        self._verify(resp)
        return resp.json()["items"]

    def list_machine_specs(self, region_id: str | None) -> list:
        resp = self.api.get(f"/region/{region_id}/machine-spec", headers=self.headers)
        self._verify(resp)
        return resp.json()["items"]

    def list_regions(self) -> list[Region]:
        resp = self.api.get("/region", headers=self.headers)
        self._verify(resp)
        return [Region.model_validate(item) for item in resp.json().get("items", [])]

    def get_region(self, name) -> dict:
        params = {"name": name} if name else {}
        resp = self.api.get("/region", headers=self.headers, params=params)
        self._verify(resp)
        if not resp.json()["items"]:
            raise ValueError(f"Region '{name}' not found.")
        return resp.json()["items"].pop()

    def create_backup(self, cluster_id: str, backup_data: dict) -> Backup:
        """Create a new backup for a cluster"""
        resp = self.api.put(f"/cluster/{cluster_id}/backup", json=backup_data)
        self._verify(resp)
        return Backup.model_validate(resp.json())

    def get_backup(self, cluster_id: str, backup_id: str) -> Backup:
        """Get details of a specific backup"""
        resp = self.api.get(f"/cluster/{cluster_id}/backup/{backup_id}")
        self._verify(resp)
        return Backup.model_validate(resp.json())

    def list_backups(self, cluster_id: str) -> list[Backup]:
        """List all backups for a cluster"""
        resp = self.api.get(f"/cluster/{cluster_id}/backup")
        self._verify(resp)
        return [Backup.model_validate(item) for item in resp.json().get("items", [])]

    # Resource usage methods
    def get_resource_usage(self, cluster_id: str) -> list[ResourceUsage]:
        """Get resource usage statistics for a cluster"""
        resp = self.api.get(f"/cluster/{cluster_id}/resource-counts")
        self._verify(resp)
        return [
            ResourceUsage(name=key, usage_count=value)
            for key, value in resp.json().get("counts", {}).items()
        ]

    def __str__(self):
        return f"MK8SClient({self.api.base_url})"
