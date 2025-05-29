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
    {{ poetry }} install --with dev
    python -m typer mkcli/main.py utils docs --output docs/reference/cli.md
    {{ poetry_run }} mkdocs serve
