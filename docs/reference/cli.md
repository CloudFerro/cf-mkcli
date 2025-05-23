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

* `auth`: Cli auth context
* `cluster`: Cli auth context
* `node-pool`: Nodepool operations

## `auth`

Cli auth context

**Usage**:

```console
$ auth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `show`: Show current auth context
* `token`: Token management

### `auth show`

Show current auth context

**Usage**:

```console
$ auth show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth token`

Token management

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

## `cluster`

Cli auth context

**Usage**:

```console
$ cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new k8s cluster
* `update`: Update the cluster with given id
* `delete`: Delete the cluster.
* `list`: List all clusters
* `show`: Show cluster details
* `kube-config`: Download kube-config.yaml

### `cluster create`

Create a new k8s cluster

**Usage**:

```console
$ cluster create [OPTIONS] CLUSTER_PAYLOAD
```

**Arguments**:

* `CLUSTER_PAYLOAD`: [required]

**Options**:

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

* `--payload FROM_JSON`
* `--help`: Show this message and exit.

### `cluster delete`

Delete the cluster.

If --force is not used, will ask for confirmation.  # TODO: implement force

**Usage**:

```console
$ cluster delete [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--force TEXT`: Cluster ID  [default: False]
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

### `cluster kube-config`

Download kube-config.yaml

**Usage**:

```console
$ cluster kube-config [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

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

* `create`
* `update`
* `delete`
* `list`
* `show`

### `node-pool create`

**Usage**:

```console
$ node-pool create [OPTIONS]
```

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

**Usage**:

```console
$ node-pool delete [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `node-pool list`

**Usage**:

```console
$ node-pool list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `node-pool show`

**Usage**:

```console
$ node-pool show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
