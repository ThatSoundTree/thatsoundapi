#!/usr/bin/env bash
set -euo pipefail

echo "Linting with Ruff..."
poetry run ruff check . --fix

echo "Type-checking with mypy..."
poetry run mypy .
