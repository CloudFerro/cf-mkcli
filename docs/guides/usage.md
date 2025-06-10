# Usage Guide
Remember, that you can always have a look at commandline help:
```commandline
mkcli --help
```

## Authorization
To start using `mkcli`, you need to authorize it with your credentials. In the simplest way this can be done by running the following command:
```commandline
mkcli auth init
```
`mkcli` will prompt you to enter `realm` and `region` names, which are required to connect to your account.
and then you can check if you are logged in by running:,
```commandline
mkcli auth token show
```
How does it work? `mkcli` will open web browser window and ask you to log in to your account.
After successful logging in, `mkcli` will "remember" your credentials and you can use it without logging in again
for certain amount of time.

If you want to log out, anc clear all saved auth session data, you can run:
```commandline
mkcli auth end
```
and it will purge all saved credentials and tokens, so you will need to run `mkcli auth init` again to log in.

![Auth init preview](docs/demo/auth_init.gif)

### *Advanced: Auth contexts (you can skip this part of docs if you are not interested in advanced usage)*
_*Optionally_: If you want to use `mkcli` simultaneously for different accounts, or in different realms,
you can use "login session contexts" feature.
This allows you to create multiple contexts, each with its own credentials and settings.
```commandline
mkcli auth context add {context-name}
```
This command will prompt you to add all needed information, for creating a new context (e.g., realm, client ID, client secret, etc.).
But don't worry if you are not familiar with all of them, since mkcli provides default values for most of the fields.
You can always list, edit, duplicate or delete contexts (see help for `mkcli auth context` command).

To switch between contexts, you can use:
```commandline
mkcli auth context switch {context-name}
```
If you want, you can also list, edit, duplicate or delete contexts (see help for `mkcli auth context` command).

![Contexts preview](docs/demo/context.gif)

### Simple usage examples just for starting up
Here you can find a several examples of how to use the mkcli tool.

### List all clusters
You can list all your clusters by running:
```commandline
mkcli cluster list
```
To increase readability you can easily filter the output by using `jq` command. For example, to list only cluster IDs, names and statuses, you can run:
```commandline
mkcli cluster list --format json | jq '.items[] | {id, name, status}'```
```
### List all available flavors
```commandline
mkcli flavor list
```
You should see a list of all available flavors in your region.
By default, you should see an output formatted as table. If you want to see it in JSON format,
you can use the `--format` option:
```commandline
mkcli flavors list --format json
```

### Create a new cluster
