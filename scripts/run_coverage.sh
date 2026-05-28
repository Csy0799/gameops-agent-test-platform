#!/usr/bin/env bash
set -euo pipefail

python -m pytest --cov=app --cov-report=term-missing --cov-report=html
echo "Coverage HTML report generated at htmlcov/index.html"
