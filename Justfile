default: install lint test

install:
    uv lock --upgrade
    uv sync --all-extras --frozen
    @just hook

lint:
    uv run ruff format
    uv run ruff check --fix
    uv run mypy .

test *args:
    uv run --no-sync pytest {{ args }}

publish:
    rm -rf dist
    uv build
    uv publish --token $PYPI_TOKEN

hook:
    uv run pre-commit install --install-hooks --overwrite

unhook:
    uv run pre-commit uninstall

docs:
    uv pip install -r docs/requirements.txt
    python -m typer mkcli/main.py utils docs --output docs/typer-autodoc.md
    uv run mkdocs serve
