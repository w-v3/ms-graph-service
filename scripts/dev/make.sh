#!/bin/bash

echo "Formatting code with Ruff..."
ruff format .

echo "Linting with Ruff..."
ruff check .

echo "Sorting imports with Ruff..."
ruff check . --select I --fix

echo "Type checking with mypy..."
mypy .

echo "Running tests with coverage..."
pytest --cov=app --cov-report=term --cov-report=html

echo "HTML coverage report saved to ./htmlcov/index.html"

echo "✅ All checks complete!"
