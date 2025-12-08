# mkcli reference documentation

mkcli - A CLI for managing your Kubernetes clusters

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--verbose`
* `--version`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `auth`: mkcli authorization and authentication...
* `cluster`: Manage Kubernetes clusters
* `node-pool`: Manage Kubernetes cluster&#x27;s node pools
* `kubernetes-version`: Manage Kubernetes versions
* `flavors`: Manage Kubernetes machine specs (flavors)
* `regions`: Manage regions

## `auth`

mkcli authorization and authentication management

**Usage**:

```console
$ auth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `init`: Initialize authentication session
* `end`: End authentication session and clear saved...
* `token`: Auth OpenID token management
* `key`: MK8s API key management
* `context`: Manage authentication contexts

### `auth init`

Initialize authentication session

**Usage**:

```console
$ auth init [OPTIONS]
```

**Options**:

* `--realm TEXT`: Realm name  [required]
* `--region TEXT`: Region name  [required]
* `--auth-type [api_key|openid]`: Auth type  [default: api_key]
* `--help`: Show this message and exit.

### `auth end`

End authentication session and clear saved tokens

**Usage**:

```console
$ auth end [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth token`

Auth OpenID token management

**Usage**:

```console
$ auth token [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clear`: Clear the current access token from the...
* `refresh`: Refresh the current access token from the...
* `show`: Show the current access token from the...

#### `auth token clear`

Clear the current access token from the authorization session (current context)

**Usage**:

```console
$ auth token clear [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth token refresh`

Refresh the current access token from the authorization session (current context)

**Usage**:

```console
$ auth token refresh [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth token show`

Show the current access token from the authorization session (current context)

**Usage**:

