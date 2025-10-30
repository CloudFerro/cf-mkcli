from tests.conftest import run_mkcli_cmd
import pytest
import json
import time
from tests.conftest import log


@pytest.mark.order(
    after="tests/integration/test_cluster_commands.py::test_cluster_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create"],
    scope="session",
)
def test_node_pool_create_dry_run(
    bdd: classmethod,
    created_cluster_id,
    name: str = "test-mkcli_node-pool",
    flavor: str = "eo2a.large",
    node_count: int = 1,
    output_format: str = "json",
):
    """Test that 'mkcli node-pool create' command executes successfully with dry-run."""
    with bdd.given("Execute node-pool create command in dry-run mode"):
        cluster_id = created_cluster_id["id"]

        cmd = [
            "node-pool",
            "create",
            cluster_id,
            "--name",
            name,
            "--flavor",
            flavor,
            "--node-count",
            str(node_count),
            "--format",
            output_format,
            "--dry-run",
        ]

        result = run_mkcli_cmd(cmd, assert_success=True, show_output=True)

        output_lower = result.output.lower()

    with bdd.then("verifying the dry-run output contains expected information"):
        assert "dry run mode:" in output_lower, (
            "Expected dry-run mode message not found"
        )

        assert f'"name": "{name}"' in output_lower, (
            f"Expected node pool name '{name}' in dry-run output"
        )

        assert f'"size": {node_count}' in output_lower, (
            f"Expected node count '{node_count}' in dry-run output"
        )

        assert '"machine_spec":' in output_lower, (
            "Expected machine_spec field in dry-run output"
        )

        assert '"id":' in output_lower, (
            "Expected machine_spec.id field in dry-run output"
        )

        assert '"autoscale": false' in output_lower, (
            "Expected autoscale field in dry-run output"
        )

        assert '"shared_networks": []' in output_lower, (
            "Expected shared_networks array in dry-run output"
        )

        assert '"labels": []' in output_lower, "Expected labels array in dry-run output"

        assert '"taints": []' in output_lower, "Expected taints array in dry-run output"

        log.info(
            "Node pool dry-run test completed successfully",
            cluster_id=cluster_id,
            name=name,
        )


@pytest.mark.order(
    after="tests/integration/test_cluster_commands.py::test_cluster_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_cluster_commands.py::test_cluster_create"],
    scope="session",
)
def test_node_pool_create(
    bdd: classmethod,
    created_cluster_id,
    created_node_pool_id,
    name: str = "test-mkcli_node-pool",
    flavor: str = "eo2a.large",
    node_count: int = 1,
    output_format: str = "json",
    create_node_pool_timeout: int = 60 * 30,
):
    """Test that 'mkcli node-pool create' command executes successfully."""
    with bdd.given("Execute node-pool create command"):
        cluster_id = created_cluster_id["id"]

        cmd = [
            "node-pool",
            "create",
            cluster_id,
            "--name",
            name,
            "--flavor",
            flavor,
            "--node-count",
            str(node_count),
            "--format",
            output_format,
        ]

        result = run_mkcli_cmd(cmd, assert_success=True, show_output=True)

        output_lower = result.output.lower()

    with bdd.when(
        "verifying the node pool creation output contains expected information"
    ):
        assert '"id":' in output_lower, (
            "Expected 'id' field in node pool creation JSON output"
        )

        assert f'"name": "{name}"' in output_lower, (
            f"Expected node pool name '{name}' in creation output"
        )

        assert '"created_at":' in output_lower, (
            "Expected 'created_at' field in node pool creation output"
        )

        assert '"updated_at":' in output_lower, (
            "Expected 'updated_at' field in node pool creation output"
        )

        assert '"status":' in output_lower, (
            "Expected 'status' field in node pool creation output"
        )

        assert f'"size": {node_count}' in output_lower, (
            f"Expected node count '{node_count}' in creation output"
        )

        assert '"machine_spec":' in output_lower, (
            "Expected 'machine_spec' field in node pool creation output"
        )

        assert f'"name": "{flavor}"' in output_lower, (
            f"Expected flavor '{flavor}' in machine_spec.name"
        )

    with bdd.then("extracting node pool ID from creation output"):
        try:
            node_pool_data = json.loads(result.output)
            node_pool_id = node_pool_data["id"]
            created_node_pool_id["id"] = node_pool_id
            created_node_pool_id["name"] = name
            created_node_pool_id["cluster_id"] = cluster_id

            log.info(
                "Extracted node pool ID",
                node_pool_id=node_pool_id,
                cluster_id=cluster_id,
            )
        except (json.JSONDecodeError, KeyError) as e:
            assert False, f"Failed to extract node pool ID from JSON output: {e}"

    with bdd.then("verifying the node pool reaches 'Running' state"):
        result_show = run_mkcli_cmd(
            ["node-pool", "show", cluster_id, node_pool_id, "--format", output_format],
            assert_success=True,
            show_output=True,
        )

        output_show_lower = result_show.output.lower()
        output_show_clean = output_show_lower.replace("\n", "").replace(" ", "")

        assert f'"id":"{node_pool_id}"' in output_show_clean, (
            f"Expected node pool ID '{node_pool_id}' in node pool show JSON output"
        )

        assert f'"name":"{name}"' in output_show_clean, (
            f"Expected node pool name '{name}' in node pool show JSON output"
        )

        final_node_pool_data = wait_for_node_pool_state(
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
            desired_state="running",
            timeout_seconds=create_node_pool_timeout,
            check_interval=20,
        )

        final_status = final_node_pool_data["status"]

        assert final_status.lower() == "running", (
            f"Expected final node pool status to be 'Running', but got '{final_status}'"
        )


