@echo off
setlocal

set COVERAGE_THRESHOLD=90

echo Formatting code with Ruff...
ruff format . || exit /b

echo Linting with Ruff...
ruff check . || exit /b

echo Sorting imports with Ruff...
ruff check . --select I --fix || exit /b

echo Type checking with mypy...
mypy . || exit /b

echo Running tests with coverage...
pytest --cov=app --cov-fail-under=%COVERAGE_THRESHOLD% --cov-report=term --cov-report=html || exit /b

echo Tests passed with coverage >= %COVERAGE_THRESHOLD%%!
echo HTML coverage report available at htmlcov\index.html
