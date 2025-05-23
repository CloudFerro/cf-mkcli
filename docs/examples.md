

### Create cluster

```zsh
python -m mkcli cluster create "$(cat examples/create_cluster_payload.json)"
```

### List clusters briefly

```zsh
python -m mkcli cluster list | jq '.items[] | {id, name, status}'
```