@pytest.mark.order(
    after="tests/integration/test_node_pool_commands.py::test_node_pool_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_node_pool_commands.py::test_node_pool_create"],
    scope="session",
)
def test_node_pool_list(bdd: classmethod, created_cluster_id, created_node_pool_id):
    """Test that 'mkcli node-pool list' command executes successfully and returns proper JSON."""
    cluster_id = created_cluster_id["id"]
    node_pool_id = created_node_pool_id["id"]
    node_pool_name = created_node_pool_id["name"]
    result = run_mkcli_cmd(
        ["node-pool", "list", cluster_id, "--format", "json"],
        assert_success=True,
        show_output=True,
    )
    with bdd.given("Execute node-pool list command"):
        try:
            list_data = json.loads(result.output)
        except json.JSONDecodeError as e:
            assert False, f"Failed to parse node pool list JSON output: {e}"

        assert "node-pools" in list_data, "Expected 'node-pools' key in JSON output"

        node_pools = list_data["node-pools"]
        assert isinstance(node_pools, list), "Expected 'node-pools' to be an array"
        assert len(node_pools) > 0, "Expected at least one node pool in the list"

        found_node_pool = None
        for node_pool in node_pools:
            if node_pool.get("id") == node_pool_id:
                found_node_pool = node_pool
                break

    with bdd.then("verifying the created node pool is in the list with correct fields"):
        assert found_node_pool is not None, (
            f"Created node pool '{node_pool_id}' not found in node pool list"
        )

        required_fields = [
            "id",
            "name",
            "status",
            "created_at",
            "updated_at",
            "machine_spec",
            "autoscale",
            "size",
            "quantity",
        ]

        for field in required_fields:
            assert field in found_node_pool, (
                f"Expected field '{field}' not found in node pool list item"
            )

        assert found_node_pool["id"] == node_pool_id, (
            f"Node pool ID mismatch: expected '{node_pool_id}', got '{found_node_pool['id']}'"
        )

        assert found_node_pool["name"] == node_pool_name, (
            f"Node pool name mismatch: expected '{node_pool_name}', got '{found_node_pool['name']}'"
        )

        machine_spec = found_node_pool.get("machine_spec", {})
        assert isinstance(machine_spec, dict), "Expected machine_spec to be an object"

        machine_spec_fields = ["id", "name", "cpu", "memory", "region_name"]
        for field in machine_spec_fields:
            assert field in machine_spec, f"Expected field '{field}' in machine_spec"


