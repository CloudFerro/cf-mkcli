default: install lint test

install:
    uv lock --upgrade
    uv sync --all-extras --frozen
    @just hook

lint:
    uvx ruff format
    uvx ruff check --fix
    uvx mypy .

test *args:
    uv run --no-sync pytest {{ args }}

publish:
    rm -rf dist
    uv build
    uv publish --token $PYPI_TOKEN

hook:
    uvx pre-commit install --install-hooks --overwrite

unhook:
    uvx pre-commit uninstall

docs:
    uv pip install -r docs/requirements.txt
    python -m typer mkcli/main.py utils docs --output docs/typer-autodoc.md
    uv run mkdocs serve
