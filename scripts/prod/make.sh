#!/bin/bash

set -e  # Exit immediately on error

COVERAGE_THRESHOLD=90

echo "Formatting code with Ruff..."
ruff format .

echo "Linting with Ruff..."
ruff check .

echo "Sorting imports with Ruff..."
ruff check . --select I --fix

echo "Type checking with mypy..."
mypy .

echo "Running tests with coverage..."
pytest --cov=app --cov-fail-under=$COVERAGE_THRESHOLD --cov-report=term --cov-report=html

echo "Tests passed with coverage >= $COVERAGE_THRESHOLD%!"
echo "HTML coverage report saved to ./htmlcov/index.html"