@pytest.mark.order(
    after="tests/integration/test_node_pool_commands.py::test_node_pool_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_node_pool_commands.py::test_node_pool_create"],
    scope="session",
)
def test_node_pool_show(
    bdd: classmethod, created_node_pool_id, output_format: str = "json"
):
    """Test that 'mkcli node-pool show' command executes successfully."""
    with bdd.given("Execute node-pool show command"):
        cluster_id = created_node_pool_id["cluster_id"]
        node_pool_id = created_node_pool_id["id"]
        node_pool_name = created_node_pool_id["name"]

        result = run_mkcli_cmd(
            ["node-pool", "show", cluster_id, node_pool_id, "--format", output_format],
            assert_success=True,
            show_output=True,
        )

        output_lower = result.output.lower()

    with bdd.then("verifying the node pool show output contains expected information"):
        assert '"id":' in output_lower, "Expected 'id' field in node pool show output"

        assert f'"id": "{node_pool_id}"' in output_lower, (
            f"Expected node pool ID '{node_pool_id}' to be present in show output"
        )

        assert f'"name": "{node_pool_name}"' in output_lower, (
            f"Expected node pool name '{node_pool_name}' in show output"
        )

        assert '"status":' in output_lower, (
            "Expected 'status' field in node pool show output"
        )

        assert '"machine_spec":' in output_lower, (
            "Expected 'machine_spec' field in node pool show output"
        )

        assert '"created_at":' in output_lower, (
            "Expected 'created_at' field in node pool show output"
        )

        assert '"updated_at":' in output_lower, (
            "Expected 'updated_at' field in node pool show output"
        )

        assert '"size":' in output_lower, (
            "Expected 'size' field in node pool show output"
        )

        node_pool_data = json.loads(result.output)

        assert node_pool_data.get("id") == node_pool_id, (
            f"Node pool ID in JSON ({node_pool_data.get('id')}) doesn't match expected ({node_pool_id})"
        )

        assert node_pool_data.get("name") == node_pool_name, (
            f"Node pool name in JSON ({node_pool_data.get('name')}) doesn't match expected ({node_pool_name})"
        )


@pytest.mark.order(
    after="tests/integration/test_node_pool_commands.py::test_node_pool_create"
)
@pytest.mark.dependency(
    depends=["tests/integration/test_node_pool_commands.py::test_node_pool_create"],
    scope="session",
)
def test_node_pool_update_scaling(
    bdd: classmethod,
    created_node_pool_id,
    update_node_pool_timeout: int = 60 * 15,
):
    """Test that 'mkcli node-pool update' command executes successfully with autoscaling."""
    with bdd.given("Execute node-pool update command to enable autoscaling"):
        cluster_id = created_node_pool_id["cluster_id"]
        node_pool_id = created_node_pool_id["id"]
        node_pool_name = created_node_pool_id["name"]

        log.info(
            "Starting node pool update test",
            node_pool_id=node_pool_id,
            cluster_id=cluster_id,
            node_pool_name=node_pool_name,
        )

        cmd = [
            "node-pool",
            "update",
            cluster_id,
            node_pool_id,
            "--autoscale",
            "--min-nodes",
            "1",
            "--max-nodes",
            "2",
        ]

        result = run_mkcli_cmd(cmd, assert_success=True, show_output=True)

        output_lower = result.output.lower()

    with bdd.when(
        "verifying the node pool update output contains expected information"
    ):
        assert '"id":' in output_lower, (
            "Expected 'id' field in node pool update JSON output"
        )

        assert f'"id": "{node_pool_id}"' in output_lower, (
            f"Expected node pool ID '{node_pool_id}' in update output"
        )

        assert f'"name": "{node_pool_name}"' in output_lower, (
            f"Expected node pool name '{node_pool_name}' in update output"
        )

        assert '"autoscale": true' in output_lower, (
            "Expected autoscale to be enabled in update output"
        )

        assert '"size_min": 1' in output_lower, (
            "Expected minimum node count of 1 in update output"
        )

        assert '"size_max": 2' in output_lower, (
            "Expected maximum node count of 2 in update output"
        )

        assert '"status":' in output_lower, (
            "Expected 'status' field in node pool update output"
        )

    with bdd.then("parsing node pool update output and verifying scaling status"):
        try:
            output_lines = result.output.split("\n")

            json_start_index = None
            for i, line in enumerate(output_lines):
                if "Node Pool updated:" in line and i + 1 < len(output_lines):
                    json_start_index = i + 1
                    break

            second_json_lines = output_lines[json_start_index:]
            second_json_text = "\n".join(second_json_lines).strip()
            update_data = json.loads(second_json_text)

            initial_status = update_data["status"]

            log.info(
                "Node pool update command executed",
                node_pool_id=node_pool_id,
                cluster_id=cluster_id,
                initial_status=initial_status,
            )

            assert initial_status.lower() == "scaling", (
                f"Expected initial status to be 'Scaling' after update, but got '{initial_status}'"
            )

            assert update_data.get("id") == node_pool_id, (
                f"Expected node pool ID '{node_pool_id}' in parsed JSON, got '{update_data.get('id')}'"
            )

            assert update_data.get("autoscale") is True, (
                f"Expected autoscale to be True in parsed JSON, got '{update_data.get('autoscale')}'"
            )

            assert update_data.get("size_min") == 1, (
                f"Expected size_min to be 1 in parsed JSON, got '{update_data.get('size_min')}'"
            )

            assert update_data.get("size_max") == 2, (
                f"Expected size_max to be 2 in parsed JSON, got '{update_data.get('size_max')}'"
            )

        except (json.JSONDecodeError, KeyError) as e:
            assert False, f"Failed to parse node pool update JSON output: {e}"

    with bdd.then("verifying the node pool reaches 'Running' state after scaling"):
        final_node_pool_data = wait_for_node_pool_state(
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
            desired_state="running",
            timeout_seconds=update_node_pool_timeout,
            check_interval=20,
        )

        final_status = final_node_pool_data["status"]

        assert final_status.lower() == "running", (
            f"Expected final node pool status to be 'Running' after scaling, but got '{final_status}'"
        )

        final_autoscale = final_node_pool_data.get("autoscale", False)
        final_size_min = final_node_pool_data.get("size_min", 0)
        final_size_max = final_node_pool_data.get("size_max", 0)

        assert final_autoscale is True, (
            f"Expected autoscale to remain enabled, but got '{final_autoscale}'"
        )

        assert final_size_min == 1, (
            f"Expected size_min to be 1, but got '{final_size_min}'"
        )

        assert final_size_max == 2, (
            f"Expected size_max to be 2, but got '{final_size_max}'"
        )


