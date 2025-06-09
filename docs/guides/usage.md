# Usage Guide
Have a look and commandline help:
```commandline
mkcli --help
```

### Authorization
To start using `mkcli`, you need to authorize it with your credentials. This is done by running the following command:
```commandline
mkcli auth init
```
and then,
```commandline
mkcli auth token refresh
```
First command creates so-called "login context" which remembers your credentials,
and the second command retrieves an access token that is used for subsequent API calls. It will open web browser window
and ask you to log in to your account. After successful logging in, `mkcli` will "remember" your credentials and you
can use it without logging in again for certain amount of time.

_*Optionally_: If you want to use `mkcli` with different credentials or in different realm, you can run the following command to
create a new login context:
```commandline
mkcli auth context add {context-name}
```
This command will prompt you to add all needed information, for creating a new context (e.g., realm, client ID, client secret, etc.).
But don't worry if you are not familiar with all of them, since mkcli provides default values for most of the fields.

To switch between contexts, you can use:
```commandline
mkcli auth context switch {context-name}
```
If you want, you can also list, edit, duplicate or delete contexts (see help for `mkcli auth context` command).

![Contexts preview](docs/demo/context.gif)

# Simple usage examples just for starting up
Here you can find a several examples of how to use the mkcli tool.
These examples cover common tasks and operations that can be performed with mkcli, providing a quick reference for users to get started.
In the examples directory you can find some ready-to-use json payloads for mkcli commands.

### Managing tokens
You can refresh your access token at any time by running the following command:
```commandline
mkcli auth token refresh
```
You can also have a look on it (including all important information like expiration time) by:
```commandline
mkcli auth token show
```
Have a look on all available commands for `mkcli auth token --help`:

## Create cluster
