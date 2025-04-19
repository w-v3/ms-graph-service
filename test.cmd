echo Running tests with coverage...
pytest --cov=app --cov-report=term --cov-report=html

echo HTML coverage report saved to htmlcov\index.html

echo ✅ All checks complete!