@pytest.mark.order(
    after="tests/integration/test_node_pool_commands.py::test_node_pool_update_scaling"
)
@pytest.mark.dependency(
    depends=[
        "tests/integration/test_node_pool_commands.py::test_node_pool_update_scaling"
    ],
    scope="session",
)
def test_delete_node_pool(
    bdd: classmethod, created_node_pool_id, delete_node_pool_timeout: int = 60 * 15
):
    """Test that 'mkcli node-pool delete' command executes successfully."""
    with bdd.given("Execute node-pool delete command"):
        cluster_id = created_node_pool_id["cluster_id"]
        node_pool_id = created_node_pool_id["id"]
        node_pool_name = created_node_pool_id["name"]

        assert node_pool_id is not None, (
            "No node pool ID available for deletion (test_node_pool_create must run first)"
        )

        log.info(
            "Starting node pool deletion test",
            node_pool_id=node_pool_id,
            cluster_id=cluster_id,
            node_pool_name=node_pool_name,
        )

        result = run_mkcli_cmd(
            ["node-pool", "delete", cluster_id, node_pool_id, "--confirm", "-y"],
            assert_success=True,
            show_output=True,
        )

    with bdd.when(
        "verifying the node pool deletion output contains expected information"
    ):
        assert node_pool_id in result.output, (
            f"Expected node pool ID '{node_pool_id}' in deletion output"
        )

        log.info(
            "Node pool deletion command executed",
            node_pool_id=node_pool_id,
            cluster_id=cluster_id,
        )

    with bdd.then("verifying the node pool reaches 'Deleted' state"):
        final_node_pool_data = wait_for_node_pool_state(
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
            desired_state="deleted",
            timeout_seconds=delete_node_pool_timeout,
            check_interval=20,
        )

        final_status = final_node_pool_data["status"]

        assert final_status.lower() == "deleted", (
            f"Expected final node pool status to be 'deleted', but got '{final_status}'"
        )


