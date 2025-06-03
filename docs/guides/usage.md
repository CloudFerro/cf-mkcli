# mkcli Usage Guide
Have a look and commandline help:
```commandline
python -m mkcli --help
```


# Simple usage examples just for starting up
Here you can find a several examples of how to use the mkcli tool.
These examples cover common tasks and operations that can be performed with mkcli, providing a quick reference for users to get started.
In the examples directory you can find some ready-to-use json payloads for mkcli commands.

### Refresh token
```commandline
python -m mkcli auth token refresh
```

### Create cluster

```commandline
python -m mkcli cluster create "$(cat examples/create_cluster_payload.json)"
```

```commandline
python -m mkcli cluster create --from-json "$(cat examples/create_cluster_simple_payload.json)" --dry-run
```

```commandline
 python -m mkcli cluster create --from-json $(cat examples/create_cluster_simple_payload.json) --dry-run
```

```commandline
python -m mkcli cluster create --name named-cluster --dry-run
```

```commandline
python -m mkcli cluster get-kubeconfig {cluster_io}
```

### List clusters briefly

```commandline
python -m mkcli cluster list | jq '.items[] | {id, name, status}'
```
