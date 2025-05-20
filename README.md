# Project Overview

This project provides a CLI tool for managing Kubernetes clusters, built with Python and Typer. Below are the actions defined in the `Justfile` to help with development, testing, and deployment.

## Prerequisites

- Python installed
- `pip` for managing Python packages
- `just` command-line tool installed

## Available Actions

### Default Action
The default action runs the following tasks in sequence:
- `install`
- `lint`
- `test`

Run it with:
```bash
just
