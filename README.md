# Project Overview

This project provides a CLI tool for managing Kubernetes clusters, built with Python and Typer. Below are the actions defined in the `Justfile` to help with development, testing, and deployment.

## Prerequisites

- Python installed
- `pip` for managing Python packages
- `just` command-line tool installed

## Available Actions

The `Justfile` defines several actions to streamline development, testing, and deployment. Below is a description of each action:

### Default Action
The default action runs the following tasks in sequence:
- `install`
- `lint`
- `test`

Run it with:
```bash
just
```

### Actions

#### `install`
Installs and synchronizes project dependencies:
- Updates the dependency lock file.
- Installs all dependencies with extras in a frozen state.
- Installs pre-commit hooks.

Run it with:
```bash
just install
```

#### `lint`
Formats and lints the codebase:
- Formats the code using `ruff`.
- Checks for linting issues and fixes them automatically.
- Runs type checking with `mypy`.

Run it with:
```bash
just lint
```

#### `test`
Runs the test suite using `pytest`. You can pass additional arguments to `pytest` if needed.

Run it with:
```bash
just test
```
Example with additional arguments:
```bash
just test -- -k "test_example"
```

#### `publish`
Builds and publishes the project to PyPI:
- Cleans the `dist` directory.
- Builds the project.
- Publishes the package using the provided PyPI token.

Run it with:
```bash
just publish
```

#### `hook`
Installs or updates pre-commit hooks.

Run it with:
```bash
just hook
```

#### `unhook`
Uninstalls pre-commit hooks.

Run it with:
```bash
just unhook
```

#### `docs`
Generates and serves the project documentation:
- Installs documentation dependencies.
- Generates CLI documentation using `typer`.
- Serves the documentation locally using `mkdocs`.

Run it with:
```bash
just docs
```

# mkcli docs for users

[See user's documentation](docs/typer-autodoc.md)
