import httpx
from mkcli.core.state import State
from mkcli.settings import APP_SETTINGS


class APICallError(Exception):
    """Custom exception for API call errors."""

    def __init__(self, status_code: int, message: str):
        _msg = f"API call failed with status code {status_code}: {message}"
        super().__init__(_msg)


class MK8SClient:
    _API_URL = APP_SETTINGS.mk8s_api_url

    def __init__(self, state: State):
        self.state = state
        self.api = httpx.Client(base_url=self._API_URL, headers=self.headers)

    @property
    def headers(self) -> dict:
        token = self.state.token
        return {
            "authorization": f"Bearer {token}",
        }

    @staticmethod
    def _verify(response: httpx.Response) -> None:
        """Verify the response from the API call."""
        if response.status_code != 200:
            raise APICallError(response.status_code, response.text)

    def get_clusters(self, organisation_id=None, order_by=None, region=None) -> list:
        params = {
            "organisationId": organisation_id,
            "orderBy": order_by,
            "region": region,
        }
        resp = self.api.get("/cluster", headers=self.headers, params=params)
        self._verify(resp)
        return resp.json()

    def create_cluster(self, cluster_data: dict | str, organisation_id=None) -> dict:
        params = {"organisationId": organisation_id}
        resp = self.api.post("/cluster", json=cluster_data, params=params)
        self._verify(resp)
        return resp.json()

    def get_cluster(self, cluster_id: str) -> dict:
        resp = self.api.get(f"cluster/{cluster_id}")
        self._verify(resp)
        return resp.json()

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

    def list_node_pools(self, cluster_id: str) -> dict:
        resp = self.api.get(f"/cluster/{cluster_id}/node-pool")
        self._verify(resp)
        return resp.json()

    def create_node_pool(self, cluster_id: str, node_pool_data: dict) -> dict:
        resp = self.api.post(f"/cluster/{cluster_id}/node-pool", json=node_pool_data)
        self._verify(resp)
        return resp.json()

    def get_node_pool(self, cluster_id: str, node_pool_id: str) -> dict:
        resp = self.api.get(f"/cluster/{cluster_id}/node-pool/{node_pool_id}")
        self._verify(resp)
        return resp.json()

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

    def list_kubernetes_versions(self) -> list:
        resp = self.api.get("/kubernetes-version", headers=self.headers)
        self._verify(resp)
        return resp.json()
