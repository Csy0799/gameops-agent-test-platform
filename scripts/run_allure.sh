#!/usr/bin/env bash
set -euo pipefail

python -m pytest --alluredir=reports/allure-results
echo "Allure results generated at reports/allure-results"
echo "If Allure CLI is installed, run: allure serve reports/allure-results"
