#!/bin/bash
# Detener la ejecución ante cualquier error
set -e

echo "Running test..."
uv run pytest

echo "Checking code style with Ruff..."
uv run ruff check .

echo "Verifying formatting..."
uv run ruff format --check .


echo "Applying formatting changes..."
uv run ruff format .
