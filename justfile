default:
    just --list

# Install all dependencies
install:
    uv sync

# Run tests with coverage
test:
    uv run pytest --cov=asana_cli --cov-report=term-missing

# Run tests without coverage (faster)
test-quick:
    uv run pytest

# Run linter
lint:
    uv run ruff check src tests

# Run linter with auto-fix
lint-fix:
    uv run ruff check --fix src tests

# Run type checker
typecheck:
    uv run mypy src

# Format code
format:
    uv run ruff format src tests

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Build package
build:
    uv build

# Publish to PyPI
publish:
    uv publish --token $PYPI_KOENVANDERVEEN_TOKEN

# Release: run checks, build, and publish to PyPI
release version: check
    #!/usr/bin/env bash
    set -euo pipefail

    # Update version in pyproject.toml
    sed -i '' 's/^version = ".*"/version = "{{version}}"/' pyproject.toml

    # Update version in __init__.py
    sed -i '' 's/__version__ = ".*"/__version__ = "{{version}}"/' src/asana_cli/__init__.py

    # Commit version bump
    git add pyproject.toml src/asana_cli/__init__.py
    git commit -m "Release v{{version}}"
    git tag -a "v{{version}}" -m "Release v{{version}}"

    # Build and publish
    uv build
    uv publish --token $PYPI_KOENVANDERVEEN_TOKEN

    # Push to GitHub
    git push origin main
    git push origin "v{{version}}"

    echo "Released v{{version}}"

# Clean build artifacts
clean:
    rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Run the CLI (with arguments)
run *args:
    uv run asana {{args}}
