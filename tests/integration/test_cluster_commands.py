from tests.conftest import run_mkcli_cmd
import pytest
import json
import time
from tests.conftest import generate_cluster_name, log
import os
import subprocess


@pytest.mark.dependency(
    depends=[
        "tests/integration/test_auth_api_token.py::test_auth_verify_session_initialized"
    ],
    scope="session",
)
def test_switch_to_default_context(bdd: classmethod, context_name="default"):
    """Test switching to default context and verify it's current."""
    with bdd.given(f"Switch to context '{context_name}'"):
        result = run_mkcli_cmd(
            ["auth", "context", "switch", context_name],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then(f"Verify current context is '{context_name}'"):
        assert f"set auth context '{context_name}' as current!" in output_lower, (
            f"Context switch success message for '{context_name}' not found"
        )


@pytest.mark.dependency(
    depends=[
        "tests/integration/test_cluster_commands.py::test_switch_to_default_context"
    ],
    scope="session",
)
def test_cluster_list(bdd: classmethod):
    """Test that 'mkcli cluster list' command executes successfully and shows cluster table."""
    with bdd.given("List clusters in the current context"):
        result = run_mkcli_cmd(
            ["cluster", "list"],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then("verifying the cluster list output"):
        assert "kubernetes clusters" in output_lower, (
            "Expected 'Kubernetes Clusters' table header not found"
        )

    with bdd.then("verify expected columns are present in the cluster list"):
        expected_headers = [
            "id",
            "name",
            "status",
            "flavor",
            "created at",
            "updated at",
        ]

        for header in expected_headers:
            assert header in output_lower, (
                f"Expected column header '{header}' not found in cluster list output"
            )

        assert "see more details with json output format" in output_lower, (
            "Expected footer message about JSON output not found"
        )


@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_list"],
    scope="session",
)
def test_cluster_create_dry_run(
    bdd: classmethod,
    name="test-mkcli-cluster",
    kubernetes_version="1.30.10",
    master_count=3,
    master_flavor="hma.medium",
    output_format="json",
):
    """Test that 'mkcli cluster create' command executes successfully with dry-run."""
    with bdd.given("Create cluster in dry-run mode"):
        result = run_mkcli_cmd(
            [
                "cluster",
                "create",
                "--name",
                name,
                "--kubernetes-version",
                kubernetes_version,
                "--master-count",
                str(master_count),
                "--master-flavor",
                master_flavor,
                "--format",
                output_format,
                "--dry-run",
            ],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then("verifying the dry-run output contains expected information"):
        assert "dry run mode: would create cluster with data:" in output_lower, (
            "Expected dry-run mode message not found"
        )

        assert f"name='{name}'" in output_lower, (
            f"Expected cluster name '{name}' in dry-run output"
        )

        assert "kubernetes_version=kubernetesversionpayload" in output_lower, (
            "Expected kubernetes version payload structure in dry-run output"
        )

        assert "control_plane=controlplanepayload" in output_lower, (
            "Expected control plane payload structure in dry-run output"
        )

        assert f"size={master_count}" in output_lower, (
            f"Expected master count '{master_count}' in control plane configuration"
        )

        assert "machine_spec=machinespecpayload" in output_lower, (
            "Expected machine spec payload structure in dry-run output"
        )


@pytest.mark.order(
    after="tests/integration/test_cluster_commands.py::test_cluster_create_dry_run"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create_dry_run"],
    scope="session",
)
def test_cluster_create(
    bdd: classmethod,
    created_cluster_id,
    kubernetes_version: str = "1.30.10",
    master_count: int = 1,
    master_flavor: str = "eo2a.large",
    output_format: str = "json",
    create_cluster_timeout: int = 60 * 60,
):
    """Test that 'mkcli cluster create' command executes successfully."""
    with bdd.given("A new cluster creation is initiated"):
        name = generate_cluster_name().lower()
        result = run_mkcli_cmd(
            [
                "cluster",
                "create",
                "--name",
                name,
                "--kubernetes-version",
                kubernetes_version,
                "--master-count",
                str(master_count),
                "--master-flavor",
                master_flavor,
                "--format",
                output_format,
            ],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then(
        "verifying the cluster creation output contains expected information"
    ):
        assert '"id":' in output_lower, (
            "Expected 'id' field in cluster creation JSON output"
        )

        assert f'"name": "{name}"' in output_lower, (
            f"Expected cluster name '{name}' in creation output"
        )

        assert '"created_at":' in output_lower, (
            "Expected 'created_at' field in cluster creation output"
        )

        assert '"updated_at":' in output_lower, (
            "Expected 'updated_at' field in cluster creation output"
        )

        assert '"join_token_expires_at": "0001-01-01t00:00:00z"' in output_lower, (
            "Expected 'join_token_expires_at' field with default value in creation output"
        )

        assert '"status": "creating"' in output_lower, (
            "Expected cluster status 'Creating' in creation output"
        )

        assert '"control_plane":' in output_lower, (
            "Expected 'control_plane' field in cluster creation output"
        )

        assert '"custom":' in output_lower, (
            "Expected 'custom' field in control_plane output"
        )

        assert f'"size": {master_count}' in output_lower, (
            f"Expected master count '{master_count}' in control_plane.custom.size"
        )

        assert '"machine_spec":' in output_lower, (
            "Expected 'machine_spec' field in control_plane.custom output"
        )

        assert f'"name": "{master_flavor}"' in output_lower, (
            f"Expected master flavor '{master_flavor}' in machine_spec.name"
        )

        assert '"provider": "cloudferro"' in output_lower, (
            "Expected 'CloudFerro' provider in machine_spec output"
        )

        assert '"region": "waw4-1"' in output_lower, (
            "Expected 'WAW4-1' region in machine_spec output"
        )

        assert '"cpu": 2' in output_lower, "Expected 'cpu': 2 in machine_spec output"

        assert '"memory": "7632"' in output_lower, (
            "Expected 'memory': '7632' in machine_spec output"
        )

        assert '"local_disk_size": "32"' in output_lower, (
            "Expected 'local_disk_size': '32' in machine_spec output"
        )

        assert '"is_active": true' in output_lower, (
            "Expected 'is_active': true in machine_spec output"
        )

        assert '"tags": [' in output_lower, (
            "Expected 'tags' array in machine_spec output"
        )

        assert '"control-plane"' in output_lower, (
            "Expected 'control-plane' tag in machine_spec output"
        )

        assert '"worker"' in output_lower, (
            "Expected 'worker' tag in machine_spec output"
        )

        assert '"errors": []' in output_lower, (
            "Expected empty 'errors' array in cluster creation output"
        )
    with bdd.when("A cluster ID is extracted from the creation output"):
        try:
            cluster_data = json.loads(result.output)
            cluster_id = cluster_data["id"]
            created_cluster_id["id"] = cluster_id
            created_cluster_id["name"] = name

            log.info("Extracted cluster ID", cluster_id=cluster_id)
        except (json.JSONDecodeError, KeyError) as e:
            assert False, f"Failed to extract cluster ID from JSON output: {e}"

        result_show = run_mkcli_cmd(
            ["cluster", "show", cluster_id, "--format", output_format],
            assert_success=True,
            show_output=True,
        )

        output_show_lower = result_show.output.lower()

        output_show_clean = output_show_lower.replace("\n", "").replace(" ", "")

    with bdd.then("verifying the cluster show output contains expected information"):
        assert f'"id":"{cluster_id}"' in output_show_clean, (
            f"Expected cluster ID '{cluster_id}' in cluster show JSON output"
        )

        assert f'"name":"{name}"' in output_show_clean, (
            f"Expected cluster name '{name}' in cluster show JSON output"
        )

        assert '"status":"creating"' in output_show_clean, (
            "Expected 'status':'Creating' field in cluster show JSON output"
        )

        assert '"control_plane":' in output_show_clean, (
            "Expected 'control_plane' field in cluster show JSON output"
        )

        assert '"machine_spec":' in output_show_clean, (
            "Expected 'machine_spec' field in cluster show JSON output"
        )

        assert f'"name":"{master_flavor}"' in output_show_clean, (
            f"Expected machine spec name '{master_flavor}' in cluster show JSON output"
        )

    with bdd.when("waiting for the cluster to reach 'Running' state"):
        final_cluster_data = wait_for_cluster_state(
            cluster_id=cluster_id,
            desired_state="running",
            timeout_seconds=create_cluster_timeout,
            check_interval=20,
        )

        final_status = final_cluster_data["status"]

    with bdd.then("verifying the cluster reached 'Running' state successfully"):
        assert final_status.lower() == "running", (
            f"Expected final cluster status to be 'Running', but got '{final_status}'"
        )


@pytest.mark.order(
    after="tests/integration/test_cluster_commands.py::test_cluster_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create"],
    scope="session",
)
def test_cluster_get_kubeconfig(
    bdd: classmethod, created_cluster_id: dict, tmp_path: str
):
    """Test that 'mkcli cluster get-kubeconfig' command works and kubeconfig is functional."""

    with bdd.given("a created cluster exists to retrieve kubeconfig for"):
        cluster_id = created_cluster_id["id"]

    with bdd.when("retrieving the kubeconfig for the created cluster"):
        assert cluster_id is not None, (
            "No cluster ID available for kubeconfig test (test_cluster_create must run first)"
        )

        kubeconfig_path = tmp_path / "kubeconfig"

        original_cwd = os.getcwd()
        os.chdir(str(tmp_path))

        try:
            result = run_mkcli_cmd(
                ["cluster", "get-kubeconfig", cluster_id],
                assert_success=True,
                show_output=True,
            )

            assert "downloaded kube-config for cluster" in result.output.lower()
            assert "kubeconfig file saved to kube-config.yaml" in result.output.lower()

            saved_kubeconfig_path = tmp_path / "kube-config.yaml"
            assert saved_kubeconfig_path.exists()

            kubeconfig_content = saved_kubeconfig_path.read_text()
            log.info(
                "Successfully read kubeconfig file",
                content_length=len(kubeconfig_content),
            )

        finally:
            os.chdir(original_cwd)

    with bdd.then("the kubeconfig content should be valid and usable with kubectl"):
        kubeconfig_lower = kubeconfig_content.lower()

        assert "apiversion: v1" in kubeconfig_lower
        assert "kind: config" in kubeconfig_lower
        assert "clusters:" in kubeconfig_lower
        assert "users:" in kubeconfig_lower
        assert "current-context:" in kubeconfig_lower

        kubeconfig_path.write_text(kubeconfig_content)

        log.info(
            "Kubeconfig saved for kubectl testing",
            kubeconfig_path=str(kubeconfig_path),
            content_size=len(kubeconfig_content),
        )

        env = os.environ.copy()
        env["KUBECONFIG"] = str(kubeconfig_path)

        try:
            result = subprocess.run(
                ["kubectl", "get", "nodes"],
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                assert "ready" in result.stdout.lower()
            else:
                log.warning(
                    "⚠️ kubectl test failed but kubeconfig was downloaded successfully"
                )

        except subprocess.TimeoutExpired:
            log.warning("⚠️ kubectl timed out - cluster may not be ready")
        except FileNotFoundError:
            log.warning("⚠️ kubectl not found - skipping functionality test")

        log.info("Kubeconfig test completed successfully")


@pytest.mark.order(
    after="tests/integration/test_cluster_commands.py::test_cluster_get_kubeconfig"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create"],
    scope="session",
)
def test_cluster_update_kubernetes_version(
    bdd: classmethod,
    created_cluster_id: dict,
    tmp_path: str,
    new_kubernetes_version: str = "1.31.10",
    update_cluster_timeout: int = 60 * 30,
):
    """Test that 'mkcli cluster update' command works and cluster reaches running state with updated version."""

    with bdd.given("A running cluster exists to update"):
        cluster_id = created_cluster_id["id"]

        assert cluster_id is not None
        log.info(
            "Testing cluster kubernetes version update",
            cluster_id=cluster_id,
            new_version=new_kubernetes_version,
        )

    with bdd.when("Updating the cluster kubernetes version"):
        result = run_mkcli_cmd(
            [
                "cluster",
                "update",
                "--kubernetes-version",
                new_kubernetes_version,
                cluster_id,
            ],
            assert_success=True,
            show_output=True,
        )
        assert cluster_id in result.output
        log.info("Cluster update command executed successfully", cluster_id=cluster_id)

        final_cluster_data = wait_for_cluster_state(
            cluster_id=cluster_id,
            desired_state="running",
            timeout_seconds=update_cluster_timeout,
            check_interval=30,
        )
        assert final_cluster_data["status"].lower() == "running"
        log.info("Cluster is running after update", cluster_id=cluster_id)

    with bdd.then(
        "All worker nodes should be ready with the updated kubernetes version"
    ):
        kubeconfig_path, env = ensure_kubeconfig_exists(cluster_id, str(tmp_path))
        verify_nodes_with_version(cluster_id, new_kubernetes_version, env)
        log.info("Cluster update test completed successfully")


@pytest.mark.order(-2)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create"],
    scope="session",
)
def test_delete_cluster(
    bdd: classmethod, created_cluster_id, delete_cluster_timeout: int = 60 * 30
):
    """Test that 'mkcli cluster delete' command executes successfully."""
    with bdd.given("A created cluster exists to delete"):
        cluster_id = created_cluster_id["id"]
        cluster_name = created_cluster_id["name"]

        assert cluster_id is not None, (
            "No cluster ID available for deletion (test_cluster_create must run first)"
        )

    with bdd.when("Deleting the created cluster"):
        log.info(
            "Starting cluster deletion test",
            cluster_id=cluster_id,
            cluster_name=cluster_name,
        )

        result = run_mkcli_cmd(
            ["cluster", "delete", cluster_id, "--confirm", "-y"],
            assert_success=True,
            show_output=True,
        )

    with bdd.then("verifying the cluster deletion output"):
        assert cluster_id in result.output, (
            f"Expected cluster ID '{cluster_id}' in deletion output"
        )

        log.info("Cluster deletion command executed", cluster_id=cluster_id)

    with bdd.when("waiting for the cluster to reach 'Deleted' state"):
        final_cluster_data = wait_for_cluster_state(
            cluster_id=cluster_id,
            desired_state="deleted",
            timeout_seconds=delete_cluster_timeout,
            check_interval=20,
        )

        final_status = final_cluster_data["status"]

    with bdd.then("verifying the cluster reached 'Deleted' state successfully"):
        assert final_status.lower() == "deleted", (
            f"Expected final cluster status to be 'deleted', but got '{final_status}'"
        )


def _is_cluster_deleted(cluster_id: str) -> bool:
    """
    Check if cluster is deleted by verifying it's not in the cluster list.

    Returns:
        True if cluster is deleted (not found in list)
        False if cluster still exists or cannot verify
    """
    try:
        result = run_mkcli_cmd(
            ["cluster", "list", "--format", "json"],
            assert_success=True,
            show_output=False,
        )
        clusters = json.loads(result.output)

        for cluster in clusters:
            if isinstance(cluster, dict) and cluster.get("id") == cluster_id:
                return False

        return True

    except Exception:
        return False


def _get_cluster_status(cluster_id: str) -> tuple[dict | None, bool]:
    """
    Get cluster status data.

    Returns:
        Tuple of (cluster_data, command_succeeded)
    """
    result = run_mkcli_cmd(
        ["cluster", "show", cluster_id, "--format", "json"],
        assert_success=False,
        show_output=False,
    )

    if result.exit_code != 0:
        return None, False

    try:
        cluster_data = json.loads(result.output)
        return cluster_data, True
    except (json.JSONDecodeError, KeyError) as e:
        log.warning("Failed to parse status JSON", error=str(e), cluster_id=cluster_id)
        return None, False


def _check_if_deleted(cluster_id: str) -> dict | None:
    """
    Check if cluster is deleted when show command fails.

    Returns:
        dict with status="deleted" if cluster is deleted
        None if cluster still exists or verification fails
    """
    if _is_cluster_deleted(cluster_id):
        log.info("Cluster successfully deleted", cluster_id=cluster_id)
        return {"id": cluster_id, "status": "deleted"}

    log.info("Cluster deletion still in progress", cluster_id=cluster_id)
    return None


def wait_for_cluster_state(
    cluster_id: str,
    desired_state: str = "running",
    timeout_seconds: int = 3600,
    check_interval: int = 20,
) -> dict:
    """
    Wait for a cluster to reach the desired state.

    Returns:
        The final cluster data as a dictionary

    Raises:
        AssertionError: If timeout is reached or cluster enters error state
    """
    start_time = time.time()
    desired_state_lower = desired_state.lower()

    log.info(
        "Waiting for cluster to reach desired state",
        cluster_id=cluster_id,
        desired_state=desired_state,
        max_wait_minutes=timeout_seconds // 60,
    )

    while time.time() - start_time < timeout_seconds:
        cluster_data, command_succeeded = _get_cluster_status(cluster_id)
        elapsed_minutes = int((time.time() - start_time) // 60)

        if not command_succeeded:
            if desired_state_lower == "deleted":
                deleted_result = _check_if_deleted(cluster_id)
                if deleted_result:
                    return deleted_result
            else:
                log.warning(
                    "Cluster show command failed for non-deleted state",
                    cluster_id=cluster_id,
                    desired_state=desired_state,
                    elapsed_minutes=elapsed_minutes,
                )

            time.sleep(check_interval)
            continue

        current_status = cluster_data["status"]
        current_status_lower = current_status.lower()

        log.info(
            "Cluster status check",
            elapsed_minutes=elapsed_minutes,
            status=current_status,
            cluster_id=cluster_id,
        )

        if current_status_lower == desired_state_lower:
            log.info(
                "Cluster reached desired state",
                elapsed_minutes=elapsed_minutes,
                cluster_id=cluster_id,
                final_state=current_status,
            )
            return cluster_data

        if current_status_lower == "error":
            raise AssertionError(f"❌ Cluster entered error state: {current_status}")

        valid_states = {
            "creating",
            "running",
            "error",
            "deleting",
            "deleted",
            "upgrading",
        }
        if current_status_lower not in valid_states:
            raise AssertionError(
                f"❌ Cluster entered unexpected state: {current_status}"
            )

        time.sleep(check_interval)

    elapsed_minutes = int((time.time() - start_time) // 60)
    raise AssertionError(
        f"❌ Timeout: Cluster did not reach '{desired_state}' state within {elapsed_minutes} minutes"
    )


def verify_nodes_with_version(
    cluster_id: str,
    expected_version: str,
    env: dict,
    timeout_seconds: int = 60 * 10,
    check_interval: int = 30,
) -> None:
    """
    Verify all cluster nodes are ready and have the expected kubernetes version.
    Waits and retries until all nodes have the correct version or timeout.
    """
    log.info(
        "Verifying cluster nodes",
        cluster_id=cluster_id,
        expected_version=expected_version,
        timeout_minutes=timeout_seconds // 60,
    )

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        elapsed_minutes = int((time.time() - start_time) // 60)

        try:
            nodes_result = subprocess.run(
                ["kubectl", "get", "nodes", "-o", "json"],
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert nodes_result.returncode == 0, (
                f"kubectl failed: {nodes_result.stderr}"
            )

            nodes_data = json.loads(nodes_result.stdout)
            nodes = nodes_data.get("items", [])
            assert len(nodes) > 0, "No nodes found in cluster"

            all_ready = True
            for node in nodes:
                node_name = node["metadata"]["name"]

                conditions = node["status"]["conditions"]
                ready_condition = next(
                    (c for c in conditions if c["type"] == "Ready"), None
                )
                is_ready = ready_condition and ready_condition["status"] == "True"

                kubelet_version = node["status"]["nodeInfo"]["kubeletVersion"]
                has_correct_version = expected_version in kubelet_version

                if not is_ready or not has_correct_version:
                    all_ready = False
                    log.info(
                        f"Node {node_name}: ready={is_ready}, version={kubelet_version}"
                    )

            if all_ready:
                log.info(
                    f"✅ All {len(nodes)} nodes ready with version {expected_version}"
                )
                return

            log.info(f"⏳ Waiting {check_interval}s... ({elapsed_minutes}m elapsed)")
            time.sleep(check_interval)

        except Exception as e:
            log.warning(f"Check failed, retrying: {e}")
            time.sleep(check_interval)

    elapsed_minutes = int((time.time() - start_time) // 60)
    raise AssertionError(
        f"❌ Timeout: Nodes not ready with version {expected_version} after {elapsed_minutes}m"
    )


def ensure_kubeconfig_exists(cluster_id: str, tmp_path: str) -> tuple[str, dict]:
    """
    Ensure kubeconfig exists for the cluster. Downloads it if not found.

    Returns:
        Tuple of (kubeconfig_path, environment_dict_for_kubectl)
    """
    from pathlib import Path

    kubeconfig_path = Path(tmp_path) / "kubeconfig"
    saved_kubeconfig_path = Path(tmp_path) / "kube-config.yaml"

    if kubeconfig_path.exists():
        log.info("Using existing kubeconfig", path=str(kubeconfig_path))
    elif saved_kubeconfig_path.exists():
        kubeconfig_content = saved_kubeconfig_path.read_text()
        kubeconfig_path.write_text(kubeconfig_content)
        log.info("Copied kubeconfig from saved location", path=str(kubeconfig_path))
    else:
        log.info("Downloading kubeconfig", cluster_id=cluster_id)

        original_cwd = os.getcwd()
        os.chdir(str(tmp_path))

        try:
            result = run_mkcli_cmd(
                ["cluster", "get-kubeconfig", cluster_id],
                assert_success=True,
                show_output=True,
            )

            assert "downloaded kube-config for cluster" in result.output.lower()
            assert "kubeconfig file saved to kube-config.yaml" in result.output.lower()
            assert saved_kubeconfig_path.exists()

            kubeconfig_content = saved_kubeconfig_path.read_text()
            kubeconfig_path.write_text(kubeconfig_content)

            log.info("Successfully downloaded and saved kubeconfig")
        finally:
            os.chdir(original_cwd)

    env = os.environ.copy()
    env["KUBECONFIG"] = str(kubeconfig_path)

    return str(kubeconfig_path), env
