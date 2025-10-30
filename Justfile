poetry := "poetry"
poetry_run := poetry + " run"

default:
    just --list --unsorted

setup:
    {{ poetry }} check
    {{ poetry }} install

lint:
    {{ poetry_run }} ruff format
    {{ poetry_run }} ruff check --fix
    {{ poetry_run }} run mypy .

test *args:
    {{ poetry_run }} pytest {{ args }}

build:
    rm -rf dist
    {{ poetry_run }} build

hook:
    {{ poetry_run }} pre-commit install --install-hooks --overwrite

unhook:
    {{ poetry_run }} pre-commit uninstall

docs:
    python -m typer mkcli/main.py utils docs --title "mkcli reference documentation" --output docs/reference/cli.md  # Update CLI documentation
    cat docs/intro.md > README.md  # add intro
    echo '' >> README.md  # add a newline
    cat docs/guides/installation.md >> README.md  # add installation
    echo '' >> README.md  # add a newline
    cat docs/guides/usage.md >> README.md
    echo '' >> README.md  # add a newline
    cat docs/reference/cli.md >> README.md  # add CLI reference
    echo '' >> README.md  # add a newline

docs-run-server:
    {{ poetry_run }} mkdocs build
    {{ poetry_run }} mkdocs serve

bump-version *args:
    {{ poetry }} version {{ args }}
    echo "__version__ = '$(cat pyproject.toml | grep version | cut -d ' ' -f 3 | tr -d '\"')'" > mkcli/_version.py

load-env-local:
    export VAULT_ADDR="https://vault.intra.cloudferro.com"
    export VAULT_SKIP_VERIFY=true
    vault login -method=oidc -path=azure
    export API_TOKEN_PROD="$(vault kv get -tls-skip-verify -field=API_TOKEN_PROD secrets/mk8s/test)"
