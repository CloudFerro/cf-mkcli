# Usage Guide
Remember, that you can always have a look at commandline help:
```commandline
mkcli --help
```

## Authorization
To start using `mkcli`, you need to setup your connection to Managed Kubernetes. The simplest way of doint it is by command:
```commandline
mkcli auth init
```
The app will ask you for all needed information like region and realm on which you want to opeate. You will be asked for providing Managed Kubernetes API key for authorization. You can get one, after logging into your account at ClodFerro's Managed Kubernetes website.

![Usage example](./docs/demo/auth_init.gif)

#### Logging out
If you want to log out, anc clear all saved auth session data, you can just run:
```commandline
mkcli auth end
```
and it will purge all saved credentials and tokens, so you will need to run `mkcli auth init` again to log in.


## Simple usage examples just for starting up
Here you can find a several examples of how to use the mkcli tool.

#### List all clusters
You can list all your clusters by running:
```commandline
mkcli cluster list
```
To increase readability you can easily filter the output by using `jq` command. For example, to list only cluster IDs, names and statuses, you can run:
```commandline
mkcli cluster list --format json | jq '.items[] | {id, name, status}'```
```

#### List all available flavors
```commandline
mkcli flavor list
```
You should see a list of all available flavors in your region.
By default, you should see an output formatted as table. If you want to see it in JSON format,
you can use the `--format` option:
```commandline
mkcli flavors list --format json
```

#### Create a new cluster
```
mkcli cluster create --master-count 1
```

### *Advanced: Auth contexts (you can skip this part of docs if you are not interested in advanced usage)*
_*Optionally_: If you want to use `mkcli` simultaneously for different accounts, regions or realms
you can use "session contexts" feature.
This allows you to create multiple contexts, each with its own credentials and settings.
```commandline
mkcli auth context add {context-name}
```
This command will prompt you to add all needed information, for creating a new context (e.g., realm, region, client secret, etc.).
You can always list, edit, duplicate or delete contexts (see help for `mkcli auth context` command).

To switch between contexts, you can use:
```commandline
mkcli auth context switch {context-name}
```
If you want, you can also list, edit, duplicate or delete contexts (see help for `mkcli auth context` command).

![Contexts preview](docs/demo/context.gif)