```console
$ auth token show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `auth key`

MK8s API key management

**Usage**:

```console
$ auth key [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clear`: Clear the current API key from the session...
* `show`: Show the current API key from the session...
* `set`: Set the current API key for the session...

#### `auth key clear`

Clear the current API key from the session (current context)

**Usage**:

```console
$ auth key clear [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth key show`

Show the current API key from the session (current context)

**Usage**:

```console
$ auth key show [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `auth key set`

Set the current API key for the session (current context)

**Usage**:

```console
$ auth key set [OPTIONS] API_KEY
```

**Arguments**:

* `API_KEY`: API key to set for the current context  [required]

**Options**:

* `--help`: Show this message and exit.


### `auth context`

Manage authentication contexts

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
* `delete`: emove given auth context from the catalogue
* `duplicate`: Duplicate given auth context with a new name
* `edit`: Update given auth context
* `switch`: Switch to a different auth context

#### `auth context show`

Show current auth context

**Usage**:

```console
$ auth context show [OPTIONS]
```

**Options**:

* `-f, --format [table|json]`: [default: table]
* `--help`: Show this message and exit.

#### `auth context list`

Remove given auth context from the catalogue

**Usage**:

```console
$ auth context list [OPTIONS]
```

**Options**:

* `-f, --format [table|json]`: [default: table]
* `--help`: Show this message and exit.

#### `auth context add`

Prompt for new auth context and add it to the catalogue

**Usage**:

```console
$ auth context add [OPTIONS]
```

**Options**:

* `--name TEXT`: Name for the new auth context  [required]
* `--realm TEXT`: Realm for the new auth context  [required]
* `--region TEXT`: Region for the new auth context  [required]
* `--identity-server TEXT`: Identity server URL for the new auth context  [default: https://identity.cloudferro.com/auth/]
* `--auth-type [api_key|openid]`: Authentication type for the new auth context  [default: openid]
* `--help`: Show this message and exit.

#### `auth context delete`

emove given auth context from the catalogue

**Usage**:

```console
$ auth context delete [OPTIONS] NAMES...
```

**Arguments**:

* `NAMES...`: Names of the auth context to delete  [required]

**Options**:

* `-y, --confirm`
* `--help`: Show this message and exit.

#### `auth context duplicate`

Duplicate given auth context with a new name

**Usage**:

```console
$ auth context duplicate [OPTIONS] CTX
```

**Arguments**:

* `CTX`: Name of the auth context to duplicate  [required]

**Options**:

* `-n, --name TEXT`: Name for the new auth context  [required]
* `--help`: Show this message and exit.

#### `auth context edit`

Update given auth context

**Usage**:

```console
$ auth context edit [OPTIONS] CTX
```

**Arguments**:

* `CTX`: Name of the auth context to update  [required]

**Options**:

* `-n, --name TEXT`: New name of the edited auth context
* `--client_id TEXT`: New Client ID for the edited auth context
* `--realm TEXT`: Realm for the edited auth context
* `--scope TEXT`: Scope for the edited auth context
* `--region TEXT`: Region for the edited auth context
* `--identity_server TEXT`: Identity server URL for the edited auth context
* `--auth_type [api_key|openid]`: Auth type for the edited auth context
* `--help`: Show this message and exit.

#### `auth context switch`

Switch to a different auth context

**Usage**:

```console
$ auth context switch [OPTIONS] CTX
```

**Arguments**:

* `CTX`: Name of the auth context to set as current  [required]

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
* `get-kubeconfig`: Download kube-config.yaml for the cluster

### `cluster create`

Create a new k8s cluster

**Usage**:

```console
$ cluster create [OPTIONS]
```

**Options**:

* `--name TEXT`: Cluster name, if None, generate with petname
* `--kubernetes-version TEXT`: Kubernetes version, if None, use default  [default: 1.30.10]
* `--master-count INTEGER`: Number of master nodes, if None, use default  [default: 3]
* `--master-flavor TEXT`: Master node flavor name, if None, use default  [default: hma.medium]
* `--from-json FROM_JSON`: Cluster payload in JSON format, if None, use provided options
* `--dry-run`: If True, do not perform any actions, just print the payload
* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
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

* `--kubernetes-version TEXT`: Kubernetes version, if None, use default
* `--master-count INTEGER`: Number of master nodes, if None, use default
* `--master-flavor TEXT`: Master node flavor name, if None, use default
* `--dry-run`: If True, do not perform any actions, just print the payload
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

* `-y, --confirm`
* `--dry-run`: If True, do not perform any actions, just print the payload
* `--help`: Show this message and exit.

### `cluster list`

List all clusters

**Usage**:

```console
$ cluster list [OPTIONS]
```

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
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

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

### `cluster get-kubeconfig`

Download kube-config.yaml for the cluster

**Usage**:

```console
$ cluster get-kubeconfig [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]

**Options**:

* `--output TEXT`: Output file for kube-config, default is &#x27;kube-config.yaml&#x27;  [default: kube-config.yaml]
* `--dry-run`: If True, do not perform any actions, just print the payload
* `--help`: Show this message and exit.

## `node-pool`

Manage Kubernetes cluster&#x27;s node pools

**Usage**:

```console
$ node-pool [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new node pool
* `list`: List all node pools in the cluster
* `update`: Update the node pool with given id
* `show`
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

* `--flavor TEXT`: Machine flavor for the node pool, if None, use the default flavor  [required]
* `--name TEXT`: Node pool name, if None, generate with petname  [required]
* `--node-count INTEGER`: Number of nodes in the pool  [default: 0]
* `--min-nodes INTEGER`: Minimum number of nodes in the pool  [default: 0]
* `--max-nodes INTEGER`: Maximum number of nodes in the pool  [default: 0]
* `--shared-networks TEXT`: List of shared networks for the node pool
* `--autoscale / --no-autoscale`: Enable autoscaling for the node pool  [default: no-autoscale]
* `--labels _PARSE_LABELS`: List of labels in the format &#x27;key=value&#x27;, e.g. &#x27;env=prod&#x27;
* `--taints _PARSE_TAINTS`: List of taints in the format &#x27;key=value:effect&#x27;, e.g. &#x27;key=value:NoSchedule&#x27;
* `--from-json FROM_JSON`: Node-pool payload in JSON format, if None, use provided options
* `--dry-run`: If True, do not perform any actions, just print the payload
* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

### `node-pool list`

List all node pools in the cluster

**Usage**:

```console
$ node-pool list [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID to operate on  [required]

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

### `node-pool update`

Update the node pool with given id

**Usage**:

```console
$ node-pool update [OPTIONS] CLUSTER_ID NODE_POOL_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID  [required]
* `NODE_POOL_ID`: Node Pool ID to update  [required]

**Options**:

* `--node-count INTEGER`: Number of nodes in the pool
* `--min-nodes INTEGER`: Minimum number of nodes in the pool
* `--max-nodes INTEGER`: Maximum number of nodes in the pool
* `--shared-networks TEXT`: List of shared networks for the node pool
* `--autoscale / --no-autoscale`: Enable autoscaling for the node pool
* `--help`: Show this message and exit.

### `node-pool show`

**Usage**:

```console
$ node-pool show [OPTIONS] CLUSTER_ID NODE_POOL_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID to operate on  [required]
* `NODE_POOL_ID`: Node pool ID to operate on  [required]

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

### `node-pool delete`

Delete a node pool

**Usage**:

```console
$ node-pool delete [OPTIONS] CLUSTER_ID NODE_POOL_ID
```

**Arguments**:

* `CLUSTER_ID`: Cluster ID to operate on  [required]
* `NODE_POOL_ID`: Node pool ID to operate on  [required]

**Options**:

* `-y, --confirm`
* `--dry-run`: If True, do not perform any actions, just print the payload
* `--help`: Show this message and exit.

## `kubernetes-version`

Manage Kubernetes versions

**Usage**:

```console
$ kubernetes-version [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all Kubernetes versions

### `kubernetes-version list`

List all Kubernetes versions

**Usage**:

```console
$ kubernetes-version list [OPTIONS]
```

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

## `flavors`

Manage Kubernetes machine specs (flavors)

**Usage**:

```console
$ flavors [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all available flavors

### `flavors list`

List all available flavors

**Usage**:

```console
$ flavors list [OPTIONS]
```

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.

## `regions`

Manage regions

**Usage**:

```console
$ regions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all available regions

### `regions list`

List all available regions

**Usage**:

```console
$ regions list [OPTIONS]
```

**Options**:

* `--format [table|json]`: Output format, either &#x27;table&#x27; or &#x27;json&#x27;  [default: table]
* `--help`: Show this message and exit.
