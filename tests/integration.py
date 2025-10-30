import time
from typer.testing import CliRunner
from mkcli.main import cli
import json
from typing import Callable

ECHO: bool = True


def run_mkcli_cmd(args: list[str]):
    print(f"Calling: {' '.join(args)}")
    runner = CliRunner(echo_stdin=ECHO)
    result = runner.invoke(cli, args)
    return result


def test_mkcli(args: list[str], input=None, show_output: bool = False):
    print(f"Calling: {' '.join(args)}")
    runner = CliRunner(echo_stdin=ECHO)
    result = runner.invoke(cli, args, input=input)
    print("Exit code: ", result.exit_code)
    if show_output:
        print(result.output)
    assert result.exit_code == 0, result.exception
    return result


def wait_state(show_func: Callable, args: list[str], desired_state: str = "Running"):
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        result = show_func(args)

        obj_info = json.loads(result.output)
        current_state = obj_info.get("status")
        print(f"Current state: {current_state}, Desired state: {desired_state}")
        if current_state == desired_state:
            return True
        time.sleep(20)  # wait before retrying
        retry_count += 1
    raise Exception(
        f"Object did not reach state {desired_state} after {max_retries} retries."
    )


# auth

result = test_mkcli(["auth", "context", "list"], show_output=True)

# clusters
result = test_mkcli(["cluster", "list"])
result = test_mkcli(["cluster", "list", "--format", "json"])
# cluster create
# result = test_mkcli(["cluster", "create", "--master-count", "1", "--format", "json"], show_output=True)
# print(result)
# _id = json.loads(result.output)["id"]
# wait_state(run_mkcli_cmd, ["cluster", "show", _id, "--format", "json"], desired_state="Running")

cluster_id = "8a607d7c-e1e2-47a9-afad-fc84d96ed2b3"

test_mkcli(["cluster", "show", cluster_id])
test_mkcli(["cluster", "get-kubeconfig", cluster_id], show_output=True)

# nodepools
test_mkcli(["node-pool", "list", cluster_id])
result = test_mkcli(
    [
        "node-pool",
        "create",
        "--flavor",
        "hma.medium",
        "--node-count",
        "1",
        "--name",
        "integration-test",
        cluster_id,
        "--format",
        "json",
    ],
    show_output=True,
)
node_pool_id = json.loads(result.output)["id"]
wait_state(
    run_mkcli_cmd,
    ["node-pool", "show", cluster_id, node_pool_id, "--format", "json"],
    desired_state="Running",
)

try:
    result = test_mkcli(
        ["node-pool", "update", "--node-count", "2", cluster_id, node_pool_id]
    )
    wait_state(
        run_mkcli_cmd,
        ["node-pool", "show", cluster_id, node_pool_id, "--format", "json"],
        desired_state="Scaling",
    )
except Exception as err:
    print(err)
wait_state(
    run_mkcli_cmd,
    ["node-pool", "show", cluster_id, node_pool_id, "--format", "json"],
    desired_state="Running",
)

result = test_mkcli(["node-pool", "delete", cluster_id, node_pool_id, "-y"])
wait_state(
    run_mkcli_cmd,
    ["node-pool", "show", cluster_id, node_pool_id, "--format", "json"],
    desired_state="Deleting",
)

# flavors
result = test_mkcli(["flavors", "list"])
result = test_mkcli(["flavors", "list", "--format", "json"])
# regions
result = test_mkcli(["regions", "list"])
result = test_mkcli(["regions", "list", "--format", "json"])

# versions
result = test_mkcli(["kubernetes-version", "list"])
result = test_mkcli(["kubernetes-version", "list", "--format", "json"])


# resources
result = test_mkcli(["resource-usage", "show", cluster_id])
result = test_mkcli(["resource-usage", "show", cluster_id, "--format", "json"])

# backups
result = test_mkcli(["backup", "list", cluster_id])
