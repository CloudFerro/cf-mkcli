# CLI

mkcli - A CLI for managing your Kubernetes clusters

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `auth`: Cli auth management
* `cluster`: Manage Kubernetes clusters
* `node-pool`: Nodepool operations

## `auth`

Cli auth management

**Usage**:

```console
$ auth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `token`: Cli token management
* `context`: Cli auth context management

### `auth token`

Cli token management

**Usage**:

```console
$ auth token [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clear`
* `refresh`
* `show`

#### `auth token clear`

**Usage**:

```console
$ auth token clear [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth token refresh`

**Usage**:

```console
$ auth token refresh [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth token show`

**Usage**:

```console
$ auth token show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth context`

Cli auth context management

**Usage**:

```console
$ auth context [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `show`: Show current auth context
* `list`: Remove given auth context from the catalogue
* `add`: Prompt for new auth context and add it to...
* `delete`: Remove given auth context from the catalogue

#### `auth context show`

Show current auth context

**Usage**:

```console
$ auth context show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth context list`

Remove given auth context from the catalogue

**Usage**:

```console
$ auth context list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth context add`

Prompt for new auth context and add it to the catalogue

**Usage**:

```console
$ auth context add [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth context delete`

Remove given auth context from the catalogue

**Usage**:

```console
$ auth context delete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `cluster`

Manage Kubernetes clusters

**Usage**:

```console
$ cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new k8s cluster
* `update`: Update the cluster with given id
* `delete`: Delete the cluster with given id
* `list`: List all clusters
* `show`: Show cluster details
* `get-kubeconfig`: Download kube-config.yaml

### `cluster create`

Create a new k8s cluster

**Usage**:

```console
$ cluster create [OPTIONS]
```

**Options**:

* `--name TEXT`: Cluster name, if None, generate with petname
* `--kubernetes-version TEXT`: Kubernetes version ID, if None, use default  [default: 52be568f-5875-4c92-a6ba-07c06368a6fe]
* `--master-count INTEGER`: Number of master nodes, if None, use default  [default: 3]
* `--master-flavor-id TEXT`: Master node flavor ID, if None, use default  [default: b003e1cf-fd40-4ad1-827c-cc20c2ddd519]
* `--from-json FROM_JSON`: Cluster payload in JSON format, if None, use provided options
* `--dry-run / --no-dry-run`: If True, do not perform any actions, just print the payload  [default: no-dry-run]
* `--help`: Show this message and exit.

### `cluster update`

Update the cluster with given id

**Usage**:

```console
$ cluster update [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--from-json FROM_JSON`: Cluster payload in JSON format, if None, use provided options
* `--dry-run / --no-dry-run`: If True, do not perform any actions, just print the payload  [default: no-dry-run]
* `--help`: Show this message and exit.

### `cluster delete`

Delete the cluster with given id

**Usage**:

```console
$ cluster delete [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--dry-run / --no-dry-run`: If True, do not perform any actions, just print the payload  [default: no-dry-run]
* `--help`: Show this message and exit.

### `cluster list`

List all clusters

**Usage**:

```console
$ cluster list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `cluster show`

Show cluster details

**Usage**:

```console
$ cluster show [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--help`: Show this message and exit.

### `cluster get-kubeconfig`

Download kube-config.yaml

**Usage**:

```console
$ cluster get-kubeconfig [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--output TEXT`: Output file for kube-config, default is &#x27;kube-config.yaml&#x27;  [default: kube-config.yaml]
* `--dry-run / --no-dry-run`: If True, do not perform any actions, just print the payload  [default: no-dry-run]
* `--help`: Show this message and exit.

## `node-pool`

Nodepool operations

**Usage**:

```console
$ node-pool [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new node pool
* `list`: List all node pools in the cluster
* `update`
* `delete`: Delete a node pool

### `node-pool create`

Create a new node pool

**Usage**:

```console
$ node-pool create [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--name TEXT`: Node pool name, if None, generate with petname
* `--node-count INTEGER`: Number of nodes in the pool  [default: 1]
* `--min-nodes INTEGER`: Minimum number of nodes in the pool  [default: 1]
* `--max-nodes INTEGER`: Maximum number of nodes in the pool  [default: 10]
* `--autoscale / --no-autoscale`: Enable autoscaling for the node pool  [default: no-autoscale]
* `--flavor-id TEXT`: Machine flavor ID for the node pool, if None, use default flavor  [default: b003e1cf-fd40-4ad1-827c-cc20c2ddd519]
* `--help`: Show this message and exit.

### `node-pool list`

List all node pools in the cluster

**Usage**:

```console
$ node-pool list [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--help`: Show this message and exit.

### `node-pool update`

**Usage**:

```console
$ node-pool update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `node-pool delete`

Delete a node pool

**Usage**:

```console
$ node-pool delete [OPTIONS] CLUSTER_ID NODE_POOL_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]
* `NODE_POOL_ID`: Node pool ID to delete  [required]

**Options**:

* `--help`: Show this message and exit.
