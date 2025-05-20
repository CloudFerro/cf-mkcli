# CLI

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

* `clear-token`
* `refresh-token`
* `show-token`
* `current`

### `auth clear-token`

**Usage**:

```console
$ auth clear-token [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth refresh-token`

**Usage**:

```console
$ auth refresh-token [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth show-token`

**Usage**:

```console
$ auth show-token [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth current`

**Usage**:

```console
$ auth current [OPTIONS]
```

**Options**:

* `-o, --output-format [table|json]`: [default: table]
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
* `update`
* `delete`: Delete the cluster.
* `list`: List all clusters
* `show`: Show cluster details

### `cluster create`

Create a new k8s cluster

**Usage**:

```console
$ cluster create [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `cluster update`

**Usage**:

```console
$ cluster update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `cluster delete`

Delete the cluster.

If --force is not used, will ask for confirmation.

**Usage**:

```console
$ cluster delete [OPTIONS]
```

**Options**:

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
$ cluster show [OPTIONS]
```

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

