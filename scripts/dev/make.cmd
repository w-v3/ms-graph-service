@echo off
echo Running Ruff (format)...
ruff format .

echo Running Ruff (lint + fix)...
ruff check . --fix

echo Sorting imports with Ruff...
ruff check . --select I --fix

echo Running Mypy (type checks)...
mypy .

echo Running tests with coverage...
pytest --cov=app --cov-report=term --cov-report=html

echo HTML coverage report saved to htmlcov\index.html

echo ✅ All checks complete!