def _is_node_pool_deleted(cluster_id: str, node_pool_id: str) -> bool:
    """
    Check if node pool is deleted by verifying it's not in the node pool list.

    Returns:
        True if node pool is deleted (not found in list)
        False if node pool still exists or cannot verify
    """
    try:
        result = run_mkcli_cmd(
            ["node-pool", "list", cluster_id, "--format", "json"],
            assert_success=True,
            show_output=False,
        )
        node_pools = json.loads(result.output)

        for node_pool in node_pools:
            if isinstance(node_pool, dict) and node_pool.get("id") == node_pool_id:
                return False

        return True

    except Exception:
        return False


def _get_node_pool_status(
    cluster_id: str, node_pool_id: str
) -> tuple[dict | None, bool]:
    """
    Get node pool status data.
    """
    result = run_mkcli_cmd(
        ["node-pool", "show", cluster_id, node_pool_id, "--format", "json"],
        assert_success=False,
        show_output=False,
    )

    if result.exit_code != 0:
        return None, False

    try:
        node_pool_data = json.loads(result.output)
        return node_pool_data, True
    except (json.JSONDecodeError, KeyError) as e:
        log.warning(
            "Failed to parse node pool status JSON",
            error=str(e),
            node_pool_id=node_pool_id,
        )
        return None, False


def _check_if_node_pool_deleted(cluster_id: str, node_pool_id: str) -> dict | None:
    """
    Check if node pool is deleted when show command fails.

    Returns:
        dict with status="deleted" if node pool is deleted
        None if node pool still exists or verification fails
    """
    if _is_node_pool_deleted(cluster_id, node_pool_id):
        log.info(
            "Node pool successfully deleted",
            node_pool_id=node_pool_id,
            cluster_id=cluster_id,
        )
        return {"id": node_pool_id, "status": "deleted"}

    log.info(
        "Node pool deletion still in progress",
        node_pool_id=node_pool_id,
        cluster_id=cluster_id,
    )
    return None


def wait_for_node_pool_state(
    cluster_id: str,
    node_pool_id: str,
    desired_state: str = "running",
    timeout_seconds: int = 30 * 60,
    check_interval: int = 20,
) -> dict:
    """
    Wait for a node pool to reach the desired state.
    """
    start_time = time.time()
    desired_state_lower = desired_state.lower()

    log.info(
        "Waiting for node pool to reach desired state",
        cluster_id=cluster_id,
        node_pool_id=node_pool_id,
        desired_state=desired_state,
        max_wait_minutes=timeout_seconds // 60,
    )

    while time.time() - start_time < timeout_seconds:
        node_pool_data, command_succeeded = _get_node_pool_status(
            cluster_id, node_pool_id
        )
        elapsed_minutes = int((time.time() - start_time) // 60)

        if not command_succeeded:
            if desired_state_lower == "deleted":
                deleted_result = _check_if_node_pool_deleted(cluster_id, node_pool_id)
                if deleted_result:
                    return deleted_result
            else:
                log.warning(
                    "Node pool show command failed for non-deleted state",
                    cluster_id=cluster_id,
                    node_pool_id=node_pool_id,
                    desired_state=desired_state,
                    elapsed_minutes=elapsed_minutes,
                )

            time.sleep(check_interval)
            continue

        current_status = node_pool_data["status"]
        current_status_lower = current_status.lower()

        log.info(
            "Node pool status check",
            elapsed_minutes=elapsed_minutes,
            status=current_status,
            cluster_id=cluster_id,
            node_pool_id=node_pool_id,
        )

        if current_status_lower == desired_state_lower:
            log.info(
                "Node pool reached desired state",
                elapsed_minutes=elapsed_minutes,
                cluster_id=cluster_id,
                node_pool_id=node_pool_id,
                final_state=current_status,
            )
            return node_pool_data

        if current_status_lower == "error":
            raise AssertionError(f"❌ Node pool entered error state: {current_status}")

        valid_states = {
            "creating",
            "running",
            "scaling",
            "deleting",
            "upgrading",
        }
        if current_status_lower not in valid_states:
            raise AssertionError(
                f"❌ Node pool entered unexpected state: {current_status}"
            )

        time.sleep(check_interval)

    elapsed_minutes = int((time.time() - start_time) // 60)
    raise AssertionError(
        f"❌ Timeout: Node pool did not reach '{desired_state}' state within {elapsed_minutes} minutes"
    )
