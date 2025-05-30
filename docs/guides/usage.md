# Cluster Management with mkcli
## Create cluster

```shell
python -m mkcli cluster create "$(cat examples/create_cluster_payload.json)"
```

```markdown
python -m mkcli cluster create --from-json "$(cat examples/create_cluster_simple_payload.json)" --dry-run
```

```shell
 python -m mkcli cluster create --from-json $(cat examples/create_cluster_simple_payload.json) --dry-run
```

```shell
python -m mkcli cluster create --name named-cluster --dry-run
```

```shell
python -m mkcli cluster get-kubeconfig {cluster_io}
```

### List clusters briefly

```shell
python -m mkcli cluster list | jq '.items[] | {id, name, status}'
```
